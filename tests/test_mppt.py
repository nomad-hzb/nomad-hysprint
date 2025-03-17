#!/usr/bin/env python3
"""
Created on Day Mon  2 13:48:09 2024

@author: a5263
"""

import os

import pytest
import warnings
from nomad_hysprint.schema_packages.file_parser.mppt_simple import read_mppt_file
from baseclasses.helper.utilities import get_encoding


TEST_FILE = '/home/a5263/nomad-distro-dev/packages/nomad-hysprint/tests/data/hzb_TestP_AA_2_c-5.mppt.txt'

# TODO: HySprint_SimpleMPPTracking testing (inheriting from MPPTracking baseclass)

# read_mppt function (is the ² properly replaced? does it have na? if error for name of column, if data type is correct, units are correct?)

def explore_mppt_file(file_path: str) -> str:
    """ Utility function that identifies the encoding of the experiment file and reads it using the appropriate encoding

Parameters : the path of the experimental file
----------

Returns : The content of the file in string
-------

"""

    with open(file_path, "rb") as f:
        encoding = get_encoding(f)
    with open(file_path, 'tr', encoding=encoding) as f:
        filedata = f.read()
    return filedata


filedata = explore_mppt_file(TEST_FILE)
data = read_mppt_file(filedata)

def test_dictionary_keys():
    expected_keys = {'time_data','step_size', 'time_per_track','active_area', 'voltage','time_data','voltage_data','current_density_data','power_data'}
    
    # Check if the returned value is a dictionary
    assert isinstance(data,dict), "read_mppt_file did not return dictionary"

    # Check if all expected keys are in the dictionary
    assert expected_keys.issubset(data.keys()), f"Missing read_mmpt_file dictionary keys: {expected_keys - data.keys()}"

# TODO: HySprint_MPPTracking testing (inheriting from MPPTrackingHsprintCustom baseclass). Q: in which case will the parser activate this class?

