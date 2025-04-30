import json
import os
from datetime import datetime

import pandas as pd

base = '..'
target = '12.12'
file_name = f'{base}/{target}/20240915_experiment_file_12.12.xlsx'
upload_id = 'SpiRNIJ-RSmBslrJdDMzug'


xls = pd.ExcelFile(file_name)
df = pd.read_excel(xls, 'Sheet', header=[0, 1])


def get_entry_id_from_file_name(file_name, upload_id):
    from nomad.utils import hash

    return hash(upload_id, file_name)


def get_reference(upload_id, file_name):
    entry_id = get_entry_id_from_file_name(file_name, upload_id)
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def convert_quantity(value, factor):
    try:
        return float(value) * factor
    except:
        return None


def get_value(data, key, default=None, number=True):
    try:
        if pd.isna(data[key]):
            return default
        try:
            if number:
                return float(data[key])
        except:
            pass
        return str(data[key]).strip()
    except:
        return None


def map_basic_sample(data, substrate_name):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Sample',
            'name': data['Nomad ID'],
            'lab_id': data['Nomad ID'],
            'substrate': get_reference(upload_id, substrate_name),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'description': get_value(data, 'Variation', None, False),
        }
    }
    return (data['Nomad ID'], archive)


def map_batch(batch_ids, batch_id):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Batch',
            'name': batch_id,
            'lab_id': batch_id,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'entities': [{'lab_id': s_id} for s_id in batch_ids],
        }
    }
    return (batch_id, archive)


def map_solutions(data):
    solvents = []
    solutes = []
    for col in data.index:
        if 'solvent' in col.lower():
            solvents.append(' '.join(col.split(' ')[:2]))
        if 'solute' in col.lower():
            solutes.append(' '.join(col.split(' ')[:2]))

    archive = {'solvent': [], 'solute': []}
    for solvent in sorted(set(solvents)):
        if not get_value(data, f'{solvent} name', None, False) and not get_value(
            data, f'{solvent} volume [uL]', None
        ):
            continue
        print(solvent, get_value(data, f'{solvent} name', None, False))
        archive['solvent'].append(
            {
                'chemical_2': {'name': get_value(data, f'{solvent} name', None, False), 'load_data': False},
                'chemical_volume': convert_quantity(
                    get_value(data, f'{solvent} volume [uL]', None), 1 / 1000
                ),
            }
        )
    for solute in sorted(set(solutes)):
        if not get_value(data, f'{solute} type', None, False) and not get_value(
            data, f'{solute} Concentration [mM]', None
        ):
            continue
        archive['solute'].append(
            {
                'chemical_2': {'name': get_value(data, f'{solute} type', None, False), 'load_data': False},
                'concentration_mol': convert_quantity(
                    get_value(data, f'{solute} Concentration [mM]', None), 1 / 1000
                ),
            }
        )
    return archive


def map_spin_coating(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_SpinCoating',
            'name': 'spin coating ' + get_value(data, 'Material name', '', False),
            'positon_in_experimental_plan': i,
            'method': 'Spin coating',
            'description': get_value(data, 'Notes', '', False),
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'layer': [
                {
                    'layer_type': get_value(data, 'Layer type', None, False),
                    'layer_material_name': get_value(data, 'Material name', None, False),
                }
            ],
            'solution': [
                {
                    'solution_details': map_solutions(data),  # check unit
                    # check unit
                    'solution_volume': convert_quantity(
                        get_value(data, 'Solution volume [um]', None), 1 / 1000
                    ),
                }
            ],
            'annealing': {
                'temperature': get_value(data, 'Annealing temperature [°C]', None),
                'time': convert_quantity(get_value(data, 'Annealing time [min]', None), 60),
            },
            'recipe_steps': [
                {
                    'speed': get_value(data, 'Rotation speed [rpm]', None),
                    'time': get_value(data, 'Rotation time [s]', None),
                }
            ],
        }
    }

    return (f'{i}_{j}_spin_coating_{get_value(data, "Material name", "", False)}', archive)


