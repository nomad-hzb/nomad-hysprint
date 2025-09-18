import pytest
from nomad.client import normalize_all
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture(
    params=[
        '0_1_0-ecf314iynbrwtd33zkk5auyebh.abspl.txt',
        'GaAs5_Large_Spot_center.abspl.txt',
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


def test_hysprint_abspl_parser(monkeypatch):
    file = 'GaAs5_Large_Spot_center.abspl.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data
    assert archive.data.results
    assert len(archive.data.results[0].wavelength) > 0
    assert len(archive.data.results[0].luminescence_flux_density) > 0
    assert len(archive.data.results[0].raw_spectrum_counts) > 0
    assert len(archive.data.results[0].dark_spectrum_counts) > 0
    assert archive.data.results[0].bandgap == 1.424 * ureg('eV')
    assert archive.data.results[0].derived_jsc == 26.46 * ureg('mA/cm**2')
    assert archive.data.results[0].quasi_fermi_level_splitting == 1.094 * ureg('eV')

    # Clean up
    delete_json()


def test_hysprint_abspl_parser_hy(monkeypatch):
    file = '100_40-1.abspl.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data
    assert archive.data.results
    assert archive.data.results[0].bandgap == 1.671 * ureg('eV')
    assert archive.data.results[0].quasi_fermi_level_splitting_het == 1.168 * ureg('eV')
    assert archive.data.results[0].i_voc == 1.172 * ureg('V')
    assert len(archive.data.results[0].wavelength) > 0
    assert len(archive.data.results[0].luminescence_flux_density) > 0
    assert len(archive.data.results[0].raw_spectrum_counts) > 0
    assert len(archive.data.results[0].dark_spectrum_counts) == 0

    # Clean up
    delete_json()
