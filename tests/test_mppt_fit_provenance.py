from datetime import datetime, timezone

import numpy as np
import pytest
from baseclasses.solar_energy.mpp_tracking import FitParameter, StabilityFiguresOfMerit
from nomad.client import normalize_all
from nomad.units import ureg

from utils import delete_json, get_archive


@pytest.fixture
def file():
    return 'test_file.mppt.txt'


def test_mppt_fit_provenance_automatic(file, monkeypatch):
    """
    Parses a real MPP tracking file through HySprint_SimpleMPPTracking and checks the
    fit-provenance fields added to StabilityFiguresOfMerit (nomad-baseclasses#181).

    On the automatic (savgol_filter) path only fit_method, fit_source, fitted_time and
    fitted_power_density are populated; the rest are reserved for a manual/external fit
    and are covered by test_mppt_fit_provenance_manual below.
    """
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data.results
    result = archive.data.results[0]
    assert isinstance(result, StabilityFiguresOfMerit)

    assert result.fit_method == 'savgol_filter'
    assert result.fit_source == 'automatic'

    assert result.fitted_time is not None
    assert result.fitted_power_density is not None
    assert len(result.fitted_time) > 0
    assert len(result.fitted_time) == len(result.fitted_power_density)
    assert str(result.fitted_time.units) == 'second'
    assert str(result.fitted_power_density.units) == 'milliwatt / centimeter ** 2'

    # Not populated on the automatic path - reserved for a manual/external fit.
    assert result.fit_range_start is None
    assert result.fit_range_end is None
    assert result.fit_computed_by is None
    assert result.fit_computed_at is None
    assert result.fit_r_squared is None
    assert result.lifetime_energy_yield is None
    assert not result.fit_parameters

    delete_json()


def test_mppt_fit_provenance_manual(file, monkeypatch):
    """
    Simulates an external analysis app (e.g. MPPT_Analysis) writing back a manual fit's
    provenance before normalization, and checks that normalize() preserves those values
    with the correct types rather than overwriting them with the automatic savgol_filter
    result.
    """
    archive = get_archive(file, monkeypatch)

    fit_computed_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    archive.data.results = [
        StabilityFiguresOfMerit(
            fit_method='Stretched Exponential',
            fit_source='manual',
            fit_range_start=0.0 * ureg('s'),
            fit_range_end=100.0 * ureg('s'),
            fitted_time=np.array([0.0, 50.0, 100.0]) * ureg('s'),
            fitted_power_density=np.array([-18.0, -17.5, -17.0]) * ureg('mW/cm**2'),
            fit_computed_by='MPPT_Analysis v0.3',
            fit_computed_at=fit_computed_at,
            fit_r_squared=0.987,
            lifetime_energy_yield=12.3 * ureg('kWh/m**2'),
            fit_parameters=[FitParameter(name='tau', value=42.0, unit='h')],
        )
    ]

    normalize_all(archive)

    result = archive.data.results[0]
    assert result.fit_method == 'Stretched Exponential'
    assert result.fit_source == 'manual'
    assert result.fit_range_start == 0.0 * ureg('s')
    assert result.fit_range_end == 100.0 * ureg('s')
    assert len(result.fitted_time) == 3
    assert len(result.fitted_power_density) == 3
    assert result.fit_computed_by == 'MPPT_Analysis v0.3'
    assert result.fit_computed_at == fit_computed_at
    assert np.isclose(result.fit_r_squared, 0.987)
    assert np.isclose(result.lifetime_energy_yield.to('kWh/m**2').magnitude, 12.3)
    assert len(result.fit_parameters) == 1
    assert result.fit_parameters[0].name == 'tau'
    assert np.isclose(result.fit_parameters[0].value, 42.0)
    assert result.fit_parameters[0].unit == 'h'

    delete_json()