def map_sdc(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_SlotDieCoating',
            'name': 'slot die coating ' + get_value(data, 'Material name', '', False),
            'positon_in_experimental_plan': i,
            'method': 'Slot die coating',
            'description': get_value(data, 'Notes', None, False),
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'solution': [
                {
                    'solution_details': map_solutions(data),  # check unit
                    # check unit
                    'solution_volume': convert_quantity(
                        get_value(data, 'Solution volume [um]', None), 1 / 1000
                    ),
                }
            ],
            'layer': [
                {
                    'layer_type': get_value(data, 'Layer type', None, False),
                    'layer_material_name': get_value(data, 'Material name', None, False),
                }
            ],
            'annealing': {
                'temperature': get_value(data, 'Annealing temperature [°C]', None),
                'time': convert_quantity(get_value(data, 'Annealing time [min]', None), 60),
            },
            'properties': {
                'flow_rate': convert_quantity(data.get('Flow rate [ul/min]', None), 1 / 1000),
                'slot_die_head_distance_to_thinfilm': get_value(data, 'Head gap [mm]'),
                'slot_die_head_speed': get_value(data, 'Speed [mm/s]'),
            },
            'quenching': {
                'm_def': 'baseclasses.material_processes_misc.AirKnifeGasQuenching',
                # "air_knife_speed":convert_quantity(data.get("Flow rate [ul/min]"), 1/1000)
                'air_knife_angle': get_value(data, 'Air knife angle [°]', None),
                'bead_volume': get_value(data, 'Bead volume [mm/s]', None),
                'drying_speed': get_value(data, 'Drying speed [cm/min]', None),
                'air_knife_distance_to_thin_film': convert_quantity(
                    data.get('Air knife gap [cm]', None), 10000
                ),
            },
        }
    }

    return (f'{i}_{j}_slot_die_coating_{get_value(data, "Material name", "", False)}', archive)


def map_cleaning(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Cleaning',
            'name': 'Cleaning',
            'positon_in_experimental_plan': i,
            'description': get_value(data, 'Notes', '', False),
            'method': 'Cleaning',
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
    }

    return (f'{i}_{j}_cleaning', archive)


def map_substrate(data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Substrate',
            'name': 'Substrate '
            + get_value(data, 'Sample dimension', '', False)
            + ' '
            + get_value(data, 'Substrate material', '', False)
            + ' '
            + get_value(data, 'Substrate conductive layer', '', False),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'solar_cell_area': get_value(data, 'Sample area [cm^2]', ''),
            'substrate': get_value(data, 'Substrate material', '', False),
            'conducting_material': [get_value(data, 'Substrate conductive layer', '', False)],
        }
    }
    return archive


def map_evaporation(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Evaporation',
            'name': 'evaporation ' + get_value(data, 'Material name', '', False),
            'positon_in_experimental_plan': i,
            'method': 'Evaporation',
            'description': get_value(data, 'Notes', '', False),
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'layer': [
                {
                    'layer_type': get_value(data, 'Layer type', None, False),
                    'layer_material_name': get_value(data, 'Material name', None, False),
                }
            ],
        }
    }
    if get_value(data, 'Organic', '', False).lower().startswith('n'):
        archive['data'].update(
            {
                'inorganic_evaporation': [
                    {
                        'thickness': get_value(data, 'Thickness [nm]'),
                        'start_rate': get_value(data, 'Rate [angstrom/s]'),
                        'chemical_2': {
                            'name': get_value(data, 'Material name', None, False),
                            'load_data': False,
                        },
                    }
                ]
            }
        )

    if get_value(data, 'Organic', '', False).lower().startswith('y'):
        archive['data'].update(
            {
                'organic_evaporation': [
                    {
                        'thickness': get_value(data, 'Thickness [nm]'),
                        'start_rate': get_value(data, 'Rate [angstrom/s]'),
                        'temperature': [get_value(data, 'Temperature [°C]', None)] * 2
                        if get_value(data, 'Temperature [°C]', None)
                        else None,
                        'chemical_2': {
                            'name': get_value(data, 'Material name', None, False),
                            'load_data': False,
                        },
                    }
                ]
            }
        )

    return (f'{i}_{j}_evaporation_{get_value(data, "Material name", "", False)}', archive)


