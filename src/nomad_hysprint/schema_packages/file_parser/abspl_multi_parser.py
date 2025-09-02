import re
import numpy as np
import pandas as pd
from io import StringIO

def parse_abspl_multi_entry_data(data_file, archive, logger):

    wavelengths = []
    lum_flux = []

    """Parses a multi-entry AbsPL data file and returns extracted settings, results, and spectral arrays per entry."""
    with archive.m_context.raw_file(data_file, mode='r') as f:
        lines = f.readlines()

    # Find the line where the data section begins
    data_start = None
    for i, line in enumerate(lines):
        if "Wavelength" in line:
            data_start = i
            break

    if data_start is None:
        raise ValueError("Spectral data section not found")

    # Read header lines (before data starts)
    header_lines = lines[:data_start]
    header_df = pd.read_csv(StringIO("".join(header_lines)), sep="\t", header=None)
    # Read numeric data (from data_start)
    numeric_lines = lines[data_start:]
    numeric_df = pd.read_csv(StringIO("".join(numeric_lines)), sep="\t", header=None)

    settings_vals, result_vals = parse_header_multi_entry(header_df)
    lum_flux, wavelengths = parse_numeric_multi_entry(numeric_df)

    return settings_vals, result_vals, wavelengths, lum_flux

def parse_header_multi_entry(header_df):
    header_map_settings = {
        'Laser Intensity (suns)': 'laser_intensity_suns',
        'Bias voltage (V)': 'bias_voltage',
        'SMU current density (mA/cm2)': 'smu_current_density',
        'Integration Time (ms)': 'integration_time',
        'Delay time (s)': 'delay_time',
        'EQE @ laser wavelength': 'eqe_laser_wavelength',
        'Laser spot size (cm²)': 'laser_spot_size',
        'Subcell area (cm²)': 'subcell_area',
        'Subcell': 'subcell_description',
    }

    header_map_result = {
        'LuQY (%)': 'luminescence_quantum_yield',
        'QFLS (eV)': 'quasi_fermi_level_splitting',
        'iVoc confidence': 'quasi_fermi_level_splitting',
        'iVoc (V)': 'i_voc',
        'Bandgap (eV)': 'bandgap',
        'Jsc (mA/cm2)': 'derived_jsc',
    }

    first_nan_index = header_df[header_df.isna().any(axis=1)].index.min()

    # Drop that row if it exists
    if pd.notna(first_nan_index):
        header_df = header_df.drop(index=first_nan_index)
    header_map_settings = {k: v for k, v in header_map_settings.items() if k in header_df.iloc[0].values}
    settings_vals = {k: header_df.iloc[0][k] for k in header_map_settings.keys()}
    result_vals = {k: header_df.iloc[0][k] for k in header_map_result.keys() if k in header_df.iloc[0].values}


    return settings_vals, result_vals

def parse_numeric_multi_entry(numeric_df):
    nan_positions = numeric_df.isna()
    numeric_df = numeric_df.iloc[2:].reset_index(drop=True)

    first_nan_index = numeric_df[numeric_df.isna().any(axis=1)].index.min()

    # Drop that row if it exists
    if pd.notna(first_nan_index):
        numeric_df = numeric_df.drop(index=first_nan_index)
    lum_flux_df = numeric_df.iloc[:, 1:]  # Assuming first column is wavelengths
    wavelengths_df = numeric_df.iloc[:, 0]  # Assuming first column is wavelengths

    lum_flux = [lum_flux_df[col].astype(float).tolist() for col in lum_flux_df.columns]
    wavelengths = wavelengths_df.astype(float).values.flatten().tolist()
    return lum_flux, wavelengths
