import os

import pandas as pd
import pytest
from nomad.client import parse
from nomad.units import ureg

from utils import delete_json, set_monkey_patch

SPIN_DELAY = 'Spin Delay [s]'

# Experiment files whose spin coating steps have the 'Spin Delay [s]' column filled in.
FILES_WITH_SPIN_DELAY = [
    '20250114_experiment_file.xlsx',
    '20250305_experiment_file.xlsx',
    'excel_test_file.xlsx',
]
# Older experiment file without the 'Spin Delay [s]' column.
LEGACY_FILE = '20240915_test_experiment.xlsx'


def parse_spin_coatings(file, monkeypatch):
    """Parse an experiment file and return its spin coating entries."""
    set_monkey_patch(monkeypatch)
    delete_json()
    parse(os.path.join('tests', 'data', file))
    spin_coatings = []
    for fname in sorted(os.listdir(os.path.join('tests', 'data'))):
        if not fname.endswith('archive.json'):
            continue
        entry = parse(os.path.join('tests', 'data', fname))[0]
        if type(entry.data).__name__ == 'HySprint_SpinCoating':
            spin_coatings.append(entry.data)
    delete_json()
    return spin_coatings


@pytest.fixture
def cleanup():
    yield
    delete_json()


@pytest.mark.parametrize('file', FILES_WITH_SPIN_DELAY)
def test_spin_delay_from_excel(file, monkeypatch, cleanup):
    df = pd.read_excel(os.path.join('tests', 'data', file), header=[0, 1])
    headers = list(df.columns.get_level_values(0).unique())
    lab_ids = df['Experiment Info']['Nomad ID']

    spin_coatings = parse_spin_coatings(file, monkeypatch)
    assert spin_coatings

    checked_headers = set()
    for spin_coating in spin_coatings:
        # the mapper's position is the index of the process column group
        header = headers[int(spin_coating.positon_in_experimental_plan)]
        assert header.endswith('Spin Coating')
        rows = lab_ids.isin([sample.lab_id for sample in spin_coating.samples])
        values = df[header][SPIN_DELAY][rows].dropna().unique()
        assert len(values) == 1
        # the single spin delay of the process goes into every recipe step
        assert spin_coating.recipe_steps
        for step in spin_coating.recipe_steps:
            assert step.spin_delay == ureg.Quantity(float(values[0]), ureg('s'))
        checked_headers.add(header)

    assert checked_headers == {h for h in headers if h.endswith('Spin Coating')}


def test_spin_delay_missing_in_legacy_excel(monkeypatch, cleanup):
    df = pd.read_excel(os.path.join('tests', 'data', LEGACY_FILE), header=[0, 1])
    spin_headers = [h for h in df.columns.get_level_values(0).unique() if h.endswith('Spin Coating')]
    assert spin_headers
    assert all(SPIN_DELAY not in df[h].columns for h in spin_headers)

    spin_coatings = parse_spin_coatings(LEGACY_FILE, monkeypatch)
    assert spin_coatings
    steps = [step for spin_coating in spin_coatings for step in spin_coating.recipe_steps]
    assert steps
    assert all(step.spin_delay is None for step in steps)
