import numpy as np
#from src.nomad_hysprint.schema_packages.file_parser.eqe_parser import interpolate_eqe
from nomad_hysprint.schema_packages.file_parser.eqe_parser import interpolate_eqe, arrange_eqe_columns, hc_eVnm
import pandas as pd





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
    df = pd.DataFrame({
    'Wavelength (nm)': [1240, 620, 310],
    'Calculated': [20, 40, 60]
    })

    photon_energy_raw, eqe_raw = arrange_eqe_columns(df)

    expected_photon_energy = hc_eVnm / np.array([1240, 620, 310])  # ✅ Now 3 values
    expected_eqe = np.array([0.2, 0.4, 0.6])


    assert np.allclose(photon_energy_raw, expected_photon_energy)
    assert np.allclose(eqe_raw, expected_eqe)
