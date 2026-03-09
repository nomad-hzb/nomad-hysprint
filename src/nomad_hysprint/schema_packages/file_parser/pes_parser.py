#!/usr/bin/env python3
"""
Created on Fri Jun  6 19:44:15 2025

@author: a2853
"""

import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from baseclasses.characterizations import (
    PESSpecsLabProdigyAnalyzerParameters,
    PESSpecsLabProdigySettings,
    PESSpecsLabProdigySourceParameters,
)
from nomad.units import ureg


def parse_pes_xy_file(filedata):
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
            current[key.strip()] += '<br>' + line.strip('#').strip()
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
                return float(v)
            return float(v) * ureg(u)
        if is_number:
            return float(value)
        return value
    except Exception:
        return None


def map_specs_lab_prodigy_data(res):
    analyzer_parameters = PESSpecsLabProdigyAnalyzerParameters(
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
        focus_displacement=map_value(res['Analyzer Parameters'].get('Focus Displacement 1'), True, True),
        l1=map_value(res['Analyzer Parameters'].get('L1'), True, True),
    )
    source_parameters = PESSpecsLabProdigySourceParameters(
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
    section = PESSpecsLabProdigySettings(
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

    comment = map_value(res.get('Comment'), False, False)
    if comment:
        for c in comment.split('<br>'):
            if 'Sample Bias Voltage' in c:
                section.sample_bias_voltage = map_value(
                    c.split('=', 1)[1][:-1], is_number=True, with_unit=False
                )
            if 'He-gas pressure' in c:
                section.he_gas_pressure = map_value(c.split('=', 1)[1][:-4], is_number=True, with_unit=False)

    method = 'XPS'
    if 'ConstantFinalState' in res.get('Scan Mode'):
        method = 'CFSYS'
    if 'FixedAnalyzerTransmission' in res.get('Scan Mode', '') and 'Monochromator' in res[
        'Source Parameters'
    ].get('Name', ''):
        method = 'NUPS'
    if 'FixedAnalyzerTransmission' in res.get('Scan Mode', '') and 'He' in res['Source Parameters'].get(
        'Settings Summary', ''
    ):
        method = 'He-UPS'

    return section, method


def _parse_datetime_from_json(
    time_str: str,
    local_tz: str = 'Europe/Berlin',
) -> datetime | None:
    """
    Parse JSON timestamp string to timezone-aware datetime.

    JSON files from SpectraPENGUIN store timestamps in the measurement
    machine's **local time** (no timezone indicator in the string).
    The parsed datetime is tagged with the correct local timezone
    (CET/CEST by default) so that comparisons with Prodigy XY timestamps
    (which carry explicit UTC / UTC+N suffixes) work correctly.

    Supports two formats:
    - Old: "20251211112654"      (YYYYMMDDHHmmss)
    - New: "28.01.2026_08:32:50" (DD.MM.YYYY_HH:MM:SS)

    Parameters
    ----------
    time_str : str
        Timestamp string in one of the two formats above.
    local_tz : str
        IANA timezone name of the measurement machine (default: "Europe/Berlin").

    Returns
    -------
    datetime or None
        Timezone-aware datetime in the machine's local timezone,
        or None if parsing fails.
    """
    if not time_str or time_str == '0':
        return None

    try:
        tz = ZoneInfo(local_tz)

        # Try new format first: DD.MM.YYYY_HH:MM:SS
        if '.' in time_str and '_' in time_str:
            dt = datetime.strptime(time_str, '%d.%m.%Y_%H:%M:%S')
            return dt.replace(tzinfo=tz)

        # Fall back to old format: YYYYMMDDHHmmss
        dt = datetime.strptime(time_str, '%Y%m%d%H%M%S')
        return dt.replace(tzinfo=tz)
    except (ValueError, TypeError):
        return None


# Get relevant time stamp from .xy prodigy
def _parse_utc_datetime(text: str) -> datetime:
    """
    Parse a Prodigy-style datetime string with timezone suffix.

    Supported formats:
        "2025-11-17 09:56:48 UTC"       -> UTC  (offset +0)
        "2025-11-17 10:56:48 UTC+1"     -> CET  (offset +1)
        "2025-11-17 11:56:48 UTC+2"     -> CEST (offset +2)

    Returns a timezone-aware datetime with the correct UTC offset.
    """
    text = text.strip()

    # Match "YYYY-MM-DD HH:MM:SS" followed by a timezone suffix
    m = re.match(
        r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+UTC([+-]\d+)?$',
        text,
    )
    if not m:
        raise ValueError(f'Cannot parse datetime string: {text!r}')

    dt_str, offset_str = m.group(1), m.group(2)
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    if offset_str:
        offset_hours = int(offset_str)
    else:
        offset_hours = 0  # plain "UTC"

    return dt.replace(tzinfo=timezone(timedelta(hours=offset_hours)))


# folder = '/home/a2853/Downloads/1File_Per_Scan/'
# for file in os.listdir(folder):
#     with open(os.path.join(folder, file), encoding='ISO-8859-15') as f:
#         res = parse_pes_xy_file(f.read())
