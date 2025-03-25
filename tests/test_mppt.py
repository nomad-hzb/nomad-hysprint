import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_hysprint.parsers.hysprint_measurement_parser.set_sample_reference',
        mockreturn_search,
    )


def delete_json():
    for file in os.listdir(os.path.join('tests/data')):
        if not file.endswith('archive.json'):
            continue
        os.remove(os.path.join('tests', 'data', file))


def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name = os.path.join('tests', 'data', file_base)
    file_archive = parse(file_name)[0]
    assert file_archive.data

    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archive = parse(measurement)[0]

    return measurement_archive


@pytest.fixture(
    params=[
        'hzb_TestP_AA_2_c-5.mppt.txt'
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


def test_mppt_simple_parser(monkeypatch):
    file = 'hzb_TestP_AA_2_c-5.mppt.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    print(archive.data)
    delete_json()

    