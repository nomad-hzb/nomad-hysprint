import pytest
from nomad.client import normalize_all

from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        'HZB_MiGo_20230913_Batch-Test-1_0_0.notessfdsf.jv.txt',
        'HZB_MMX_B7_0_C-16.pxA_ch1_LS000min_2024-11-21T12-53-39_rev.jv.txt',
        'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt',
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


def test_trpl_parser_1(monkeypatch):
    file = 'trPL-S2-1800s-ND2-BE-A2-10kHz.trpl.csv'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data.trpl_properties.ns_per_bin.magnitude == 0.512

    # Clean up
    delete_json()


def test_trpl_parser_2(monkeypatch):
    file = '07-Si6505_10kHz-ND1-0.40uW-300s.trpl.dat'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data.trpl_properties.ns_per_bin.magnitude == 1.0

    # Clean up
    delete_json()


def test_trpl_parser_3(monkeypatch):
    file = 'M0-FAPI3Q6-Spot2_5400s_10kHz_ND1_210cps_0.0209011uW.trpl.dat'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data.trpl_properties.ns_per_bin.magnitude == 1.0

    # Clean up
    delete_json()


def test_trspv_parser_1(monkeypatch):
    file = '00-S3207-10avgs-filter36.trspv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data.properties.number_of_transients == 48.0

    # Clean up
    delete_json()
