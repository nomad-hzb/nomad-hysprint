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
    """
    test for the resistance passes but the values seem unphysical or at least too deviant compated to the 
    other files.
    Cross check the units/scale! Typical values for area-normalized series resistance are between 0.5 Ωcm2 
    for laboratory type solar cells and typical values for area-normalized shunt resistance are in the MΩcm2
    range
    """
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

    # Clean up
    delete_json()


def test_pvcomb_jv_parser(monkeypatch):
    file = 'HZB_MMX_B7_0_C-16.pxA_ch1_LS000min_2024-11-21T12-53-39_rev.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data

    # Test dictionary keys
    expected_keys = [
        'datetime',
        'active_area',
        'intensity',
        'compliance',
        'settling_time',
        'jv_curve',
    ]
    for key in expected_keys:
        assert hasattr(archive.data, key), f'Missing key: {key}'

    # Test specific values - adjust expected values based on your sample data
    assert archive.data.datetime.strftime('%Y-%m-%d %H:%M:%S') == '2024-11-21 12:53:50'
    assert abs(archive.data.active_area.magnitude - 0.16) < 1e-6
    assert abs(archive.data.intensity.magnitude - 100.0) < 1e-6
    assert abs(archive.data.settling_time.magnitude - 0.02) < 1e-6
    assert abs(archive.data.compliance.magnitude - 31.25) < 1e-6

    # Test array values - these need to be accessed through jv_curve objects
    assert len(archive.data.jv_curve) == 1  # PVComb has only one curve
    assert abs(archive.data.jv_curve[0].short_circuit_current_density.magnitude - 23.71677) < 1e-6
    assert abs(archive.data.jv_curve[0].open_circuit_voltage.magnitude - 1.078086) < 1e-6
    assert abs(archive.data.jv_curve[0].fill_factor - 0.6800677) < 1e-6
    assert abs(archive.data.jv_curve[0].efficiency - 17.38846) < 1e-6
    assert abs(archive.data.jv_curve[0].potential_at_maximum_power_point.magnitude - 0.8425) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density_at_maximun_power_point.magnitude - 20.63912) < 1e-6
    assert abs(archive.data.jv_curve[0].series_resistance.magnitude - 45.788151) < 1e-6
    assert abs(archive.data.jv_curve[0].shunt_resistance.magnitude - 7834.505) < 1e-6

    # # Test units
    assert archive.data.active_area.units == ureg.cm**2
    assert archive.data.intensity.units == ureg.mW / ureg.cm**2
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
    assert (
        archive.data.jv_curve[0].cell_name is not None
    )  # Adjust if cell_name is expected to be a specific value
    assert archive.data.jv_curve[0].voltage[0] is not None
    assert archive.data.jv_curve[0].current_density[0] is not None
    assert archive.data.jv_curve[0].voltage.units == ureg.V
    assert archive.data.jv_curve[0].current_density.units == ureg.mA / ureg.cm**2

    # # Test specific curve values - adjust based on your sample data
    assert abs(archive.data.jv_curve[0].voltage.magnitude[0] - 1.4) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density.magnitude[0] - 31.25374) < 1e-6

    # # Test the last line of values in the curve data
    assert abs(archive.data.jv_curve[0].voltage.magnitude[-1] - (-0.2)) < 1e-6
    assert abs(archive.data.jv_curve[0].current_density.magnitude[-1] - (-23.84712)) < 1e-6

    # Clean up
    delete_json()


