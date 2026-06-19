import os

import pytest
from nomad.client import parse
from nomad.units import ureg

from utils import delete_json


@pytest.fixture(autouse=False)
def cleanup_json():
    yield
    delete_json()


def check_substrate(m):
    props = m.data.substrate_properties[0]
    assert props['layer_sheet_resistance'] == 15 * ureg('ohm')
    assert props['layer_transmission'] == 90.0


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


def match_check(name_lc, step):
    for k, func in PROCESS_CHECKS.items():
        if isinstance(k, tuple):
            key_name, key_step = k
            if name_lc.startswith(key_name) and step == key_step:
                return func
    for k, func in PROCESS_CHECKS.items():
        if isinstance(k, str) and (k == name_lc or name_lc.startswith(k)):
            return func
    return None


def test_hysprint_batch_parser(cleanup_json):
    file_name = os.path.join('tests', 'data', '20260603_Experiment_solution-layer.xlsx')
    parse(file_name)

    measurement_archives = [
        parse(os.path.join('tests', 'data', fname))[0]
        for fname in os.listdir(os.path.join('tests', 'data'))
        if 'archive.json' in fname
    ]
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    checked = 0
    for m in measurement_archives:
        name = getattr(m.data, 'name', None)
        step = getattr(m.data, 'positon_in_experimental_plan', None)
        name_lc = name.lower() if name else ''

        func = match_check(name_lc, step)
        if func is not None:
            func(m)
            checked += 1

    assert checked == len(PROCESS_CHECKS), (
        f'Expected to run {len(PROCESS_CHECKS)} checks, but only ran {checked}'
    )
