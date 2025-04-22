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

import ast
from io import StringIO

import numpy as np
import pandas as pd
from baseclasses.helper.utilities import convert_datetime


def get_jv_data_hysprint(filedata):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.

    filedata = filedata.replace('²', '^2')

    df = pd.read_csv(
        StringIO(filedata),
        skiprows=8,
        nrows=9,
        sep='\t',
        index_col=0,
        engine='python',
        encoding='unicode_escape',
    )
    df_header = pd.read_csv(
        StringIO(filedata),
        skiprows=1,
        nrows=6,
        header=None,
        sep=':|\t',
        index_col=0,
        encoding='unicode_escape',
        engine='python',
    )
    df_curves = pd.read_csv(
        StringIO(filedata),
        header=19,
        skiprows=[20],
        sep='\t',
        encoding='unicode_escape',
        engine='python',
    )
    df_curves = df_curves.dropna(how='all', axis=1)

    df_header.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    number_of_curves = len(df_curves.columns) - 1

    jv_dict = {}
    jv_dict['active_area'] = df_header.iloc[0, 1]
    jv_dict['intensity'] = df_header.iloc[1, 1]
    jv_dict['integration_time'] = df_header.iloc[2, 1]
    jv_dict['settling_time'] = df_header.iloc[3, 1]
    jv_dict['averaging'] = df_header.iloc[4, 1]
    jv_dict['compliance'] = df_header.iloc[5, 1]

    jv_dict['J_sc'] = list(abs(df.iloc[0]))[:number_of_curves]
    jv_dict['V_oc'] = list(df.iloc[1])[:number_of_curves]
    jv_dict['Fill_factor'] = list(df.iloc[2])[:number_of_curves]
    jv_dict['Efficiency'] = list(df.iloc[3])[:number_of_curves]
    jv_dict['P_MPP'] = list(df.iloc[4])[:number_of_curves]
    jv_dict['J_MPP'] = list(abs(df.iloc[5]))[:number_of_curves]
    jv_dict['U_MPP'] = list(df.iloc[6])[:number_of_curves]
    jv_dict['R_ser'] = list(df.iloc[7])[:number_of_curves]
    jv_dict['R_par'] = list(df.iloc[8])[:number_of_curves]

    jv_dict['jv_curve'] = []
    for column in range(1, len(df_curves.columns)):
        jv_dict['jv_curve'].append(
            {
                'name': df_curves.columns[column],
                'voltage': df_curves[df_curves.columns[0]].values,
                'current_density': df_curves[df_curves.columns[column]].values,
            }
        )

    return jv_dict


def get_jv_data_pvcomb_1(filedata):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.

    filedata = filedata.replace('²', '^2')

    df = pd.read_csv(
        StringIO(filedata),
        header=None,
        skiprows=3,
        nrows=6,
        sep=':\t',
        index_col=0,
        engine='python',
        encoding='unicode_escape',
    )
    df_header = pd.read_csv(
        StringIO(filedata),
        skiprows=14,
        nrows=12,
        header=None,
        sep=':\t',
        index_col=0,
        encoding='unicode_escape',
        engine='python',
    )
    df_curves = pd.read_csv(
        StringIO(filedata),
        header=26,
        # skiprows=[20],
        sep='\t',
        encoding='unicode_escape',
        engine='python',
    )

    df_curves = df_curves.dropna(how='all', axis=1)

    df_header.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    jv_dict = {}
    jv_dict['datetime'] = convert_datetime(df.iloc[0, 0], '%d.%m.%Y %H:%M:%S')
    jv_dict['active_area'] = float(df.iloc[1, 0])
    jv_dict['intensity'] = float(df.iloc[2, 0]) / 10
    jv_dict['compliance'] = float(df.iloc[4, 0]) * 1000 / float(df.iloc[1, 0])
    jv_dict['settling_time'] = float(df.iloc[3, 0])

    jv_dict['J_sc'] = [df_header.iloc[7, 0]]
    jv_dict['V_oc'] = [df_header.iloc[1, 0]]
    jv_dict['Fill_factor'] = [float(df_header.iloc[5, 0])]
    jv_dict['Efficiency'] = [df_header.iloc[6, 0]]
    jv_dict['J_MPP'] = [df_header.iloc[8, 0]]
    jv_dict['U_MPP'] = [df_header.iloc[3, 0]]
    jv_dict['R_ser'] = [df_header.iloc[10, 0]]
    jv_dict['R_par'] = [df_header.iloc[11, 0]]

    jv_dict['jv_curve'] = [
        {
            'name': df.iloc[5, 0],
            'voltage': df_curves['V [V]'].values,
            'current_density': df_curves['J [mA/cm2]'].values,
        }
    ]

    return jv_dict


