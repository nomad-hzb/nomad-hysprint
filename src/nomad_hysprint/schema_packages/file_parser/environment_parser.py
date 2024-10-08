#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 11:44:19 2023

@author: a2853
"""

import pandas as pd
from io import StringIO


def find_data(filedata):
    for num, line in enumerate(filedata, 1):
        if "Time [s]" in line:
            return num-1


def get_environment_data(filedata, encoding='utf-8'):
    nrows = find_data(filedata)
    if nrows is None:
        return
    data = pd.read_csv(StringIO(filedata), sep="\t", skiprows=nrows)

    return data
