import numpy as np
import pandas as pd

from nomad_hysprint.schema_packages.file_parser.eqe_parser import (
    arrange_eqe_columns,
    hc_eVnm,
    interpolate_eqe,
    read_file,
    read_file_multiple,
)


def dummy_interpolate_eqe(x, y):
    return x, y


def test_interpolate_eqe_basic():
    # Input data
    photon_energy_raw = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
    eqe_raw = np.array([0.2, 0.4, 0.6, 0.8, 1.0])

    # Run interpolation
    photon_energy_interp, eqe_interp = interpolate_eqe(photon_energy_raw, eqe_raw)

    # Assertions
    assert len(photon_energy_interp) == 1000
    assert len(eqe_interp) == 1000
    assert np.all(photon_energy_interp >= photon_energy_raw.min())
    assert np.all(photon_energy_interp <= photon_energy_raw.max())
    assert np.all(np.diff(photon_energy_interp) > 0)  # check increasing order
    assert not np.isnan(eqe_interp).any()


def test_arrange_eqe_columns_basic():
    df = pd.DataFrame({'Wavelength (nm)': [1240, 620, 310], 'Calculated': [20, 40, 60]})

    photon_energy_raw, eqe_raw = arrange_eqe_columns(df)

    expected_photon_energy = hc_eVnm / np.array([1240, 620, 310])  # ✅ Now 3 values
    expected_eqe = np.array([0.2, 0.4, 0.6])

    assert np.allclose(photon_energy_raw, expected_photon_energy)
    assert np.allclose(eqe_raw, expected_eqe)


def test_read_file_default_header():
    filedata = '1\t2\n3\t4\n5\t6'
    result = read_file(filedata)

    expected_photon_energy = np.array([1, 3, 5])
    expected_intensity = np.array([2, 4, 6])

    np.testing.assert_array_equal(result['photon_energy_raw'], expected_photon_energy)
    np.testing.assert_array_equal(result['intensty_raw'], expected_intensity)
    # Skip interpolated ones unless you're testing them too


def test_read_file_multiple_parsing_only(monkeypatch):
    monkeypatch.setattr(
        'nomad_hysprint.schema_packages.file_parser.eqe_parser.interpolate_eqe', dummy_interpolate_eqe
    )

    filedata = (
        'A\tB\tC\tD\tE\tF\n'
        'header1\theader2\theader3\theader4\theader5\theader6\n'
        'metadata1\tmetadata2\tmetadata3\tmetadata4\tmetadata5\tmetadata6\n'
        'metadata1\tmetadata2\tmetadata3\tmetadata4\tmetadata5\tmetadata6\n'
        'metadata1\tmetadata2\tmetadata3\tmetadata4\tmetadata5\tmetadata6\n'  # Added fifth row
        '400\t50\t1\t1\t1\t1\n'
        '500\t60\t1\t1\t1\t1\n'
        '600\t70\t1\t1\t1\t1\n'
    )

    result = read_file_multiple(filedata)

    assert isinstance(result, list)
    assert len(result) == 1

    parsed = result[0]
    expected_x = np.array([1239.84193 / 600, 1239.84193 / 500, 1239.84193 / 400])
    expected_y = np.array([0.7, 0.6, 0.5])

    np.testing.assert_array_almost_equal(parsed['photon_energy_raw'], expected_x)
    np.testing.assert_array_almost_equal(parsed['intensty_raw'], expected_y)


def test_sid1_eqe():
    with open('./tests/data/SID1.eqe.txt') as f:
        content = f.read()

    # Extract just the data block (after "//DATA//")
    if '//DATA//' in content:
        content = content.split('//DATA//', 1)[-1].strip()

    result = read_file(content)

    assert isinstance(result, dict)
    assert 'photon_energy' in result
    assert 'intensity' in result
    assert len(result['photon_energy']) == 1000
    assert all(isinstance(x, float) for x in result['photon_energy'])
    assert all(0 <= x <= 1 for x in result['intensity'])


def test_hzb_eqe():
    with open('./tests/data/hzb_TestP_AA_2_c-5.eqe.txt') as f:
        content = f.read()
    results = read_file_multiple(content)

    assert isinstance(results, list)
    assert len(results) > 0
    for res in results:
        assert 'photon_energy' in res
        assert 'intensity' in res
        assert len(res['photon_energy']) == 1000
        assert all(isinstance(x, float) for x in res['photon_energy'])
        assert all(0 <= x <= 1 for x in res['intensity'])
