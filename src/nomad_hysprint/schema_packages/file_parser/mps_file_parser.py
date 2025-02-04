#!/usr/bin/env python3
"""
Created on Mon Dec 19 11:18:04 2022

@author: a2853
"""

from io import StringIO

import pandas as pd

encoding = 'iso-8859-1'


def headeranddelimiter(lines):
    header = 0
    header_found = False
    decimal = '.'
    for i, line in enumerate(lines):
        line_decode = line
        if line_decode.startswith('mode') or line_decode.startswith('freq/Hz'):
            header = i
            header_found = True
        if header_found:
            if ',' in line_decode and '.' not in line_decode:
                decimal = ','
            if '.' in line_decode and decimal == ',':
                raise Exception('decimal delimiter . and , found')

    return header, decimal


def parse_line(line, separator, encoding):
    stripped_line = line.strip()

    if not stripped_line:
        return '', ''

    if separator in stripped_line:
        split = list(filter(None, stripped_line.split(separator)))
        if len(split) < 2:
            return None, None
        key, value = split[0], ':'.join(split[1:])
        return key.strip(), value.strip()

    return None, None


def read_mps_file(datafile, encoding='iso-8859-1'):
    """Reads an MPS file, splits by : and if technique splits by spaces"""
    res = {}
    tmp = res
    separator = ':'

    with open(datafile, 'rb') as file:
        for line in file.readlines():
            key, value = parse_line(line, separator, encoding)

            if key is None and value is None:
                continue

            if key == '' and value == '':
                separator = ':'
                tmp = res
                continue

            if 'Technique' in key:
                separator = '  '
                res.update({f'{key} {value}': {}})
                tmp = res[f'{key} {value}']
                continue

            tmp.update({key: value})

    return res


def read_mpt_file(file, encoding='iso-8859-1'):
    """Reads an MPS file, splits by : and if technique splits by spaces"""
    metadata = {}
    separator = ':'
    technique = ''
    count = 0
    key = ''
    lines = file.readlines()
    for line in lines:
        line_decode = line
        if count == 3:
            technique = line_decode.strip()
        count += 1
        if line_decode.startswith('mode'):
            break
        if line_decode.startswith('vs.'):
            key_old = key
        if line_decode.strip() == '':
            continue

        if ':' in line_decode:
            separator = ':'
        else:
            separator = '  '

        key, value = parse_line(line_decode, separator, encoding)
        try:
            value = float(value)
        except BaseException:
            pass
        if key is None and value is None:
            continue

        if line_decode.startswith('vs.'):
            metadata.update({f'{key_old} {key}': value})
            continue
        metadata.update({key: value})

    header_line, decimal = headeranddelimiter(lines)
    data = pd.read_csv(
        StringIO(''.join(lines)),
        sep='\t',
        header=header_line,
        encoding=encoding,
        skip_blank_lines=False,
        decimal=decimal,
    )

    if 'Cyclic' in technique and 'nc cycles' in metadata:
        curve = 0
        data['curve'] = 0
        v_value_new = data.iloc[0]['Ewe/V']
        v_value_start = data.iloc[0]['Ewe/V']
        for index, row in data[1:].iterrows():
            v_value_old = v_value_new
            v_value_new = row['Ewe/V']
            if v_value_new < v_value_start and v_value_old > v_value_start:
                curve += 1

            data.at[index, 'curve'] = curve
        data = data.set_index('curve')

    return metadata, data, technique


# filename = '/home/a2853/Documents/Projects/nomad/hysprintlab/manuel/HZB_MaVa_20230519_ITO._OCV_C01.mpt'
# r, data, t = read_mpt_file(filename)
