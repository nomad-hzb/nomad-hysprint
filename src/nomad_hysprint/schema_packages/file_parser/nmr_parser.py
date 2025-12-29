#!/usr/bin/env python3
"""
Created on Tue Aug 19 14:00:11 2025

@author: a2853
"""

import re
from datetime import datetime

import numpy as np


def get_nmr_data_hysprint_txt(filedata):
    ppm_re = '%s = [+-]?([0-9]*[.])?[0-9]+ ppm'
    x = re.search(ppm_re % 'LEFT', filedata)
    left = float(x.group()[7:-4])
    x = re.search(ppm_re % 'RIGHT', filedata)
    right = float(x.group()[7:-4])

    intensity = []
    lines = filedata.split('\n')
    for line in lines:
        if line.startswith('#') or not line:
            continue
        intensity.append(float(line))


    dt_str = lines[0].split('=', 1)[1].strip().strip(' Central European Summer Time')


    f = '%A, %B %d, %Y at %I:%M:%S %p'
    dt_obj = datetime.strptime(dt_str, f)

    return np.linspace(left, right, len(intensity)), np.array(intensity), dt_obj
