#!/usr/bin/env python3
"""
Created on Mon Sep  2 13:48:09 2024

@author: a2853
"""
from io import StringIO

import numpy as np
import pandas as pd


def get_value(val):
    try:
        return float(val)
    except Exception:
        return None


def read_mppt_file(filedata):
    filedata = filedata.replace("²", "^2")

    df = pd.read_csv(
        StringIO(filedata),
        skiprows=0,
        nrows=5,
        header=None,
        sep=':\t',
        index_col=0,
        engine='python',
        encoding='unicode_escape')
    df_curve = pd.read_csv(
        StringIO(filedata),
        header=6,
        skiprows=[7],
        sep='\t',
        encoding='unicode_escape',
        engine='python')
    df_curve = df_curve.dropna(how='any', axis=0)

    mppt_dict = {}
    mppt_dict['total_time'] = get_value(df.iloc[0, 0])
    mppt_dict['step_size'] = get_value(df.iloc[1, 0])
    mppt_dict['time_per_track'] = get_value(df.iloc[2, 0])
    mppt_dict['active_area'] = get_value(df.iloc[3, 0])
    mppt_dict['voltage'] = get_value(df.iloc[4, 0])

    mppt_dict['time_data'] = np.array(df_curve["time"], dtype=np.float64)
    mppt_dict['voltage_data'] = np.array(df_curve["voltage"], dtype=np.float64)
    mppt_dict['current_density_data'] = np.array(
        df_curve["current density"],
        dtype=np.float64)
    mppt_dict['power_data'] = np.array(df_curve["power"], dtype=np.float64)

    return mppt_dict