def get_jv_data_iris(filedata):
    # Block to clean up some bad characters found in the file which gives
    # trouble reading.

    filedata = filedata.replace('²', '^2')

    df = pd.read_csv(
        StringIO(filedata),
        skiprows=30,
        header=0,
        nrows=11,
        sep='\t',
        index_col=0,
        engine='python',
        encoding='unicode_escape',
    )

    df_header = pd.read_csv(
        StringIO(filedata),
        skiprows=0,
        nrows=29,
        header=None,
        sep='\t',
        index_col=0,
        encoding='unicode_escape',
        engine='python',
    )  # , on_bad_lines=lambda x: x[:2])

    df_curves = pd.read_csv(
        StringIO(filedata),
        header=0,
        skiprows=43,
        sep='\t',
        encoding='unicode_escape',
        engine='python',
    )
    df_curves = df_curves.dropna(how='all', axis=1)

    df_header.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    jv_dict = {}
    jv_dict['datetime'] = convert_datetime(df_header.iloc[0, 0], '%H:%M:%S - %d.%m.%Y')
    jv_dict['active_area'] = list(ast.literal_eval(df_header.iloc[12, 0]))[0]
    jv_dict['intensity'] = float(df_header.iloc[27, 0]) / 100 * 100
    jv_dict['integration_time'] = float(df_header.iloc[9, 0]) * 1000
    jv_dict['settling_time'] = float(df_header.iloc[10, 0]) * 1000
    jv_dict['averaging'] = float(df_header.iloc[8, 0])
    # jv_dict['compliance'] = df_header.iloc[5, 1]
    jv_dict['J_sc'] = list(abs(df.iloc[1].astype(np.float64)))
    jv_dict['V_oc'] = list(df.iloc[0].astype(np.float64))
    jv_dict['Fill_factor'] = list(df.iloc[2].astype(np.float64))
    jv_dict['Efficiency'] = list(df.iloc[3].astype(np.float64))
    jv_dict['P_MPP'] = list(abs(df.iloc[6].astype(np.float64)))
    jv_dict['J_MPP'] = list(abs(df.iloc[5].astype(np.float64)))
    jv_dict['U_MPP'] = list(df.iloc[4].astype(np.float64))
    jv_dict['R_ser'] = list(df.iloc[7].astype(np.float64))
    jv_dict['R_par'] = list(df.iloc[8].astype(np.float64))

    jv_dict['jv_curve'] = []

    for column in range(0, len(df_curves.columns) // 2):
        jv_dict['jv_curve'].append(
            {
                'name': '_'.join(df_curves.columns[2 * column].split('_')[-3:]),
                'dark': True if 'dark' in df_curves.columns[2 * column].lower() else False,
                'voltage': df_curves[df_curves.columns[2 * column]].values,
                'current_density': df_curves[df_curves.columns[2 * column + 1]].values,
            }
        )

    return jv_dict


def get_jv_data(filedata):
    if filedata.startswith('Keithley'):
        return get_jv_data_hysprint(filedata), 'HySprint HyVap'
    if 'SoSim PVcomB' in filedata:
        return get_jv_data_pvcomb_1(filedata), 'PVcomB'
    return get_jv_data_iris(filedata), 'IRIS HZBGloveBoxes Pero4SOSIMStorage'
