#!/usr/bin/env python3
"""
Created on Fri Sep 27 09:08:03 2024

@author: a2853
"""

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

import pandas as pd
from baseclasses.helper.solar_cell_batch_mapping import (
    get_reference,
    map_atomic_layer_deposition,
    map_basic_sample,
    map_batch,
    map_cleaning,
    map_evaporation,
    map_generic,
    map_inkjet_printing,
    map_laser_scribing,
    map_sdc,
    map_spin_coating,
    map_sputtering,
    map_substrate,
)
from baseclasses.helper.utilities import create_archive
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.basesections import (
    Entity,
)
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser

from nomad_hysprint.schema_packages.hysprint_package import (
    HySprint_Batch,
    HySprint_Cleaning,
    HySprint_Evaporation,
    HySprint_Inkjet_Printing,
    HySprint_LaserScribing,
    HySprint_Process,
    HySprint_Sample,
    HySprint_SlotDieCoating,
    HySprint_SpinCoating,
    HySprint_Sputtering,
    HySprint_Substrate,
    IRIS_AtomicLayerDeposition,
)

"""
This is a hello world style example for an example parser/converter.
"""


class RawHySprintExperiment(EntryData):
    processed_archive = Quantity(type=Entity, shape=['*'])


class HySprintExperimentParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ):
        is_mainfile_super = super().is_mainfile(
            filename, mime, buffer, decoded_buffer, compression
        )
        if not is_mainfile_super:
            return False
        try:
            df = pd.read_excel(filename, header=[0, 1])
            df['Experiment Info']['Nomad ID'].dropna().to_list()
        except Exception:
            return False
        return True

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        upload_id = archive.metadata.upload_id
        # xls = pd.ExcelFile(mainfile)
        df = pd.read_excel(mainfile, header=[0, 1])

        sample_ids = df['Experiment Info']['Nomad ID'].dropna().to_list()
        batch_id = '_'.join(sample_ids[0].split('_')[:-1])
        archives = [map_batch(sample_ids, batch_id, upload_id, HySprint_Batch)]
        substrates = []
        substrates_col = [
            'Sample dimension',
            'Sample area [cm^2]',
            'Substrate material',
            'Substrate conductive layer',
        ]
        for i, sub in (
            df['Experiment Info'][substrates_col].drop_duplicates().iterrows()
        ):
            if pd.isna(sub).all():
                continue
            substrates.append(
                (f'{i}_substrate', sub, map_substrate(sub, HySprint_Substrate))
            )

        def find_substrate(d):
            for s in substrates:
                if d.equals(s[1]):
                    return s[0]

        for i, row in df['Experiment Info'].iterrows():
            if pd.isna(row).all():
                continue
            substrate_name = (
                find_substrate(
                    row[
                        [
                            'Sample dimension',
                            'Sample area [cm^2]',
                            'Substrate material',
                            'Substrate conductive layer',
                        ]
                    ]
                )
                + '.archive.json'
            )
            archives.append(
                map_basic_sample(row, substrate_name, upload_id, HySprint_Sample)
            )

        for i, col in enumerate(df.columns.get_level_values(0).unique()):
            if col == 'Experiment Info':
                continue

            df_dropped = df[col].drop_duplicates()
            for j, row in df_dropped.iterrows():
                lab_ids = [
                    x['Experiment Info']['Nomad ID']
                    for _, x in df[['Experiment Info', col]].iterrows()
                    if x[col].astype('object').equals(row.astype('object'))
                ]
                if 'Cleaning' in col:
                    archives.append(
                        map_cleaning(i, j, lab_ids, row, upload_id, HySprint_Cleaning)
                    )

                if 'Laser Scribing' in col:
                    archives.append(
                        map_laser_scribing(
                            i, j, lab_ids, row, upload_id, HySprint_LaserScribing
                        )
                    )

                if 'Generic Process' in col:  # move up
                    archives.append(
                        map_generic(i, j, lab_ids, row, upload_id, HySprint_Process)
                    )

                if pd.isna(row.get('Material name')):
                    continue

                if 'Evaporation' in col:
                    archives.append(
                        map_evaporation(
                            i, j, lab_ids, row, upload_id, HySprint_Evaporation
                        )
                    )

                if 'Spin Coating' in col:
                    archives.append(
                        map_spin_coating(
                            i, j, lab_ids, row, upload_id, HySprint_SpinCoating
                        )
                    )

                if 'Slot Die Coating' in col:
                    archives.append(
                        map_sdc(i, j, lab_ids, row, upload_id, HySprint_SlotDieCoating)
                    )

                if 'Sputtering' in col:
                    archives.append(
                        map_sputtering(i, j, lab_ids, row, upload_id,
                                       HySprint_Sputtering)
                    )

                if 'Inkjet Printing' in col:
                    archives.append(
                        map_inkjet_printing(
                            i, j, lab_ids, row, upload_id, HySprint_Inkjet_Printing
                        )
                    )

                if 'ALD' in col:
                    archives.append(
                        map_atomic_layer_deposition(
                            i, j, lab_ids, row, upload_id, IRIS_AtomicLayerDeposition
                        )
                    )

        refs = []
        for subs in substrates:
            file_name = f'{subs[0]}.archive.json'
            create_archive(subs[2], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        for a in archives:
            file_name = f'{a[0]}.archive.json'
            create_archive(a[1], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        archive.data = RawHySprintExperiment(processed_archive=refs)
