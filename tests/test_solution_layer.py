import os
import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg
from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'test_hysprint_blade_coating.xlsx',
    ]
)
def parsed_archive(request, monkeypatch):
    """Sets up data for testing and cleans up after the test."""
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive):
    normalize_all(parsed_archive)


@pytest.fixture(autouse=False)
def cleanup_json():
    yield
    delete_json()


def match_check(name_lc, step):
    # Tuple keys: exact name prefix + step match
    for k, func in PROCESS_CHECKS.items():
        if isinstance(k, tuple):
            key_name, key_step = k
            if name_lc.startswith(key_name) and step == key_step:
                return func
    # String keys: exact match
    for k, func in PROCESS_CHECKS.items():
        if isinstance(k, str) and k == name_lc:
            return func
    # String keys: prefix match
    for k, func in PROCESS_CHECKS.items():
        if isinstance(k, str) and name_lc.startswith(k):
            return func
    return None


def test_hysprint_batch_parser(cleanup_json):
    file_name = os.path.join('tests', 'data', '20260603_Experiment_solution-layer.xlsx')
    parse(file_name)

    measurement_archives = []
    for fname in os.listdir(os.path.join('tests', 'data')):
        if 'archive.json' not in fname:
            continue
        measurement = os.path.join('tests', 'data', fname)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    unmatched = []
    for m in measurement_archives:
        name = getattr(m.data, 'name', None)
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        name_lc = name.lower() if name else ''

        func = match_check(name_lc, step)
        if func is None:
            unmatched.append(f'{name} at step {step}')
            continue

        if isinstance(func, list):
            for f in func:
                f(m)
        else:
            func(m)

    if unmatched:
        pytest.fail(f'No check function for processes:\n' + '\n'.join(unmatched))


# Helper functions

def check_substrate(m):
    props = m.data.substrate_properties[0]
    assert props['layer_sheet_resistance'] == 15 * ureg('Ohms/square')
    assert props['layer_transmission'] == 90 * ureg('%')


def check_slot_die(m):
    sol = m.data.solution[0]
    assert sol['solution_viscosity'] == 120 * ureg('mPa*s')
    assert sol['solution_contact_angle'] == 45 * ureg('°')
    assert sol['solution_density'] == 1 * ureg('g/cm^3')
    assert sol['solution_surface_tension'] == 72 * ureg('mN/m')

PROCESS_CHECKS = {
    'substrate 1 cm x 1 cm soda lime glass ito': check_substrate,
    ('slot die coating', 1.0): check_slot_die,
}