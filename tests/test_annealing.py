import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'test_hysprint_double_annealing.xlsx',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)
    delete_json()


# Constants for test assertions.
#
# test_hysprint_double_annealing.xlsx has 4 groups of samples (one per
# subbatch). Each group goes through a "1: Spin Coating" step that carries
# its own embedded annealing sub-step, followed by a separate standalone
# "2: Annealing" step - so every group exercises both ways annealing data
# can show up in an experiment plan. The two annealing temperatures differ
# per group and are looked up below by the group's first sample lab_id.
N_PROCESSED_ARCHIVES = 28

SPIN_COATING_ANNEALING_TIME = 10 * ureg('minute')
STANDALONE_ANNEALING_TIME = 20 * ureg('minute')
ANNEALING_ATMOSPHERE = 'Nitrogen'
STANDALONE_RELATIVE_HUMIDITY = 0.0

# keyed by each group's first sample lab_id
SPIN_COATING_GROUPS = {
    'HZB_double_annealing_1_1_1': {'temperature': 1.0, 'n_samples': 4},
    'HZB_double_annealing_1_2_5': {'temperature': 3.0, 'n_samples': 4},
    'HZB_double_annealing_1_3_9': {'temperature': 5.0, 'n_samples': 4},
    'HZB_double_annealing_1_4_13': {'temperature': 7.0, 'n_samples': 6},
}
STANDALONE_ANNEALING_GROUPS = {
    'HZB_double_annealing_1_1_1': {'temperature': 2.0, 'n_samples': 4},
    'HZB_double_annealing_1_2_5': {'temperature': 4.0, 'n_samples': 4},
    'HZB_double_annealing_1_3_9': {'temperature': 6.0, 'n_samples': 4},
    'HZB_double_annealing_1_4_13': {'temperature': 8.0, 'n_samples': 6},
}


def test_hysprint_batch_parser(monkeypatch):
    file = 'test_hysprint_double_annealing.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == N_PROCESSED_ARCHIVES

    measurement_archives = []
    for fname in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in fname:
            continue
        measurement = os.path.join('tests', 'data', fname)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    checked_types = set()
    for m in measurement_archives:
        type_name = type(m.data).__name__
        if type_name == 'HySprint_Batch':
            check_batch(m)
        elif type_name == 'HySprint_Sample':
            check_sample(m)
        elif type_name == 'HySprint_Substrate':
            check_substrate(m)
        elif type_name == 'HySprint_SpinCoating':
            check_spin_coating_annealing(m)
        elif type_name == 'HySprint_Annealing':
            check_standalone_annealing(m)
        else:
            print(f'No check function for process: {type_name}')
            continue
        checked_types.add(type_name)

    assert checked_types == {
        'HySprint_Batch',
        'HySprint_Sample',
        'HySprint_Substrate',
        'HySprint_SpinCoating',
        'HySprint_Annealing',
    }
    delete_json()


# Helper functions for each process type


def check_sample(m):
    assert m.data.name == m.data.lab_id
    assert m.data.name.startswith('HZB_double_annealing_1_')
    assert m.data.datetime.isoformat() == '2026-09-02T00:00:00+00:00'
    assert m.data.description


def check_batch(m):
    assert m.data.name == 'HZB_double_annealing_1_1'
    assert m.data.lab_id == 'HZB_double_annealing_1_1'
    assert len(m.data.entities) == 18


def check_substrate(m):
    assert m.data.datetime.isoformat() == '2026-09-02T00:00:00+00:00'
    assert m.data.solar_cell_area == 1.0 * ureg('cm**2')
    assert m.data.number_of_pixels == 1.0
    assert m.data.pixel_area == 1.0 * ureg('cm**2')
    assert m.data.substrate == 'Glass'
    assert m.data.conducting_material == ['ITO']
    assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
    assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'


def check_spin_coating_annealing(m):
    """Annealing as a supporting sub-step nested inside Spin Coating."""
    group = SPIN_COATING_GROUPS[m.data.samples[0].lab_id]
    assert m.data.name == 'spin coating Pero'
    assert len(m.data.samples) == group['n_samples']
    assert m.data.annealing['time'] == SPIN_COATING_ANNEALING_TIME
    assert m.data.annealing['temperature'] == ureg.Quantity(group['temperature'], ureg('°C'))
    assert m.data.annealing['atmosphere'] == ANNEALING_ATMOSPHERE


def check_standalone_annealing(m):
    """Annealing as its own standalone, top-level process."""
    group = STANDALONE_ANNEALING_GROUPS[m.data.samples[0].lab_id]
    assert m.data.name == 'Thermal Annealing'
    assert len(m.data.samples) == group['n_samples']
    assert m.data.annealing['time'] == STANDALONE_ANNEALING_TIME
    assert m.data.annealing['temperature'] == ureg.Quantity(group['temperature'], ureg('°C'))
    assert m.data.annealing['atmosphere'] == ANNEALING_ATMOSPHERE
    assert m.data.atmosphere['relative_humidity'] == STANDALONE_RELATIVE_HUMIDITY
