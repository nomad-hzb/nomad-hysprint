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

# HySprint_SimpleMPPTracking testing (inheriting from MPPTracking baseclass)

# TODO 1 : read_mppt function
# raises encoding issue
# is the ² properly replaced?
# does it have na?
# if error for name of column 
# if data type is correct

def explore_mppt_file(file_path: str) -> str:
    """ Summary

Parameters
----------

Returns
-------

"""

    with open(file_path, "rb") as f:
        encoding = get_encoding(f)
    with open(file_path, 'tr', encoding=encoding) as f:
        filedata = f.read()
    return filedata
 

# HySprint_MPPTracking testing (inheriting from MPPTrackingHsprintCustom baseclass). Q: in which case will the parser activate this class?

# TODO : read_mppt function