#!/usr/bin/env python3
"""
Created on Fri Jun  6 19:44:15 2025

@author: a2853
"""

from baseclasses.characterizations import (
    XPSSpecsLabProdigyAnalyzerParameters,
    XPSSpecsLabProdigySettings,
    XPSSpecsLabProdigySourceParameters,
)
from nomad.units import ureg


def parse_xps_xy_file(filedata):
    res = {}
    current = res
    key = None
    for line in filedata.split('\n'):
        if not line.startswith('#'):
            return res
        if line.strip() == '#':
            current = res
            continue
        if line.strip().startswith('#     '):
            if not key:
                continue
            current[key.strip()] += '\n' + line.strip('#').strip()
            continue
        if ':' not in line or line.strip().endswith(':'):
            key = line.strip('#').split(':')[0]
            res[key.strip()] = {}
            current = res[key.strip()]
            continue
        key, value = line.strip('#').split(':', 1)
        current[key.strip()] = value.strip()


def map_value(value, is_number=False, with_unit=False):
    if not is_number and with_unit:
        return None
    try:
        if with_unit:
            v, u = value.split(' ', 1)
            if 'nu' in u.lower():
                return float(value)
            return float(v) * ureg(u)
        if is_number:
            return float(value)
        return value
    except Exception:
        return None


def map_specs_lab_prodigy_data(res):
    analyzer_parameters = XPSSpecsLabProdigyAnalyzerParameters(
        polar_angle=map_value(res['Analyzer Parameters'].get('Polar Angle'), True, True),
        azimuth_angle=map_value(res['Analyzer Parameters'].get('Azimuth Angle'), True, True),
        rotation_angle=map_value(res['Analyzer Parameters'].get('Rotation Angle'), True, True),
        coil_current=map_value(res['Analyzer Parameters'].get('Coil Current'), True, True),
        bias_voltage_ions=map_value(res['Analyzer Parameters'].get('Bias Voltage Ions'), True, True),
        bias_voltage_electrons=map_value(
            res['Analyzer Parameters'].get('Bias Voltage Electrons'), True, True
        ),
        detector_voltage=map_value(res['Analyzer Parameters'].get('Detector Voltage (Target)'), True, True),
        work_function=map_value(res['Analyzer Parameters'].get('Work Function'), True, False),
        focus_displacement=map_value(res['Analyzer Parameters'].get('Focus Displacement 1'), True, False),
        l1=map_value(res['Analyzer Parameters'].get('L1'), True, False),
    )
    source_parameters = XPSSpecsLabProdigySourceParameters(
        polar_angle=map_value(res['Source Parameters'].get('Polar Angle'), True, True),
        azimuth_angle=map_value(res['Source Parameters'].get('Azimuth Angle'), True, True),
        excitation_energy=map_value(res['Source Parameters'].get('Excitation Energy'), True, True),
        device_state=map_value(res['Source Parameters'].get('device_state'), False, False),
        preset_name=map_value(res['Source Parameters'].get('preset_name'), False, False),
        anode=map_value(res['Source Parameters'].get('anode'), False, False),
        anode_voltage=map_value(res['Source Parameters'].get('anode_voltage'), True, False),
        anode_current=map_value(res['Source Parameters'].get('anode_current'), True, False),
        filament_current=map_value(res['Source Parameters'].get('filament_current'), True, False),
        filament_voltage=map_value(res['Source Parameters'].get('filament_voltage'), True, False),
        power=map_value(res['Source Parameters'].get('power'), True, False),
        emission=map_value(res['Source Parameters'].get('emission'), True, False),
        arcs=map_value(res['Source Parameters'].get('arcs'), True, False),
        lens_voltage=map_value(res['Source Parameters'].get('lens_voltage'), True, False),
        lens_current=map_value(res['Source Parameters'].get('lens_current'), True, False),
        focused=map_value(res['Source Parameters'].get('focused'), False, False),
        settings_summary=map_value(res['Source Parameters'].get('Settings Summary'), False, False),
    )
    section = XPSSpecsLabProdigySettings(
        region=map_value(res.get('Region'), False, False),
        calibration_file=map_value(res.get('Calibration File'), False, False),
        analyzer_lens_mode=map_value(res.get('Analyzer Lens Mode'), False, False),
        scan_variable=map_value(res.get('Scan Variable'), False, False),
        step_size=map_value(res.get('Step Size'), True, False),
        dwell_time=map_value(res.get('Dwell Time'), True, False),
        excitation_energy=map_value(res.get('Excitation Energy'), True, False),
        kinetic_energy=map_value(res.get('Kinetic Energy'), True, False),
        binding_energy=map_value(res.get('Binding Energy'), True, False),
        pass_energy=map_value(res.get('Pass Energy'), True, False),
        bias_voltage=map_value(res.get('Bias Voltage'), True, False),
        detector_voltage=map_value(res.get('Detector Voltage'), True, False),
        effective_work_function=map_value(res.get('Eff. Workfunction'), True, False),
        iris_diameter=map_value(res.get('Iris Diameter'), True, False),
        analyzer_slit=map_value(res.get('Analyzer Slit'), False, False),
        analyzer_lens_voltage=map_value(res.get('Analyzer Lens Voltage'), False, False),
        analyzer_parameters=analyzer_parameters,
        source_parameters=source_parameters,
    )
    method = 'XPS'
    if 'ConstantFinalState' in res.get('Scan Mode'):
        method = 'CFSYS'
    if 'FixedAnalyzerTransmission' in res.get('Scan Mode', '') and 'Monochromator' in res[
        'Source Parameters'
    ].get('Name', ''):
        method = 'NUPS'
    if 'FixedAnalyzerTransmission' in res.get('Scan Mode', '') and 'He' in res.get('Settings Summary', ''):
        method = 'He-UPS'

    return section, method


# folder = '/home/a2853/Downloads/1File_Per_Scan/'
# for file in os.listdir(folder):
#     with open(os.path.join(folder, file), encoding='ISO-8859-15') as f:
#         res = parse_xps_xy_file(f.read())
