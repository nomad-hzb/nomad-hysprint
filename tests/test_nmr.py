import pytest
from nomad.client import normalize_all
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture
def file():
    return 'hzok3106-AsAs_3_C_5.nmr.txt'


@pytest.fixture
def parsed_archive(file, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(file, monkeypatch)


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)
    delete_json()


def test_mppt_simple_parser(file, monkeypatch):
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)
    assert archive.data
    assert archive.metadata

    # # Test properties
    assert hasattr(archive.data, 'data')

    # Test properties with proper unit handling
    assert archive.data.data.chemical_shift[0] == 180.0 * ureg('ppm')
    assert archive.data.data.intensity[0] == 180.0

    # Clean up
    delete_json()
