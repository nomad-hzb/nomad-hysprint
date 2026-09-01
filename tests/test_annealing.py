import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'test_hysprint_annealing.xlsx',
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


# Constants for test assertions
N_PROCESSED_ARCHIVES = 4
ANNEALING_TIME = 30 * ureg('minute')
ANNEALING_TEMPERATURE = ureg.Quantity(120, ureg('°C'))
ANNEALING_ATMOSPHERE = 'Nitrogen'
NOTES = 'Annealing process notes'
TOOL_NAME = 'HZB-HotplateBox'


def test_hysprint_batch_parser(monkeypatch):
    file = 'test_hysprint_annealing.xlsx'
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

    PROCESS_CHECKS = {
        # Exact name matches for batch, sample, substrate (lowercased)
        'hzb_fina_2_1': check_batch,
        'hzb_fina_2_1_c-1': check_sample,
        'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
        # Step-specific process checks
        ('thermal annealing', 1.0): check_annealing,
    }

    for m in measurement_archives:
        name = getattr(m.data, 'name', None)
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        found = False
        name_lc = name.lower() if name else ''
        # Try tuple keys first (for step-specific checks)
        for k, func in PROCESS_CHECKS.items():
            if isinstance(k, tuple) and len(k) == 2:
                key_name, key_step = k
                if name_lc.startswith(key_name) and step == key_step:
                    if isinstance(func, list):
                        for f in func:
                            f(m)
                    else:
                        func(m)
                    found = True
                    break
        if not found:
            # Try exact string key match (for batch, sample, substrate)
            for k, func in PROCESS_CHECKS.items():
                if isinstance(k, str) and k == name_lc:
                    func(m)
                    found = True
                    break
        if not found:
            # Try string keys as prefix (for generic checks)
            for k, func in PROCESS_CHECKS.items():
                if isinstance(k, str) and name_lc.startswith(k):
                    func(m)
                    found = True
                    break
        if not found:
            print(f'No check function for process: {name} at step {step}')
    delete_json()


# Helper functions for each process type


def check_sample(m):
    assert m.data.name in ['HZB_FiNa_2_1_C-1']
    assert m.data.lab_id in ['HZB_FiNa_2_1_C-1']
    assert m.data.datetime.isoformat() == '2025-02-26T00:00:00+00:00'
    assert m.data.description == 'annealing test'


def check_batch(m):
    assert m.data.name == 'HZB_FiNa_2_1'
    assert m.data.lab_id == 'HZB_FiNa_2_1'
    assert len(m.data.entities) == 1
    assert m.data.entities[0].lab_id == 'HZB_FiNa_2_1_C-1'


def check_substrate(m):
    assert m.data.datetime.isoformat() == '2025-02-26T00:00:00+00:00'
    assert m.data.solar_cell_area == 0.16 * ureg('cm**2')
    assert m.data.number_of_pixels == 6.0
    assert m.data.pixel_area == 0.16 * ureg('cm**2')
    assert m.data.substrate == 'Soda Lime Glass'
    assert m.data.conducting_material == ['ITO']
    assert m.data.substrate_properties[0]['layer_type'] == 'Substrate Conductive Layer'
    assert m.data.substrate_properties[0]['layer_material_name'] == 'ITO'


def check_annealing(m):
    assert m.data.name == 'Thermal Annealing'
    assert m.data.description == NOTES
    assert m.data.location == TOOL_NAME
    assert m.data.samples[0].lab_id == 'HZB_FiNa_2_1_C-1'
    assert m.data.annealing['time'] == ANNEALING_TIME
    assert m.data.annealing['temperature'] == ANNEALING_TEMPERATURE
    assert m.data.annealing['atmosphere'] == ANNEALING_ATMOSPHERE
    assert m.data.atmosphere['relative_humidity'] == 25
