#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


# Evaluation of EQE measurement data + Urbach tail to determine the radiative open-circuit voltage.
# Building from the work of Lisa Krückemeier et al. (https://doi.org/10.1002/aenm.201902573)
# Initially translated to Python by Christian Wolff


from io import StringIO

import numpy as np
import pandas as pd

# Constants
temperature = 300  # in [°K]
q = 1.602176462e-19  # % [As], elementary charge
h_Js = 6.62606876e-34  # % [Js], Planck's constant
k = 1.38064852e-23  # % [(m^2)kg(s^-2)(K^-1)], Boltzmann constant
T = temperature
VT = (k * T) / q  # % [V], 25.8mV thermal voltage at 300K
c = 299792458  # % [m/s], speed of light c_0
hc_eVnm = h_Js * c / q * 1e9  # % [eV nm]  Planck's constant for energy to wavelength conversion


def interpolate_eqe(photon_energy_raw, eqe_raw):
    photon_energy_interpolated = np.linspace(min(photon_energy_raw), max(photon_energy_raw), 1000, endpoint=True)
    eqe_interpolated = np.interp(photon_energy_interpolated, photon_energy_raw, eqe_raw)

    return photon_energy_interpolated, eqe_interpolated


def arrange_eqe_columns(df):
    """
    Gets a df with columns of the file and returns a `photon_energy_raw` array
    and `eqe_raw` array with values of the photon energy values in *eV* and
    the eqe (values between 0 and 1) respectively.
    It finds if the eqe data comes in nm or eV and converts it to eV.

    Returns:
        photon_energy_raw: array of photon energy values in eV
        eqe_raw: array of eqe values
    """
    if 'Calculated' in list(df.columns):  # for files from the hzb
        x = df.iloc[:, 0].values
        y = df['Calculated'].values
    else:
        x = df.iloc[:, 0].values
        y = df.iloc[:, 1].values

    if any(x > 10):  # check if energy (eV) or wavelength (nm)
        x = hc_eVnm / x
    if any(y > 10):  # check if EQE is given in (%), if so it's translated to abs. numbers
        y = y / 100

    # bring both arrays into correct order (i.e. w.r.t eV increasing) if one started with e.g. wavelength in increasing order e.g. 300nm, 305nm,...
    if x[1] - x[2] > 0:
        x = np.flip(x)
        y = np.flip(y)

    photon_energy_raw = x
    eqe_raw = y
    return photon_energy_raw, eqe_raw


def read_file(file_path, header_lines=None):
    """
    Reads the file and returns the columns in a pandas DataFrame `df`.
    :return: df
    :rtype: pandas.DataFrame
    """
    if header_lines is None:
        header_lines = 0
    if header_lines == 0:  # in case you have a header
        try:
            df = pd.read_csv(file_path, header=None, sep='\t',)
            if len(df.columns) < 2:
                raise IndexError
        except IndexError:
            df = pd.read_csv(file_path, header=None)
    else:
        try:
            # header_lines - 1 assumes last header line is column names
            df = pd.read_csv(file_path, header=int(header_lines - 1), sep='\t')
            if len(df.columns) < 2:
                raise IndexError
        except IndexError:
            try:  # wrong separator?
                df = pd.read_csv(file_path, header=int(header_lines - 1))
                if len(df.columns) < 2:
                    raise IndexError
            except IndexError:
                try:  # separator was right, but last header_line is not actually column names?
                    df = pd.read_csv(file_path, header=int(header_lines), sep='\t')
                    if len(df.columns) < 2:
                        raise IndexError
                except IndexError:
                    # Last guess: separator was wrong AND last header_line is not actually column names?
                    df = pd.read_csv(file_path, header=int(header_lines))
                    if len(df.columns) < 2:
                        raise IndexError
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna()
    photon_energy_raw, eqe_raw = arrange_eqe_columns(df)
    photon_energy, intensity = interpolate_eqe(photon_energy_raw, eqe_raw)
    return photon_energy_raw, eqe_raw, photon_energy, intensity


def read_file_multiple(filedata):
    df = pd.read_csv(StringIO(filedata), sep="\t")
    result = []
    for i in range(0, len(df.columns), 6):
        try:
            x = np.array(df[df.columns[i]][4:], dtype=np.float64)
            y = np.array(df[df.columns[i+1]][4:], dtype=np.float64)

            x = x[np.isfinite(x)]
            y = y[np.isfinite(y)]
            if any(x > 10):  # check if energy (eV) or wavelength (nm)
                x = hc_eVnm / x
            if any(y > 10):  # check if EQE is given in (%), if so it's translated to abs. numbers
                y = y / 100

            # bring both arrays into correct order (i.e. w.r.t eV increasing) if one started with e.g. wavelength in increasing order e.g. 300nm, 305nm,...
            if x[1] - x[2] > 0:
                x = np.flip(x)
                y = np.flip(y)
            photon_energy, intensity = interpolate_eqe(x, y)

            result.append({
                "photon_energy_raw": x,
                "intensty_raw": y,
                "photon_energy": photon_energy,
                "intensity": intensity,
            })
        except:
            continue
    return result
