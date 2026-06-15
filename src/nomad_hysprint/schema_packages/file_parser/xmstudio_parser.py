"""Binary parser for XM-Studio electrochemistry `.hy.data` files.

Ported from Echem_helpers.py. The only change from the original is that
`import_xmstudio_binary_data` accepts raw `bytes` instead of a file path,
so it works inside NOMAD without filesystem access.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _as_list(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple, set, pd.Index, np.ndarray)):
        return list(value)
    return [value]


def _to_number(value):
    try:
        if pd.isna(value):
            return np.nan
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def _clean_metadata_series(series, index):
    if series is None:
        series = pd.Series('', index=index)
    return (
        series.fillna('')
        .astype(str)
        .str.lower()
        .str.replace(r'[^a-z0-9]+', ' ', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )


def _numeric_column(df, column, scale=1.0):
    if column not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[column], errors='coerce') * scale


def _first_existing_numeric_column(df, columns, scale=1.0):
    for column in columns:
        if column in df.columns:
            return _numeric_column(df, column, scale=scale)
    return pd.Series(np.nan, index=df.index)


# ---------------------------------------------------------------------------
# Binary reader helpers (module-level so they don't inflate statement counts)
# ---------------------------------------------------------------------------

_TIMESERIES_DTYPE = np.dtype(
    [
        ('time_ns', '<u8'),
        ('potential_V', '<f4'),
        ('current_A', '<f4'),
        ('aux_1', '<f4'),
        ('status', '<u4'),
    ]
)
_DPV_DTYPE = np.dtype([('time_ns', '<u8')] + [(f'channel_{i:02d}', '<f4') for i in range(1, 11)])
_IMPEDANCE_DTYPE = np.dtype(
    [('time_ns', '<u8')]
    + [(f'channel_{i:02d}', '<f4') for i in range(10)]
    + [('frequency_Hz_raw', '<f8')]
    + [(f'channel_{i:02d}', '<f4') for i in range(12, 35)]
)


def _find_u16_marker(blob: bytes, text: str) -> list:
    marker = text.encode('utf-16le') + b'\x00\x00'
    positions = []
    start = 0
    while True:
        pos = blob.find(marker, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def _extract_u16_strings(chunk: bytes) -> list:
    decoded = chunk.decode('utf-16le', errors='ignore')
    strings = []
    current = []
    for char in decoded:
        if char.isprintable():
            current.append(char)
        elif current:
            strings.append(''.join(current))
            current = []
    if current:
        strings.append(''.join(current))
    return strings


def _strings_to_fields(strings: list) -> dict:
    return {key: value for key, value in zip(strings[0::2], strings[1::2])}


def _add_impedance_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['potential_V'] = df['channel_00']
    df['current_A'] = df['channel_01']
    df['frequency_Hz'] = pd.to_numeric(df['frequency_Hz_raw'], errors='coerce')
    df.loc[~np.isfinite(df['frequency_Hz']) | (df['frequency_Hz'] <= 0), 'frequency_Hz'] = np.nan
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        df['log_omega'] = np.log(2 * np.pi * df['frequency_Hz'])
        current_complex = df['channel_15'].to_numpy() + 1j * df['channel_16'].to_numpy()
        voltage_complex = df['channel_17'].to_numpy() + 1j * df['channel_18'].to_numpy()
        impedance = voltage_complex / current_complex
    df['ac_amplitude_V'] = df['channel_12']
    df['dc_potential_V'] = df['channel_13']
    df['current_real_A'] = df['channel_15']
    df['current_imag_A'] = df['channel_16']
    df['voltage_real_V'] = df['channel_17']
    df['voltage_imag_V'] = df['channel_18']
    df['Z_real_ohm'] = np.real(impedance)
    df['Z_imag_ohm'] = np.imag(impedance)
    df['Z_abs_ohm'] = np.abs(impedance)
    df['phase_deg'] = np.angle(impedance, deg=True)
    df['valid_impedance'] = df['frequency_Hz'].notna() & np.isfinite(df['Z_real_ohm'])
    return df


def _decode_binary_record(blob: bytes, av_pos: int, start_offset: int, n_points: int,
                           record_type: str, row_size: int) -> pd.DataFrame:
    data_bytes = blob[av_pos + start_offset : av_pos + start_offset + n_points * row_size]
    if record_type == 'timeseries':
        return pd.DataFrame(np.frombuffer(data_bytes, dtype=_TIMESERIES_DTYPE, count=n_points))
    if record_type == 'dpv':
        df = pd.DataFrame(np.frombuffer(data_bytes, dtype=_DPV_DTYPE, count=n_points))
        return df.rename(columns={
            'channel_01': 'potential_V',
            'channel_02': 'current_A',
            'channel_03': 'aux_1',
            'channel_04': 'aux_2',
            'channel_05': 'pulse_current_A',
        })
    df = pd.DataFrame(np.frombuffer(data_bytes, dtype=_IMPEDANCE_DTYPE, count=n_points))
    return _add_impedance_columns(df)


def _choose_layout(blob: bytes, fields: dict, av_pos: int, next_st: int, n_points: int):
    name = fields.get('NM', '')

    def valid_footer(start_offset, row_size):
        footer_size = next_st - (av_pos + start_offset) - n_points * row_size
        return footer_size if 0 <= footer_size <= 256 else None

    def timeseries_score(start_offset):
        footer_size = valid_footer(start_offset, 24)
        if footer_size is None:
            return -1, None
        sample_count = min(n_points, 12)
        data_start = av_pos + start_offset
        sample = np.frombuffer(
            blob[data_start : data_start + sample_count * 24],
            dtype=_TIMESERIES_DTYPE,
            count=sample_count,
        )
        plausible = (
            (sample['time_ns'] >= 0)
            & (sample['time_ns'] <= 20_000_000_000)
            & np.isfinite(sample['potential_V'])
            & (np.abs(sample['potential_V']) <= 2)
            & np.isfinite(sample['current_A'])
            & (np.abs(sample['current_A']) <= 0.02)
            & np.isfinite(sample['aux_1'])
            & (np.abs(sample['aux_1']) <= 1)
        )
        return int(plausible.sum()), footer_size

    if 'Impedance' in name or 'NZ' in fields:
        footer_size = valid_footer(152, 148)
        if footer_size is not None:
            return 'impedance', 152, 148, footer_size

    if 'Differential Pulse' in name or 'Polarography' in name:
        footer_size = valid_footer(142, 48)
        if footer_size is not None:
            return 'dpv', 142, 48, footer_size

    candidates = []
    for start_offset in (140, 142):
        score, footer_size = timeseries_score(start_offset)
        if score >= 0:
            candidates.append((score, start_offset, footer_size))
    if candidates:
        score, start_offset, footer_size = max(candidates, key=lambda item: item[0])
        if score > 0:
            return 'timeseries', start_offset, 24, footer_size

    for record_type, start_offset, row_size in (('dpv', 142, 48), ('impedance', 152, 148)):
        footer_size = valid_footer(start_offset, row_size)
        if footer_size is not None:
            return record_type, start_offset, row_size, footer_size

    raise ValueError(f'Could not infer binary layout for {fields}')


# ---------------------------------------------------------------------------
# Binary reader
# ---------------------------------------------------------------------------


def import_xmstudio_binary_data(blob: bytes, strict: bool = False) -> pd.DataFrame:
    """Decode a raw XM-Studio binary `.hy.data` blob into a DataFrame.

    Parameters
    ----------
    blob:
        Raw bytes of the `.hy.data` file.
    strict:
        If True, raise on undecodable blocks; otherwise skip them.
    """
    st_positions = np.asarray(_find_u16_marker(blob, 'ST'), dtype=np.int64)
    av_positions = _find_u16_marker(blob, 'AV')
    frames = []

    for record_index, av_pos in enumerate(av_positions):
        st_insert_at = np.searchsorted(st_positions, av_pos, side='left')
        if st_insert_at == 0:
            continue
        st_pos = int(st_positions[st_insert_at - 1])
        next_st = int(st_positions[st_insert_at]) if st_insert_at < len(st_positions) else len(blob)
        fields = _strings_to_fields(_extract_u16_strings(blob[st_pos : av_pos + 6]))
        n_points = int(fields.get('NP', '0'))
        if n_points <= 0:
            continue
        try:
            record_type, start_offset, row_size, footer_size = _choose_layout(
                blob, fields, av_pos, next_st, n_points
            )
        except ValueError:
            if strict:
                raise
            continue
        df = _decode_binary_record(blob, av_pos, start_offset, n_points, record_type, row_size)
        df.insert(0, 'record_index', record_index)
        df.insert(1, 'step_number', fields.get('SN'))
        df.insert(2, 'step_name', fields.get('NM'))
        df.insert(3, 'record_type', record_type)
        df['time_s'] = df['time_ns'] / 1e9
        df['n_points_declared'] = n_points
        df['scan_rate'] = _to_number(fields.get('SR'))
        df['binary_start_offset_bytes'] = start_offset
        df['footer_size_bytes'] = footer_size
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Technique classification
# ---------------------------------------------------------------------------


def classify_xmstudio_techniques(df: pd.DataFrame) -> pd.Series:
    """Return a Series of technique labels (one per row) for a raw DataFrame."""
    index = df.index
    record_type = _clean_metadata_series(df.get('record_type'), index)
    step_text = _clean_metadata_series(df.get('step_name'), index)
    scan_rate = pd.to_numeric(
        df.get('scan_rate', pd.Series(np.nan, index=index)),
        errors='coerce',
    )

    if 'cycle_number' in df.columns:
        cycle_number = pd.to_numeric(df['cycle_number'], errors='coerce')
    elif 'step_number' in df.columns:
        step_parts = df['step_number'].astype(str).str.split('.', regex=False)
        cycle_number = pd.to_numeric(step_parts.str[2], errors='coerce')
    else:
        cycle_number = pd.Series(np.nan, index=index)

    conditions = [
        record_type.eq('impedance') | step_text.str.contains('impedance', regex=False),
        record_type.eq('dpv') | step_text.str.contains('differential pulse|polarography', regex=True),
        step_text.str.contains(r'\b(?:ocp|ocv)\b|open circuit|rest potential', regex=True),
        (
            cycle_number.notna()
            | scan_rate.notna()
            | step_text.str.contains(r'\bcv\b|cyclic voltammetry', regex=True)
        ),
        step_text.str.contains('potentiostatic|chronoamperometry', regex=True),
        record_type.eq('timeseries'),
    ]
    choices = ['Impedance', 'DPV', 'OCP', 'CV', 'Potentiostatic', 'Time series']
    return pd.Series(np.select(conditions, choices, default='Unknown'), index=index, dtype='object')


def add_experiment_step_columns(df: pd.DataFrame, force: bool = False) -> pd.DataFrame:
    """Add `experiment_step`, `cycle_number`, and `technique` columns if missing."""
    required_columns = {'experiment_step', 'cycle_number', 'technique'}
    if not force and required_columns.issubset(df.columns):
        return df.copy()

    df = df.copy()
    if force or 'experiment_step' not in df.columns or 'cycle_number' not in df.columns:
        if 'step_number' in df.columns:
            step_parts = df['step_number'].astype(str).str.split('.', regex=False)
            df['experiment_step'] = pd.to_numeric(step_parts.str[1], errors='coerce').astype('Int64')
            df['cycle_number'] = pd.to_numeric(step_parts.str[2], errors='coerce').astype('Int64')
        else:
            df['experiment_step'] = pd.Series(pd.NA, index=df.index, dtype='Int64')
            df['cycle_number'] = pd.Series(pd.NA, index=df.index, dtype='Int64')

    if force or 'technique' not in df.columns:
        df['technique'] = classify_xmstudio_techniques(df)
    return df


def _get_step_data(df, step=None, record_type=None, technique=None, scan_rate=None, cycle_number=None):
    step_df = add_experiment_step_columns(df)

    if step is not None:
        step_df = step_df[step_df['experiment_step'].isin(_as_list(step))]
    if record_type is not None:
        wanted_types = {str(item).lower() for item in _as_list(record_type)}
        step_df = step_df[step_df['record_type'].astype(str).str.lower().isin(wanted_types)]
    if technique is not None:
        wanted_techniques = {str(item).lower() for item in _as_list(technique)}
        step_df = step_df[step_df['technique'].astype(str).str.lower().isin(wanted_techniques)]
    if scan_rate is not None:
        wanted_rates = [_to_number(rate) for rate in _as_list(scan_rate)]
        rates = pd.to_numeric(step_df['scan_rate'], errors='coerce').to_numpy(dtype=float)
        mask = np.zeros(len(step_df), dtype=bool)
        for rate in wanted_rates:
            if pd.notna(rate):
                mask |= np.isclose(rates, float(rate), rtol=0, atol=1e-12)
        step_df = step_df[mask]
    if cycle_number is not None:
        step_df = step_df[step_df['cycle_number'].isin(_as_list(cycle_number))]
    return step_df.copy()


# ---------------------------------------------------------------------------
# Data extraction (columns match HySprint schema quantity names)
# ---------------------------------------------------------------------------


def extract_impedance_data(df: pd.DataFrame, step=None) -> pd.DataFrame:
    """Extract EIS data; column names match HySprint_ElectrochemicalImpedanceSpectroscopy."""
    impedance_df = _get_step_data(df, step=step, technique='Impedance')
    if 'valid_impedance' in impedance_df.columns:
        valid_mask = impedance_df['valid_impedance'].astype('boolean').fillna(False).to_numpy(dtype=bool)
        impedance_df = impedance_df[valid_mask]

    extracted = pd.DataFrame(
        {
            'time': _numeric_column(impedance_df, 'time_s'),
            'frequency': _numeric_column(impedance_df, 'frequency_Hz'),
            'z_real': _numeric_column(impedance_df, 'Z_real_ohm'),
            'z_imaginary': -_numeric_column(impedance_df, 'Z_imag_ohm'),
            'z_modulus': _numeric_column(impedance_df, 'Z_abs_ohm'),
            'z_angle': _numeric_column(impedance_df, 'phase_deg'),
        }
    )
    return extracted.dropna(how='all').reset_index(drop=True)


def extract_dpv_data(df: pd.DataFrame, step=None) -> pd.DataFrame:
    """Extract DPV data; column names match HySprint_DifferentialPulseVoltammetry."""
    dpv_df = _get_step_data(df, step=step, technique='DPV')
    i_current = _numeric_column(dpv_df, 'current_A')
    i_pulse = _first_existing_numeric_column(dpv_df, ['pulse_current_A', 'current_A'])
    extracted = pd.DataFrame(
        {
            'time': _numeric_column(dpv_df, 'time_s'),
            'voltage': -_numeric_column(dpv_df, 'potential_V'),
            'current': -(i_current - i_pulse),
        }
    )
    return extracted.dropna(how='all').reset_index(drop=True)


def extract_ocp_data(df: pd.DataFrame, step=None) -> pd.DataFrame:
    """Extract OCP data; column names match HySprint_OpenCircuitVoltage."""
    ocp_df = _get_step_data(df, step=step, technique='OCP')
    extracted = pd.DataFrame(
        {
            'time': _numeric_column(ocp_df, 'time_s'),
            'voltage': _numeric_column(ocp_df, 'potential_V'),
            'current': _numeric_column(ocp_df, 'current_A'),
        }
    )
    return extracted.dropna(how='all').reset_index(drop=True)


def _extract_cv_data(df: pd.DataFrame, step=None, scan_rate=None, cycle_number=None) -> pd.DataFrame:
    cv_df = _get_step_data(df, step=step, technique='CV', scan_rate=scan_rate, cycle_number=cycle_number)
    extracted = pd.DataFrame(
        {
            'experiment_step': cv_df['experiment_step'].reset_index(drop=True),
            'scan_rate': _numeric_column(cv_df, 'scan_rate').reset_index(drop=True),
            'cycle_number': cv_df['cycle_number'].reset_index(drop=True),
            'time': _numeric_column(cv_df, 'time_s').reset_index(drop=True),
            'voltage': -_numeric_column(cv_df, 'potential_V').reset_index(drop=True),
            'current': -_numeric_column(cv_df, 'current_A').reset_index(drop=True),
        }
    )
    return extracted.dropna(subset=['voltage', 'current'], how='all').reset_index(drop=True)


def extract_cv_data_by_scan_rate(df: pd.DataFrame, step=None, cycle_number=None) -> dict:
    """Return CV DataFrames grouped by scan rate (V/s).

    Keys are float scan-rate values or ``"unknown_scan_rate"`` if no scan rate
    is present. Each value is a DataFrame with columns ``time``, ``voltage``,
    ``current``, ``cycle_number``.
    """
    cv_data = _extract_cv_data(df, step=step, cycle_number=cycle_number)
    if cv_data.empty:
        return {}
    cv_groups = {}
    for sr, group in cv_data.groupby('scan_rate', dropna=False, sort=True):
        key = 'unknown_scan_rate' if pd.isna(sr) else float(sr)
        cv_groups[key] = group.reset_index(drop=True)
    return cv_groups
