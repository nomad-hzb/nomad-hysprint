import pytest
from nomad.client import normalize_all
from nomad.units import ureg
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


def test_hysprint_jv_parser(monkeypatch):
    file = 'HZB_MiGo_20230913_Batch-Test-1_0_0.notessfdsf.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data

    # Test dictionary keys
    expected_keys = [
        'datetime',
        'active_area',
        'intensity',
        'integration_time',
        'settling_time',
        'averaging',
        'compliance',
        'jv_curve',
    ]
    for key in expected_keys:
        assert hasattr(archive.data, key), f'Missing key: {key}'

    # Test specific values
    assert abs(archive.data.jv_curve[2].efficiency - 20.1) < 1e-6
    assert abs(archive.data.active_area.magnitude - 0.16) < 1e-6
    assert abs(archive.data.intensity.magnitude - 100.0) < 1e-6
    assert abs(archive.data.integration_time.magnitude - 20.0) < 1e-6
    assert abs(archive.data.settling_time.magnitude - 40.0) < 1e-6
    assert abs(archive.data.averaging - 1.0) < 1e-6
    assert abs(archive.data.compliance.magnitude - 30.0) < 1e-6

    # Test array values - these need to be accessed through jv_curve objects
    assert len(archive.data.jv_curve) == 6
    assert abs(archive.data.jv_curve[0].short_circuit_current_density.magnitude - 21.990472) < 1e-6
    assert abs(archive.data.jv_curve[0].open_circuit_voltage.magnitude - 1.212763) < 1e-6
    assert abs(archive.data.jv_curve[0].fill_factor - 0.79948537) < 1e-6
    assert abs(archive.data.jv_curve[0].efficiency - 20.2) < 1e-6
    assert abs(archive.data.jv_curve[0].potential_at_maximum_power_point.magnitude - 1.030000) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density_at_maximun_power_point.magnitude - 20.700637) < 1e-6
    assert abs(archive.data.jv_curve[0].series_resistance.magnitude - 0.003881) < 1e-6
    assert abs(archive.data.jv_curve[0].shunt_resistance.magnitude - 7.713772) < 1e-6

    # Test units for the first curve
    assert archive.data.active_area.units == ureg.cm**2
    assert archive.data.intensity.units == ureg.mW / ureg.cm**2
    assert archive.data.integration_time.units == ureg.ms
    assert archive.data.settling_time.units == ureg.ms
    assert archive.data.compliance.units == ureg.mA / ureg.cm**2

    assert archive.data.jv_curve[0].short_circuit_current_density.units == ureg.mA / ureg.cm**2
    assert archive.data.jv_curve[0].open_circuit_voltage.units == ureg.V
    # Note: fill_factor is stored as a decimal, not with units
    assert archive.data.jv_curve[0].potential_at_maximum_power_point.units == ureg.V
    assert archive.data.jv_curve[0].current_density_at_maximun_power_point.units == ureg.mA / ureg.cm**2
    assert archive.data.jv_curve[0].series_resistance.units == ureg.ohm * ureg.cm**2
    assert archive.data.jv_curve[0].shunt_resistance.units == ureg.ohm * ureg.cm**2

    # Test curve data
    assert len(archive.data.jv_curve) == 6
    assert archive.data.jv_curve[0].cell_name == 'b_rev'
    assert archive.data.jv_curve[0].voltage[0] is not None
    assert archive.data.jv_curve[0].current_density[0] is not None
    assert archive.data.jv_curve[0].voltage.units == ureg.V
    assert archive.data.jv_curve[0].current_density.units == ureg.mA / ureg.cm**2

    # Test specific curve values
    assert abs(archive.data.jv_curve[0].voltage.magnitude[0] - 1.25) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density.magnitude[0] - 10.25890) < 1e-6
    assert abs(archive.data.jv_curve[1].voltage.magnitude[1] - 1.23) < 1e-6
    assert abs(archive.data.jv_curve[1].current_density.magnitude[1] - 7.418619) < 1e-6

    # Test the last line of values in the curve data
    assert abs(archive.data.jv_curve[0].voltage.magnitude[-1] - (-0.19000)) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density.magnitude[-1] - (-22.02528)) < 1e-6
    assert abs(archive.data.jv_curve[1].current_density.magnitude[-1] - (-22.02426)) < 1e-6
    assert abs(archive.data.jv_curve[2].current_density.magnitude[-1] - (-21.96246)) < 1e-6
    assert abs(archive.data.jv_curve[3].current_density.magnitude[-1] - (-21.96426)) < 1e-6
    assert abs(archive.data.jv_curve[4].current_density.magnitude[-1] - (-22.17145)) < 1e-6
    assert abs(archive.data.jv_curve[5].current_density.magnitude[-1] - (-22.17339)) < 1e-6


def test_pvcomb_jv_parser(monkeypatch):
    file = 'HZB_MMX_B7_0_C-16.pxA_ch1_LS000min_2024-11-21T12-53-39_rev.jv.txt'
    pass


def test_iris_jv_parser(monkeypatch):
    file = 'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt'
    pass