def map_sputtering(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Sputtering',
            'name': 'sputtering ' + get_value(data, 'Material name', '', False),
            'positon_in_experimental_plan': i,
            'method': 'Sputtering',
            'description': get_value(data, 'Notes', '', False),
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'layer': [
                {
                    'layer_type': get_value(data, 'Layer type', None, False),
                    'layer_material_name': get_value(data, 'Material name', None, False),
                }
            ],
        }
    }
    archive['data'].update(
        {
            'processes': [
                {
                    'thickness': get_value(data, 'Thickness [nm]'),
                    'gas_flow_rate': get_value(data, 'Gas flow rate [cm^3/min]'),
                    'rotation_rate': get_value(data, 'Rotation rate [rpm]'),
                    'power': get_value(data, 'Power [W]'),
                    'temperature': get_value(data, 'Temperature [°C]'),
                    'deposition_time': get_value(data, 'Deposition time [s]'),
                    'burn_in_time': get_value(data, 'Burn in time [s]'),
                    'pressure': get_value(data, 'Pressure [mbar]'),
                    'target_2': {'name': get_value(data, 'Material name', None, False), 'load_data': False},
                    'gas_2': {'name': get_value(data, 'Gas', None, False), 'load_data': False},
                }
            ]
        }
    )

    return (f'{i}_{j}_sputtering_{get_value(data, "Material name", "", False)}', archive)


def map_generic(i, j, lab_ids, data):
    archive = {
        'data': {
            'm_def': 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Process',
            'name': get_value(data, 'Name', '', False),
            'positon_in_experimental_plan': i,
            'description': get_value(data, 'Notes', '', False),
            'samples': [{'lab_id': lab_id} for lab_id in lab_ids],
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
    }
    return (f'{i}_{j}_generic_process', archive)


sample_ids = df['Experiment Info']['Nomad ID'].dropna().to_list()
batch_id = '_'.join(sample_ids[0].split('_')[:-1])
archives = [map_batch(sample_ids, batch_id)]
substrates = []

for i, sub in (
    df['Experiment Info'][
        ['Sample dimension', 'Sample area [cm^2]', 'Substrate material', 'Substrate conductive layer']
    ]
    .drop_duplicates()
    .iterrows()
):
    if pd.isna(sub).all():
        continue
    substrates.append((f'{i}_substrate', sub, map_substrate(sub)))


def find_substrate(d):
    for s in substrates:
        if d.equals(s[1]):
            return s[0]


for i, row in df['Experiment Info'].iterrows():
    if pd.isna(row).all():
        continue
    substrate_name = (
        find_substrate(
            row[
                ['Sample dimension', 'Sample area [cm^2]', 'Substrate material', 'Substrate conductive layer']
            ]
        )
        + '.archive.json'
    )
    archives.append(map_basic_sample(row, substrate_name))

for i, col in enumerate(df.columns.get_level_values(0).unique()):
    if col == 'Experiment Info':
        continue

    df_dropped = df[col].drop_duplicates()
    for j, row in df_dropped.iterrows():
        lab_ids = [
            x['Experiment Info']['Nomad ID']
            for _, x in df[['Experiment Info', col]].iterrows()
            if x[col].equals(row)
        ]
        if 'Cleaning' in col:
            archives.append(map_cleaning(i, j, lab_ids, row))
        if pd.isna(row.get('Material name')):
            continue
        if 'Evaporation' in col:
            archives.append(map_evaporation(i, j, lab_ids, row))

        if 'Spin Coating' in col:
            archives.append(map_spin_coating(i, j, lab_ids, row))

        if 'Slot Die Coating' in col:
            archives.append(map_sdc(i, j, lab_ids, row))

        if 'Sputtering' in col:
            archives.append(map_sputtering(i, j, lab_ids, row))

        if 'Generic Process' in col:
            archives.append(map_generic(i, j, lab_ids, row))


for subs in substrates:
    with open(os.path.join(base, target, 'processes', f'{subs[0]}.archive.json'), 'w') as f:
        json.dump(subs[2], f)

for archive in archives:
    with open(os.path.join(base, target, 'processes', f'{archive[0]}.archive.json'), 'w') as f:
        json.dump(archive[1], f)
