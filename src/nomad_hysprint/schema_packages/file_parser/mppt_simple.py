#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 13:48:09 2024

@author: a2853
"""
import chardet
import pandas as pd
import numpy as np


def get_value(val):
    try:
        return float(val)
    except:
        return None


def read_mppt_file(filename, encoding):
    with open(filename, 'r', encoding=encoding) as f:
        filedata = f.read()

    newdata = filedata.replace("²", "^2")

    with open(filename, 'w') as f:
        f.write(newdata)

    with open(filename) as f:
        df = pd.read_csv(
            f,
            skiprows=0,
            nrows=5,
            header=None,
            sep=':\t',
            index_col=0,
            engine='python',
            encoding='unicode_escape')
    with open(filename) as f:
        df_curve = pd.read_csv(
            f,
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
    mppt_dict['current_density_data'] = np.array(df_curve["current density"], dtype=np.float64)
    mppt_dict['power_data'] = np.array(df_curve["power"], dtype=np.float64)

    return mppt_dict


# file = "/home/a2853/Documents/Projects/nomad/hysprintlab/mppt/0a4d713aea22a9edaf1ac8b98fd5e44e.20211129_ re_02-2.mppt.txt"
# with open(file, 'br') as f:
#     en = chardet.detect(f.read())["encoding"]
# read_mppt_file(file, en)
