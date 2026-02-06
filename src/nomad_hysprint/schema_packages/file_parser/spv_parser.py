#!/usr/bin/env python3
"""
Created on Thu Sep  7 11:44:19 2023

@author: a2853
"""

from io import StringIO

import pandas as pd


def is_float(string):
    try:
        # Return true if float
        float(string)
        return True
    except ValueError:
        # Return False if Error
        return False


def find_footer(file_lines):
    for num, line in enumerate(file_lines, 1):
        if 'BEGIN_METADATA' in line:
            return num - 5
    return num


def get_spv_data(filedata):
    file_lines = filedata.split('\n')
    nrows = find_footer(file_lines)
    if nrows is None:
        return None, None
    data = pd.read_csv(StringIO(filedata), sep='\t', nrows=nrows)

    md_dict = {}
    for num, line in enumerate(file_lines, 1):
        if num < nrows or ':' not in line:
            continue
        line_split = line.split(':')
        line_split[0] = line_split[0].replace('#', '')
        value = float(line_split[1].strip()) if is_float(line_split[1].strip()) else line_split[1].strip()
        md_dict.update({line_split[0].strip(): value})
    return md_dict, data
