#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import os
import sys
from pathlib import Path

from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    set_sample_reference,
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import Activity
from nomad.metainfo import Quantity
from nomad.parsing import MatchingParser

from nomad_hysprint.schema_packages.hysprint_package import (
    HySprint_AbsPLMeasurement,
    HySprint_CyclicVoltammetry,
    HySprint_DifferentialPulseVoltammetry,
    HySprint_ElectrochemicalImpedanceSpectroscopy,
    HySprint_EQEmeasurement,
    HySprint_JVmeasurement,
    HySprint_Measurement,
    HySprint_OpenCircuitVoltage,
    HySprint_PES,
    HySprint_PLImaging,
    HySprint_PLmeasurement,
    HySprint_SEM,
    HySprint_Simple_NMR,
    HySprint_SimpleMPPTracking,
    HySprint_TimeResolvedPhotoluminescence,
    HySprint_trSPVmeasurement,
    HySprint_UVvismeasurement,
    HySprint_XRD_XY,
    HZB_EnvironmentMeasurement,
    HZB_NKData,
)

"""
This is a hello world style example for an example parser/converter.
"""


class RawFileHZB(EntryData):
    processed_archive = Quantity(
        type=Activity,
    )


def update_general_process_entries(entry, entry_id, archive, logger):
    from nomad import files
    from nomad.search import search

    query = {
        'entry_id': entry_id,
    }
    search_result = search(owner='all', query=query, user_id=archive.metadata.main_author.user_id)
    entry_type = search_result.data[0].get('entry_type') if len(search_result.data) == 1 else None
    if entry_type != 'HySprint_Measurement':
        return None
    new_entry_dict = entry.m_to_dict()
    res = search_result.data[0]
    try:
        # Open Archives
        with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(entry_id=res['entry_id']) as ar:
            entry_id = res['entry_id']
            entry_data = ar[entry_id]['data']
            entry_data.pop('m_def', None)
            new_entry_dict.update(entry_data)
    except Exception:
        pass
        # logger.error('Error in processing data: ', e)
    print(type(entry).__name__)
    new_entry = getattr(sys.modules[__name__], type(entry).__name__).m_from_dict(new_entry_dict)
    return new_entry


class HySprintParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.
        file = mainfile.rsplit('raw/', maxsplit=1)[-1]
        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = '.'.join(mainfile_split[1:-2])
        measurment_type = mainfile_split[-2].lower()
        entry = HySprint_Measurement()

        if mainfile_split[-1].lower() == 'mpt' and measurment_type.lower() == 'hy':
            from nomad_hysprint.schema_packages.file_parser.mps_file_parser import read_mpt_file

            with open(mainfile) as f:
                metadata, _, technique = read_mpt_file(f)
            if 'Cyclic Voltammetry' in technique:
                entry = HySprint_CyclicVoltammetry()
            if 'Open Circuit Voltage' in technique:
                entry = HySprint_OpenCircuitVoltage()
            if 'Potentio Electrochemical Impedance Spectroscopy' in technique:
                entry = HySprint_ElectrochemicalImpedanceSpectroscopy()
        if mainfile_split[-1].lower() == 'csv' and measurment_type.lower() == 'hy':
            with open(mainfile) as f:
                file_content = f.read()
            if (
                'Experiment:' in file_content
                and 'Start date:' in file_content
                and ' Charge (C)' in file_content
            ):
                entry = HySprint_CyclicVoltammetry()
            if (
                'Experiment:' in file_content
                and 'Start date:' in file_content
                and 'Aux A (V)' in file_content
            ):
                entry = HySprint_OpenCircuitVoltage()
        if mainfile_split[-1].lower() == 'data' and measurment_type.lower() == 'hy':
            self._parse_xmstudio_hy_data(mainfile, file, archive, mainfile_split[0])
            return

        if mainfile_split[-1].lower() in ['txt', 'json'] and measurment_type.lower() == 'jv':
            entry = HySprint_JVmeasurement()
        if mainfile_split[-1].lower() == 'txt' and measurment_type.lower() == 'abspl':
            entry = HySprint_AbsPLMeasurement()
        if mainfile_split[-1].lower() == 'txt' and measurment_type.lower() in ['trspv', 'spv']:
            entry = HySprint_trSPVmeasurement()
        if mainfile_split[-1].lower() in ['txt', 'csv', 'dat'] and measurment_type.lower() in ['trpl']:
            entry = HySprint_TimeResolvedPhotoluminescence()
        if (
            mainfile_split[-1].lower() == 'txt' or mainfile_split[-1].upper() == 'TRQ'
        ) and measurment_type.lower() == 'eqe':
            entry = HySprint_EQEmeasurement()
        if mainfile_split[-1].lower() in ['tif', 'tiff'] and measurment_type.lower() == 'sem':
            entry = HySprint_SEM()
            entry.detector_data = [file]
        if measurment_type.lower() == 'pl':
            entry = HySprint_PLmeasurement()
        if measurment_type.lower() == 'pli':
            entry = HySprint_PLImaging()
        if measurment_type.lower() == 'xrd' and mainfile_split[-1].lower() == 'xy':
            entry = HySprint_XRD_XY()
        if measurment_type.lower() == 'nmr' and mainfile_split[-1].lower() == 'txt':
            entry = HySprint_Simple_NMR()
        if measurment_type.lower() == 'pes' and mainfile_split[-1].lower() in ['xy']:
            entry = HySprint_PES()
        if measurment_type == 'uvvis':
            entry = HySprint_UVvismeasurement()
            entry.data_file = [file]
        if mainfile_split[-1].lower() in ['txt'] and measurment_type.lower() == 'env':
            entry = HZB_EnvironmentMeasurement()
        if mainfile_split[-1].lower() in ['nk']:
            entry = HZB_NKData()
        if mainfile_split[-1].lower() in ['txt', 'csv'] and measurment_type.lower() == 'mppt':
            entry = HySprint_SimpleMPPTracking()
        archive.metadata.entry_name = file

        if mainfile_split[-1].lower() not in ['nk']:
            search_id = mainfile_split[0]
            set_sample_reference(archive, entry, search_id)

            entry.name = f'{search_id} {notes}'
            entry.description = f'Notes from file name: {notes}'

        if measurment_type not in ['uvvis', 'sem', 'SEM']:
            entry.data_file = file
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        file_name = f'{file}.archive.json'
        eid = get_entry_id_from_file_name(file_name, archive)
        archive.data = RawFileHZB(processed_archive=get_reference(archive.metadata.upload_id, eid))
        new_entry_created = create_archive(entry, archive, file_name)
        if not new_entry_created:
            new_entry = update_general_process_entries(entry, eid, archive, logger)
            if new_entry is not None:
                create_archive(new_entry, archive, file_name, overwrite=True)

    def _parse_xmstudio_hy_data(self, mainfile, file, archive, search_id):
        from baseclasses.chemical_energy.cyclicvoltammetry import CVProperties
        from baseclasses.chemical_energy.voltammetry import VoltammetryCycleWithPlot
        from nomad.units import ureg

        from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import (
            add_experiment_step_columns,
            extract_cv_data_by_scan_rate,
            extract_dpv_data,
            extract_impedance_data,
            extract_ocp_data,
            import_xmstudio_binary_data,
        )

        raw_df = add_experiment_step_columns(import_xmstudio_binary_data(Path(mainfile).read_bytes()))

        eis_df = extract_impedance_data(raw_df)
        if not eis_df.empty:
            eis_entry = HySprint_ElectrochemicalImpedanceSpectroscopy()
            eis_entry.name = f'{search_id} EIS'
            eis_entry.time = eis_df['time'].to_numpy() * ureg('s')
            eis_entry.frequency = eis_df['frequency'].to_numpy() * ureg('Hz')
            eis_entry.z_real = eis_df['z_real'].to_numpy() * ureg('ohm')
            eis_entry.z_imaginary = eis_df['z_imaginary'].to_numpy() * ureg('ohm')
            eis_entry.z_modulus = eis_df['z_modulus'].to_numpy() * ureg('ohm')
            eis_entry.z_angle = eis_df['z_angle'].to_numpy() * ureg('degree')
            set_sample_reference(archive, eis_entry, search_id, upload_id=archive.metadata.upload_id)
            create_archive(eis_entry, archive, f'{search_id}.eis.archive.json')

        dpv_df = extract_dpv_data(raw_df)
        if not dpv_df.empty:
            dpv_entry = HySprint_DifferentialPulseVoltammetry()
            dpv_entry.name = f'{search_id} DPV'
            dpv_entry.time = dpv_df['time'].to_numpy() * ureg('s')
            dpv_entry.voltage = dpv_df['voltage'].to_numpy() * ureg('V')
            dpv_entry.current = dpv_df['current'].to_numpy() * ureg('A')
            set_sample_reference(archive, dpv_entry, search_id, upload_id=archive.metadata.upload_id)
            create_archive(dpv_entry, archive, f'{search_id}.dpv.archive.json')

        ocp_df = extract_ocp_data(raw_df)
        if not ocp_df.empty:
            ocp_entry = HySprint_OpenCircuitVoltage()
            ocp_entry.name = f'{search_id} OCV'
            ocp_entry.time = ocp_df['time'].to_numpy() * ureg('s')
            ocp_entry.voltage = ocp_df['voltage'].to_numpy() * ureg('V')
            ocp_entry.current = ocp_df['current'].to_numpy() * ureg('A')
            set_sample_reference(archive, ocp_entry, search_id, upload_id=archive.metadata.upload_id)
            create_archive(ocp_entry, archive, f'{search_id}.ocv.archive.json')

        cv_by_rate = extract_cv_data_by_scan_rate(raw_df)
        if cv_by_rate:
            cv_entry = HySprint_CyclicVoltammetry()
            cv_entry.data_file = f'{search_id}.cv.archive.json'
            cv_entry.name = f'{search_id} CV'
            scan_rates = [sr for sr in cv_by_rate if isinstance(sr, float)]
            if len(scan_rates) == 1:
                cv_entry.properties = CVProperties()
                cv_entry.properties.scan_rate = scan_rates[0] * 1000 * ureg('mV/s')
            cycles = []
            for cv_group in cv_by_rate.values():
                for _, cyc in cv_group.groupby('cycle_number', dropna=True, sort=True):
                    cycles.append(
                        VoltammetryCycleWithPlot(
                            time=cyc['time'].to_numpy() * ureg('s'),
                            voltage=cyc['voltage'].to_numpy() * ureg('V'),
                            current=cyc['current'].to_numpy() * ureg('A'),
                        )
                    )
            cv_entry.cycles = cycles
            set_sample_reference(archive, cv_entry, search_id, upload_id=archive.metadata.upload_id)
            create_archive(cv_entry, archive, f'{search_id}.cv.archive.json')

        archive.metadata.entry_name = file
        archive.data = RawFileHZB()
