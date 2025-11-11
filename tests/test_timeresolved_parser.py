from nomad.client import normalize_all

from utils import delete_json, get_archive


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
