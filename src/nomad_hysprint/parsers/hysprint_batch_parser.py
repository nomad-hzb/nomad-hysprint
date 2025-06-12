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
from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.solar_cell_batch_mapping import (
    get_reference,
    get_value,
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
from baseclasses.solution import SolutionChemical
from nomad.datamodel import EntryArchive
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import Entity
from nomad.metainfo import Quantity
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
    ProcessParameter,
)
from nomad_hysprint.schema_packages.ink_recycling_package import (
    InkRecycling_Filter,
    InkRecycling_FunctionalLiquid,
    InkRecycling_Ink,
    InkRecycling_RecyclingExperiment,
    InkRecycling_Results,
)

"""
This is a hello world style example for an example parser/converter.
"""


class RawHySprintExperiment(EntryData):
    processed_archive = Quantity(type=Entity, shape=['*'])


def map_generic_parameters(process, data):
    parameters = []
    for col, val in data.items():
        if col in ['Notes', 'Name']:
            continue
        try:
            val_float = float(val)
            parameters.append(ProcessParameter(name=col, value_number=val_float))
        except Exception:
            parameters.append(ProcessParameter(name=col, value_string=val))
    process.process_parameters = parameters


def map_ink(data):
    solvents = []
    solutes = []
    precursors = []
    for col in data.index:
        if col.lower().startswith('solvent'):
            solvents.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('solute'):
            solutes.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('precursor'):
            precursors.append(' '.join(col.split(' ')[:2]))

    final_solvents = []
    final_solutes = []
    final_precursors = []
    for solvent in sorted(set(solvents)):
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solvent} name', None, False),
                    load_data=False,
                ),
                chemical_volume=get_value(data, f'{solvent} volume [mL]', None, unit='mL'),
            )
        )

    for solute in sorted(set(solutes)):
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solute} name', None, False),
                    load_data=False,
                ),
                concentration_mol=get_value(data, f'{solute} concentration [M]', None, unit='M'),
                chemical_mass=get_value(data, f'{solute} amount [g]', None, unit='g'),
            )
        )
        # substance amount in mol
        # solute_mol = get_value(
        #    data, f'{solute} moles [mol]', None, unit='mol'),

    for precursor in sorted(set(precursors)):
        final_precursors.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{precursor} name', None, False),
                    load_data=False,
                ),
                # chemical_mass=get_value(
                #     data, f'{precursor} moles [mol]', None, unit='mol'
                # ),
            )
        )

    archive = InkRecycling_Ink(solvent=final_solvents, solute=final_solutes, precursor=final_precursors)
    return archive


def map_mixing(data):
    archive = InkRecycling_FunctionalLiquid(
        name=get_value(data, 'Functional liquid name', None, False),
        volume=get_value(data, 'Functional liquid volume [ml]', None, unit='mL'),
        dissolving_temperature=get_value(data, 'Dissolving temperature [°C]', None, unit='°C'),
    )
    return archive


def map_filtering(data):
    archive = InkRecycling_Filter(
        type=get_value(data, 'Filter material', None, False),
        size=get_value(data, 'Filter size [mm]', None, unit='mm'),
    )
    return archive


def map_results(data):
    archive = InkRecycling_Results(
        recovered_solute=get_value(data, 'Recovered solute [g]', None, unit='g'),
        yield_=get_value(data, 'Yield [%]', None, True),
    )
    return archive


class HySprintExperimentParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ):
        is_mainfile_super = super().is_mainfile(filename, mime, buffer, decoded_buffer, compression)
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
        df['Experiment Info']['Nomad ID'].dropna().to_list()
        sample_ids = df['Experiment Info']['Nomad ID'].dropna().to_list()
        batch_id = '_'.join(sample_ids[0].split('_')[:-1])

        batch = map_batch(sample_ids, batch_id, upload_id, HySprint_Batch)
        archives = [batch]

        is_ink_recycling = False
        columns = df.columns.get_level_values(0).unique()
        if any('Ink' in col for col in columns):
            is_ink_recycling = True
        if not is_ink_recycling:
            substrates = []
            substrates_col = [
                'Sample dimension',
                'Sample area [cm^2]',
                'Pixel area [cm^2]',
                'Number of pixels',
                'Notes',
                'Substrate material',
                'Substrate conductive layer',
            ]
            substrates_col = [s for s in substrates_col if s in df['Experiment Info'].columns]
            for i, sub in df['Experiment Info'][substrates_col].drop_duplicates().iterrows():
                if pd.isna(sub).all():
                    continue
                substrates.append((f'{i}_substrate', sub, map_substrate(sub, HySprint_Substrate)))

            def find_substrate(d):
                for s in substrates:
                    if d.equals(s[1]):
                        return s[0]

            for i, row in df['Experiment Info'].iterrows():
                if pd.isna(row).all():
                    print(f'Skipping empty experiment info row {i}')
                    continue
                substrate_name = find_substrate(row[substrates_col]) + '.archive.json'
                archives.append(map_basic_sample(row, substrate_name, upload_id, HySprint_Sample))

        if is_ink_recycling:
            # For ink workflow, process the entire dataframe row by row
            for i, row in df.iterrows():
                ink_recycling_archive = InkRecycling_RecyclingExperiment()

                # Process each column for this row
                for j, col in enumerate(df.columns.get_level_values(0).unique()):
                    if col == 'Experiment Info':
                        ink_exp_id = row[col]['Nomad ID']

                    if 'Ink Preparation' in col:
                        ink_preparation = map_ink(row[col])
                        ink_recycling_archive.ink = ink_preparation

                    if 'Mixing' in col:
                        mixing = map_mixing(row[col])
                        ink_recycling_archive.FL = mixing

                    if 'Filtering' in col:
                        filtering = map_filtering(row[col])
                        ink_recycling_archive.filter = filtering

                    if 'Results' in col:
                        recycling_results = map_results(row[col])
                        ink_recycling_archive.recycling_results = recycling_results

                archives.append((f'{ink_exp_id}_ink_recycling', ink_recycling_archive))

        else:
            # Original workflow for non-ink cases, process column by column
            for i, col in enumerate(df.columns.get_level_values(0).unique()):
                if col == 'Experiment Info':
                    continue
                # Original workflow for non-ink cases
                df_dropped = df[col].drop_duplicates()
                for j, row in df_dropped.iterrows():
                    lab_ids = [
                        x['Experiment Info']['Nomad ID']
                        for _, x in df[['Experiment Info', col]].iterrows()
                        if x[col].astype('object').equals(row.astype('object'))
                    ]

                    if 'Cleaning' in col:
                        archives.append(map_cleaning(i, j, lab_ids, row, upload_id, HySprint_Cleaning))

                    if 'Laser Scribing' in col:
                        archives.append(
                            map_laser_scribing(i, j, lab_ids, row, upload_id, HySprint_LaserScribing)
                        )

                    if 'Generic Process' in col:  # move up
                        generic_process = map_generic(i, j, lab_ids, row, upload_id, HySprint_Process)
                        map_generic_parameters(generic_process[1], row)
                        archives.append(generic_process)

                    if pd.isna(row.get('Material name')):
                        continue

                    if 'Evaporation' in col:
                        archives.append(map_evaporation(i, j, lab_ids, row, upload_id, HySprint_Evaporation))

                    if 'Spin Coating' in col:
                        archives.append(map_spin_coating(i, j, lab_ids, row, upload_id, HySprint_SpinCoating))

                    if 'Slot Die Coating' in col:
                        archives.append(map_sdc(i, j, lab_ids, row, upload_id, HySprint_SlotDieCoating))

                    if 'Sputtering' in col:
                        archives.append(map_sputtering(i, j, lab_ids, row, upload_id, HySprint_Sputtering))

                    if 'Inkjet Printing' in col:
                        archives.append(
                            map_inkjet_printing(i, j, lab_ids, row, upload_id, HySprint_Inkjet_Printing)
                        )

                    if 'ALD' in col:
                        archives.append(
                            map_atomic_layer_deposition(
                                i, j, lab_ids, row, upload_id, IRIS_AtomicLayerDeposition
                            )
                        )

        refs = []

        if not is_ink_recycling:
            for subs in substrates:
                file_name = f'{subs[0]}.archive.json'
                create_archive(subs[2], archive, file_name)
                refs.append(get_reference(upload_id, file_name))

        for a in archives:
            file_name = f'{a[0]}.archive.json'
            create_archive(a[1], archive, file_name)
            refs.append(get_reference(upload_id, file_name))

        archive.data = RawHySprintExperiment(processed_archive=refs)