def test_iris_jv_parser(monkeypatch):
    file = 'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt'
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
        'jv_curve',
    ]
    for key in expected_keys:
        assert hasattr(archive.data, key), f'Missing key: {key}'

    # Test specific values
    assert archive.data.datetime.strftime('%Y-%m-%d %H:%M:%S') == '2023-11-30 17:30:54'
    assert abs(archive.data.active_area.magnitude - 0.16) < 1e-6
    assert abs(archive.data.intensity.magnitude - 100.0) < 1e-6
    assert abs(archive.data.integration_time.magnitude - 100) < 1e-6
    assert abs(archive.data.settling_time.magnitude - 100) < 1e-6
    assert abs(archive.data.averaging - 3.0) < 1e-6

    # Test curves exist
    # 6 cells (a-f) × 4 measurements (Forward/Reverse × Light/Dark)
    assert len(archive.data.jv_curve) == 24

    # Test first JV curve (index 0): a_Forward_Dark
    curve0 = archive.data.jv_curve[0]
    assert curve0['cell_name'] == 'a_Forward_Dark'

    # Test second JV curve (index 1): a_Reverse_Dark
    curve1 = archive.data.jv_curve[1]
    assert curve1['cell_name'] == 'a_Reverse_Dark'
    assert abs(curve1['current_density'][0].magnitude - 0.2576272291666666) < 1e-6
    assert str(curve1['current_density'][0].units) == 'milliampere / centimeter ** 2'
    assert abs(curve1['voltage'][0].magnitude - 1.2) < 1e-6
    assert str(curve1['voltage'][0].units) == 'volt'

    # Test third JV curve (index 2): a_Forward_Light
    curve2 = archive.data.jv_curve[2]
    assert curve2['cell_name'] == 'a_Forward_Light'
    assert abs(curve2['light_intensity'].magnitude - 100.0) < 1e-6
    assert str(curve2['light_intensity'].units) == 'milliwatt / centimeter ** 2'
    assert abs(curve2['open_circuit_voltage'].magnitude - 0.31548588) < 1e-6
    assert abs(curve2['short_circuit_current_density'].magnitude - 3.57435437) < 1e-6
    assert abs(curve2['fill_factor'] - 0.32838176599999996) < 1e-8
    assert abs(curve2['efficiency'] - 0.37030243) < 1e-8
    assert abs(curve2['potential_at_maximum_power_point'].magnitude - 0.16) < 1e-6
    assert abs(curve2['current_density_at_maximun_power_point'].magnitude - 2.31439021) < 1e-6
    assert abs(curve2['series_resistance'].magnitude - 49.138047) < 1e-6
    assert str(curve2['series_resistance'].units) == 'centimeter ** 2 * ohm'
    assert abs(curve2['shunt_resistance'].magnitude - 178.4879356) < 1e-6
    assert str(curve2['shunt_resistance'].units) == 'centimeter ** 2 * ohm'
    assert abs(curve2['current_density'][0].magnitude + 4.383857708333333) < 1e-6  # negative value
    assert abs(curve2['voltage'][0].magnitude + 0.2) < 1e-6  # negative value

    # Test fourth JV curve (index 3): a_Reverse_Light
    curve3 = archive.data.jv_curve[3]
    assert curve3['cell_name'] == 'a_Reverse_Light'

    # Test fifth JV curve (index 4): b_Forward_Dark
    curve4 = archive.data.jv_curve[4]
    assert curve4['cell_name'] == 'b_Forward_Dark'

    # Test cell names for first five curves
    expected_cell_names = [
        'a_Forward_Dark',
        'a_Reverse_Dark',
        'a_Forward_Light',
        'a_Reverse_Light',
        'b_Forward_Dark',
    ]
    for i, expected_name in enumerate(expected_cell_names):
        assert archive.data.jv_curve[i]['cell_name'] == expected_name

    # Optionally, test that all 24 curves have a cell_name and at least one voltage/current_density value
    for curve in archive.data.jv_curve:
        assert 'cell_name' in curve
        assert 'voltage' in curve and len(curve['voltage']) > 0
        assert 'current_density' in curve and len(curve['current_density']) > 0

    # Clean up
    delete_json()


def test_iris_jv_json_parser(monkeypatch):
    file = 'hzb_TestP_AA_1_c-1.1_JM261.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    # Test data exists
    assert archive.data
    assert len(archive.data.jv_curve) == 12

    # Test first JV curve (index 0): a_Forward_Dark
    curve0 = archive.data.jv_curve[0]
    assert curve0['cell_name'] == 'A FWD'
    assert round(curve0['open_circuit_voltage'], 5) == -0.00173 * ureg('V')
    assert round(curve0['voltage'][0], 3) == -0.20 * ureg('V')

    # Clean up
    delete_json()
