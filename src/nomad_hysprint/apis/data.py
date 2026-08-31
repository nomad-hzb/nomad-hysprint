"""Build the JV dataframe from a set of selected batches."""

import numpy as np
import pandas as pd

from .api_calls import get_all_jv, get_ids_in_batch, get_sample_description
from .config import BATCH_TYPE, J_MAX, JV_TYPE


def filter_batch_list(batch_ids):
    """Drop batches whose '_'-prefixed parent is also in the list.

    Mirrors the original notebook filter so we don't show both a parent batch
    and its child batches.
    """
    batch_set = set(batch_ids)
    out = []
    for b in batch_ids:
        parent = '_'.join(b.split('_')[:-1])
        if parent and parent in batch_set:
            continue
        out.append(b)
    return out


def load_jv_dataframe(url, token, batch_ids):
    """Load all JV data from the given batches into a tidy DataFrame.

    Columns:
        lab_id, condition, direction, cell, PCE(%), Voc(V), Jsc(mA/cm2),
        FF(%), N_Rs, N_Rsh, Voltage(V), Current(mA/cm2)
    """
    sample_ids = get_ids_in_batch(url, token, batch_ids, batch_type=BATCH_TYPE)
    if not sample_ids:
        return pd.DataFrame()

    description = get_sample_description(url, token, sample_ids)
    jv_by_sample = get_all_jv(url, token, sample_ids, jv_type=JV_TYPE)

    rows = []
    for lab_id, entries in jv_by_sample.items():
        condition = description.get(lab_id, '(no description)')
        for entry in entries:
            for curve in entry.get('jv_curve', []) or []:
                cell_name = curve.get('cell_name', '') or ''
                if '_for' in cell_name:
                    direction = 'Forward'
                elif '_rev' in cell_name:
                    direction = 'Reverse'
                else:
                    continue

                V = np.asarray(curve.get('voltage', []), dtype=float)
                J = np.asarray(curve.get('current_density', []), dtype=float)
                if V.size and J.size:
                    mask = J <= J_MAX
                    V = V[mask]
                    J = J[mask]

                rs = curve.get('series_resistance')
                rsh = curve.get('shunt_resistance')

                rows.append(
                    {
                        'lab_id': lab_id,
                        'condition': condition,
                        'direction': direction,
                        'cell': cell_name[0] if cell_name else '',
                        'PCE(%)': curve.get('efficiency'),
                        'Voc(V)': curve.get('open_circuit_voltage'),
                        'Jsc(mA/cm2)': curve.get('short_circuit_current_density'),
                        'FF(%)': curve.get('fill_factor'),
                        'N_Rs': rs * 1e3 if rs is not None else np.nan,
                        'N_Rsh': rsh * 1e3 if rsh is not None else np.nan,
                        'Voltage(V)': V,
                        'Current(mA/cm2)': J,
                    }
                )

    df = pd.DataFrame(
        rows,
        columns=[
            'lab_id',
            'condition',
            'direction',
            'cell',
            'PCE(%)',
            'Voc(V)',
            'Jsc(mA/cm2)',
            'FF(%)',
            'N_Rs',
            'N_Rsh',
            'Voltage(V)',
            'Current(mA/cm2)',
        ],
    )
    return df
