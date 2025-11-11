from io import StringIO

import pandas as pd


def get_trpl_measurement_hy_gui(filedata):
    file_lines = filedata.split('\n')

    bin_line = -1
    count_line = -1
    counts = []
    time = []
    for l_idx, raw_line in enumerate(file_lines):
        line = raw_line.strip()
        if line.startswith('#ns/bin'):
            bin_line = l_idx + 1
        if l_idx == bin_line:
            ns_per_bin = float(line)
        if line.startswith('#counts'):
            count_line = l_idx + 1
        if l_idx >= count_line >= 0 and line:
            counts.append(float(line))
            time.append(
                float((l_idx + 1 - count_line) * ns_per_bin)
                if ns_per_bin > 0
                else float(l_idx + 1 - count_line)
            )
    return {'counts': counts, 'time': time, 'ns_per_bin': ns_per_bin}


def get_trpl_measurement_wannsee(filedata):
    file_lines = filedata.split('\n')
    res = {}
    for l_idx, raw_line in enumerate(file_lines):
        if not raw_line.startswith('#') or len(raw_line.split(':', 1)) < 2:
            break

        key, value = raw_line.split(':', 1)
        if 'Integration time' in key:
            res['integration_time'] = float(value.strip().split(' ')[0])  # s
        if 'Excitation wavelength' in key:
            res['excitation_peak_wavelength'] = float(value.strip().split(' ')[0])  # nm
        if 'Detection wavelength' in key:
            res['detection_wavelength'] = float(value.strip().split(' ')[0])  # nm
        if 'Spot size' in key:
            res['spotsize'] = float(value.strip().split(' ')[0]) / 1e8  # cm**2
        if 'Repetition rate' in key:
            res['repetition_rate'] = float(value.strip().split(' ')[0]) / 1000  # MHZ

    df = pd.read_csv(StringIO('\n'.join(file_lines[l_idx:])), header=0, sep=',')
    res.update(
        {
            'counts': df[' counts'],
            'time': df['# delay_time [ps]'],
            'ns_per_bin': (df['# delay_time [ps]'].iloc[1] - df['# delay_time [ps]'].iloc[0]) / 1000,
        }
    )
    return res


def get_trpl_measurement_hy_auto(filedata):
    df = pd.read_csv(StringIO(filedata), index_col=0, header=0, sep='\t')
    return {
        'counts': df['counts [#]'],
        'time': df['bins [ps]'],
        'ns_per_bin': (df['bins [ps]'].iloc[1] - df['bins [ps]'].iloc[0]) / 1000,
    }


def get_trpl_measurement(filedata):
    if '#ns/bin' in filedata:
        return get_trpl_measurement_hy_gui(filedata)
    elif 'bins [ps]	counts [#]' in filedata:
        return get_trpl_measurement_hy_auto(filedata)
    else:
        return get_trpl_measurement_wannsee(filedata)
