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

from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    set_sample_reference,
)
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.basesections import (
    Activity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_hysprint.schema_packages.hysprint_package import (
    HySprint_CyclicVoltammetry,
    HySprint_ElectrochemicalImpedanceSpectroscopy,
    HySprint_EQEmeasurement,
    HySprint_JVmeasurement,
    HySprint_Measurement,
    HySprint_OpenCircuitVoltage,
    HySprint_PLImaging,
    HySprint_PLmeasurement,
    HySprint_SEM,
    HySprint_SimpleMPPTracking,
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

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = '.'.join(mainfile_split[1:-2])
        measurment_type = mainfile_split[-2].lower()
        entry = HySprint_Measurement()
        if mainfile_split[-1] == 'mpt' and measurment_type == 'hy':
            from nomad_hysprint.schema_packages.file_parser.mps_file_parser import (
                read_mpt_file,
            )

            with open(mainfile) as f:
                metadata, _, technique = read_mpt_file(f)
            if 'Cyclic Voltammetry' in technique:
                entry = HySprint_CyclicVoltammetry()
            if 'Open Circuit Voltage' in technique:
                entry = HySprint_OpenCircuitVoltage()
            if 'Potentio Electrochemical Impedance Spectroscopy' in technique:
                entry = HySprint_ElectrochemicalImpedanceSpectroscopy()
        if mainfile_split[-1] == 'csv' and measurment_type == 'hy':
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
        if mainfile_split[-1] == 'txt' and measurment_type == 'jv':
            entry = HySprint_JVmeasurement()
        if mainfile_split[-1] == 'txt' and measurment_type == 'spv':
            entry = HySprint_trSPVmeasurement()
        if mainfile_split[-1] == 'txt' and measurment_type == 'eqe':
            entry = HySprint_EQEmeasurement()
        if mainfile_split[-1] in ['tif', 'tiff'] and measurment_type.lower() == 'sem':
            entry = HySprint_SEM()
            entry.detector_data = [os.path.basename(mainfile)]
        if measurment_type == 'pl':
            entry = HySprint_PLmeasurement()
        if measurment_type == 'pli':
            entry = HySprint_PLImaging()
        if measurment_type == 'xrd' and mainfile_split[-1] == 'xy':
            entry = HySprint_XRD_XY()
        if measurment_type == 'uvvis':
            entry = HySprint_UVvismeasurement()
            entry.data_file = [os.path.basename(mainfile)]
        if mainfile_split[-1] in ['txt'] and measurment_type == 'env':
            entry = HZB_EnvironmentMeasurement()
        if mainfile_split[-1] in ['nk']:
            entry = HZB_NKData()
        if mainfile_split[-1] in ['txt'] and measurment_type == 'mppt':
            entry = HySprint_SimpleMPPTracking()
        archive.metadata.entry_name = os.path.basename(mainfile)

        if mainfile_split[-1] not in ['nk']:
            search_id = mainfile_split[0]
            set_sample_reference(archive, entry, search_id)

            entry.name = f'{search_id} {notes}'
            entry.description = f'Notes from file name: {notes}'

        if measurment_type not in ['uvvis', 'sem', 'SEM']:
            entry.data_file = os.path.basename(mainfile)
        entry.datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        eid = get_entry_id_from_file_name(file_name, archive)
        archive.data = RawFileHZB(processed_archive=get_reference(archive.metadata.upload_id, eid))
        new_entry_created = create_archive(entry, archive, file_name)
        if not new_entry_created:
            new_entry = update_general_process_entries(entry, eid, archive, logger)
            if new_entry is not None:
                create_archive(new_entry, archive, file_name, overwrite=True)
