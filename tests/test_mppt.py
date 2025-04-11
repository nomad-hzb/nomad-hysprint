import numpy as np
import pytest
from nomad.client import normalize_all
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture
def file():
    return 'hzb_TestP_AA_2_c-5.mppt.txt'


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
    assert hasattr(archive.data, 'properties')

    # Test properties with proper unit handling
    assert archive.data.properties.time == 180.0 * ureg('second')
    assert archive.data.properties.perturbation_voltage == 0.01 * ureg('volt')

    # # Test data arrays
    assert hasattr(archive.data, 'time')
    assert hasattr(archive.data, 'voltage')
    assert hasattr(archive.data, 'current_density')
    assert hasattr(archive.data, 'power_density')

    # Test array lengths
    assert len(archive.data.time) > 0
    assert len(archive.data.voltage) == len(archive.data.time)
    assert len(archive.data.current_density) == len(archive.data.time)
    assert len(archive.data.power_density) == len(archive.data.time)

    # Test specific values from the sample data
    # First value tests
    assert np.isclose(archive.data.time[0].magnitude, 2.8320e-2)
    assert np.isclose(archive.data.voltage[0].magnitude, 9.5000e-1)
    assert np.isclose(archive.data.current_density[0].magnitude, -2.2999e1)
    assert np.isclose(archive.data.power_density[0].magnitude, -2.1849e1)

    # Check units
    assert str(archive.data.time[0].units) == 'second'
    assert str(archive.data.voltage[0].units) == 'volt'
    assert str(archive.data.current_density[0].units) == 'milliampere / centimeter ** 2'
    assert str(archive.data.power_density[0].units) == 'milliwatt / centimeter ** 2'

    # Test that all voltage values are within the range they appear in the measurement
    voltage_magnitudes = np.array([v.magnitude for v in archive.data.voltage])
    assert np.allclose(voltage_magnitudes, 9.5000e-1, rtol=0.3e-1)

    # Clean up
    delete_json()
