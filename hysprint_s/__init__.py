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

from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
import os
import random
import string

from nomad.metainfo import (
    Quantity,
    Package,
    Section,
    MSection,
    SubSection,
)

import numpy as np
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from baseclasses import (
    BaseProcess, BaseMeasurement, LayerDeposition, Batch, ReadableIdentifiersCustom
)
from baseclasses.assays import (
    EnvironmentMeasurement,
)
from baseclasses.chemical import (
    Chemical
)
from baseclasses.chemical_energy import (
    Electrode,
    ElectroChemicalSetup, Environment
)
from baseclasses.data_transformations import NKData
from baseclasses.experimental_plan import ExperimentalPlan
from baseclasses.material_processes_misc import (
    Cleaning,
    SolutionCleaning,
    PlasmaCleaning,
    UVCleaning,
    LaserScribing,
    Storage)
from baseclasses.solar_energy import (
    StandardSampleSolarCell, SolarCellProperties,
    Substrate,
    TimeResolvedPhotoluminescence,
    JVMeasurement,
    trSPVMeasurement,
    PLMeasurement, PLImaging,
    UVvisMeasurement,
    EQEMeasurement,
    OpticalMicroscope,
    SolcarCellSample, BasicSampleWithID,
    MPPTrackingHsprintCustom
)
from baseclasses.solution import Solution, Ink, SolutionPreparationStandard
from baseclasses.vapour_based_deposition import (
    Evaporations,
    AtomicLayerDeposition,
    Sputtering)
from baseclasses.wet_chemical_deposition import (
    SpinCoating,
    SpinCoatingRecipe,
    SlotDieCoating, DipCoating, BladeCoating,
    LP50InkjetPrinting,
    VaporizationAndDropCasting,
    SprayPyrolysis,
    WetChemicalDeposition,
    Crystallization)
from nomad.datamodel.data import EntryData
from nomad.datamodel.results import Results, Properties, Material, ELN
from nomad.units import ureg
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section)

from baseclasses.voila import (
    VoilaNotebook
)

m_package = Package(name='HySprint')


# %% ####################### Entities


def randStr(chars=string.ascii_uppercase + string.digits, N=6):
    return ''.join(random.choice(chars) for _ in range(N))


class HySprint_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id'])
    )

    def normalize(self, archive, logger):
        super(HySprint_VoilaNotebook, self).normalize(archive, logger)


class HySprint_ExperimentalPlan(ExperimentalPlan, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users'],
                   properties=dict(
                       order=[
                           "name",
                           "standard_plan",
                           "load_standard_processes",
                           "create_samples_and_processes",
                           "number_of_substrates",
                           "substrates_per_subbatch",
                           "lab_id"
                       ])),
        a_template=dict(institute="HZB_Hysprint"))

    solar_cell_properties = SubSection(
        section_def=SolarCellProperties)

    def normalize(self, archive, logger):
        super(HySprint_ExperimentalPlan, self).normalize(archive, logger)

        from baseclasses.helper.execute_solar_sample_plan import execute_solar_sample_plan
        execute_solar_sample_plan(self, archive, HySprint_Sample, HySprint_Batch, logger)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ["HySprint_ExperimentalPlan"]


class HySprint_StandardSample(StandardSampleSolarCell, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "architecture",
                    "substrate",
                    "processes",
                    "lab_id"
                ])))


class HySprint_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class HySprint_Chemical(Chemical, EntryData):
    m_def = Section(
        a_eln=dict(hide=['lab_id', 'users']))


class Hysprint_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition', 'origin'],
                   properties=dict(
                       order=[
                           "name", "lab_id",
                           "chemical_composition_or_formulas"
                       ]))
    )


class HySprint_ElectroChemicalSetup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition', 'origin'],
                   properties=dict(
                       order=[
                           "name",
                           "lab_id",
                           "chemical_composition_or_formulas",
                           "setup",
                           "reference_electrode",
                           "counter_electrode",
                       ])),
    )

    setup_id = SubSection(
        section_def=ReadableIdentifiersCustom)


class HySprint_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition',
                'origin'],
            properties=dict(
                editable=dict(
                    exclude=["chemical_composition_or_formulas"]),
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "ph_value",
                    "solvent"])))

    environment_id = SubSection(
        section_def=ReadableIdentifiersCustom)


class HySprint_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users', 'components', 'elemental_composition'],
            properties=dict(
                order=[
                    "name",
                    "substrate",
                    "conducting_material",
                    "solar_cell_area",
                    "pixel_area",
                    "number_of_pixels"])))


class HySprint_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition', "method", "temperature", "time", "speed",
                "solvent_ratio", "washing"],
            properties=dict(
                order=[
                    "name",
                    "datetime",
                    "lab_id",
                    "description", "preparation", "solute", "solvent", "other_solution", "additive", "storage"
                ],
            )),
        a_template=dict(
            temperature=45,
            time=15,
            method='Shaker'))

    preparation = SubSection(section_def=SolutionPreparationStandard)

    # def normalize(self, archive, logger):
    #     super(HySprint_Solution, self).normalize(archive, logger)
    #     print(Solution.schema())


class HySprint_Ink(Ink, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition',
                'chemical_formula'],
            properties=dict(
                order=[
                    "name",
                    "method",
                    "temperature",
                    "time",
                    "speed",
                    "solvent_ratio"])),
        a_template=dict(
            temperature=45,
            time=15,
            method='Shaker'))


class HySprint_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition'], properties=dict(
            order=["name", "substrate", "architecture"])),
        a_template=dict(institute="HZB_Hysprint"),
        label_quantity='sample_id'
    )


class HySprint_BasicSample(BasicSampleWithID, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition']),
        a_template=dict(institute="HZB_Hysprint"),
        label_quantity='sample_id'
    )


class HySprint_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(
                order=[
                    "name",
                    "export_batch_ids",
                    "csv_export_file"])))


# class HySprint_BasicBatch(Batch, EntryData):
#     m_def = Section(
#         a_eln=dict(
#             hide=['users'],
#             properties=dict(
#                 order=[
#                     "name",
#                     "samples",
#                     "number_of_samples",
#                     "create_samples",
#                     "export_batch_ids",
#                     "csv_export_file"])))

#     number_of_samples = Quantity(
#         type=np.dtype(np.int64),
#         default=0,
#         a_eln=dict(
#             component='NumberEditQuantity'
#         ))

#     create_samples = Quantity(
#         type=bool,
#         default=False,
#         a_eln=dict(component='BoolEditQuantity')
#     )

#     def normalize(self, archive, logger):
#         super(HySprint_BasicBatch, self).normalize(archive, logger)

#         if self.number_of_samples > 0 and self.create_samples:
#             self.create_samples = False
#             samples = []
#             from baseclasses.helper.execute_solar_sample_plan import create_archive, get_entry_id_from_file_name, get_reference
#             sample_name_id = self.batch_id.sample_short_name if self.batch_id is not None else None
#             for sample_idx in range(self.number_of_samples):
#                 hysprint_basicsample = HySprint_BasicSample(
#                     sample_id=self.batch_id if self.batch_id is not None else None,
#                     datetime=self.datetime if self.datetime is not None else None,
#                     description=self.description if self.description is not None else None,
#                     name=f'{self.name} {sample_idx}' if self.name is not None else None,
#                 )
#                 hysprint_basicsample.sample_id.sample_short_name = f'{sample_name_id}_{sample_idx}'

#                 file_name = f'{self.name.replace(" ","_")}_{sample_idx}.archive.json'
#                 create_archive(hysprint_basicsample, archive, file_name)
#                 if sample_name_id is not None:
#                     self.batch_id.sample_short_name = sample_name_id
#                 entry_id = get_entry_id_from_file_name(file_name, archive)

#                 samples.append(get_reference(
#                     archive.metadata.upload_id, entry_id))
#             self.samples = []
#             self.samples = samples

# %% ####################### Cleaning


class HySprint_BasicCrystallization(Crystallization, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results', 'batch', "present", "positon_in_experimental_plan"],
            properties=dict(
                order=[
                    "name", "location",
                    "datetime",
                    "samples"])))


# %% ####################### Cleaning
class HySprint_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['HySprint', 'IRIS Printerlab', 'IRIS Preparationlab'])
        ))

    cleaning = SubSection(
        section_def=SolutionCleaning, repeats=True)

    cleaning_uv = SubSection(
        section_def=UVCleaning, repeats=True)

    cleaning_plasma = SubSection(
        section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition
class HySprint_SprayPyrolysis(SprayPyrolysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "properties",
                    "quenching",
                    "annealing"])))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['HySprint HTFumeHood'])
        ))


# %% ### Dropcasting


class HySprint_VaporizationAndDropCasting(
        VaporizationAndDropCasting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results',
                'previous_process'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "properties",
                    "quenching",
                    "annealing"])),
        a_template=dict(
            layer_type="Non-functional layer",
        ))


# %% ### Printing


class HySprint_Inkjet_Printing(
        LP50InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "recipe_used", "print_head_used",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "properties",
                    "print_head_path",
                    "nozzle_voltage_profile",
                    "quenching",
                    "annealing"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['IRIS HZBGloveBoxes Pero3Inkjet'])
        ))


# %% ### Spin Coating
class HySprint_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results', 'recipe'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "recipe"
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['HySprint HyFlowBox', 'HySprint HyPeroSpin', 'HySprint HySpin', 'HySprint ProtoVap',
                             'IRIS HZBGloveBoxes Pero2Spincoater'])
        ))


# %% ### Dip Coating


class HySprint_DipCoating(DipCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])),
        a_template=dict(
            layer_type="Absorber Layer",
        ))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['HySprint'])
        ))


class HySprint_BladeCoating(BladeCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])))

# %% ### Slot Die Coating


class HySprint_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "properties",
                    "quenching",
                    "annealing"
                ])),
        a_template=dict(
            layer_type="Absorber Layer"))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['HySprint HySDC'])
        ))


# %% ### Sputterring
class HySprint_Sputtering(
        Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples", "layer"])))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['IRIS', 'HySprint'])
        ))


# %% ### AtomicLayerDepositio
class HySprint_AtomicLayerDeposition(
        AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples", "layer"])))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['IRIS', 'HySprint'])
        ))


# %% ### Evaporation
class HySprint_Evaporation(
        Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples", "layer"])))

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['IRIS HZBGloveBoxes Pero5Evaporation', 'HySprint HyVap', 'HySprint HyPeroVap',
                             'HySprint ProtoVap'])
        ))


# %% ## Laser Scribing
class HySprint_LaserScribing(LaserScribing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime",
                    "batch",
                    "samples"])))


# %% ## Storage


class HySprint_Storage(Storage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "location",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples"])))


# %%####################################### Measurements
class HZB_EnvironmentMeasurement(EnvironmentMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time', 'steps', 'instruments', 'results',
                'location'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                "label": "Temperature Sensors", 'x': 'data/time', 'y': 'data/temperature_sensors/:/temperature',
                'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}},
            {
                "label": "Environment", 'x': 'data/time', 'y': ['data/humidity', 'data/temperature'], 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}]
    )

    def normalize(self, archive, logger):
        if self.data_file and self.data is None:  # and self.properties is None:
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.environment_parser import get_environment_data
                from baseclasses.helper.archive_builder.environment_archive import get_environment_archive

                env_data = get_environment_data(f.name, encoding)
                get_environment_archive(env_data, self)
        super(HZB_EnvironmentMeasurement, self).normalize(archive, logger)


class HySprint_trSPVmeasurement(trSPVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time', 'steps', 'instruments', 'results',
                'location'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "active_area",
                    "intensity",
                    "integration_time",
                    "settling_time",
                    "averaging",
                    "compliance",
                    "samples"])),
        a_plot=[
            {
                "label": "Voltage", 'x': 'data/time', 'y': 'data/voltages/:/voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False, 'type': 'log'}}, "config": {
                    "editable": True, "scrollZoom": True}}]
    )

    def normalize(self, archive, logger):
        if self.data_file and self.data is None and self.properties is None:
            # todo detect file format
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.spv_parser import get_spv_data
                from baseclasses.helper.archive_builder.spv_archive import get_spv_archive

                spv_dict, spv_data = get_spv_data(f.name, encoding)
                get_spv_archive(spv_dict, spv_data, f.name, self)
        super(HySprint_trSPVmeasurement,
              self).normalize(archive, logger)


class HySprint_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time', 'steps', 'instruments', 'results',
            ],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "active_area",
                    "intensity",
                    "integration_time",
                    "settling_time",
                    "averaging",
                    "compliance",
                    "samples"])),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file:
            # todo detect file format
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.jv_parser import get_jv_data
                from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

                jv_dict, location = get_jv_data(f.name, encoding)
                self.location = location
                get_jv_archive(jv_dict, self.data_file, self)

        super(HySprint_JVmeasurement,
              self).normalize(archive, logger)


class HySprint_MPPTracking(MPPTrackingHsprintCustom, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'author',
                'end_time', 'steps', 'instruments', 'results',
                'location', 'figures'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "active_area",
                    "intensity",
                    "integration_time",
                    "settling_time",
                    "averaging",
                    "compliance",
                    "samples"]))
    )

    def normalize(self, archive, logger):
        if self.data_file and self.load_data_from_file:
            self.load_data_from_file = False
            from baseclasses.helper.utilities import rewrite_json
            rewrite_json(["data", "load_data_from_file"], archive, False)

            # from baseclasses.helper.utilities import get_encoding
            # with archive.m_context.raw_file(self.data_file, "br") as f:
            #     encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding="ascii") as f:
                if os.path.splitext(f.name)[-1] != ".csv":
                    return
                from baseclasses.helper.file_parser.load_mpp_hysprint import load_mpp_file
                data = load_mpp_file(f.name)  # , encoding)

            from baseclasses.helper.archive_builder.mpp_hysprint_archive import get_mpp_hysprint_samples
            self.samples = get_mpp_hysprint_samples(self, data)
        import plotly.express as px
        import pandas as pd
        column_names = ["Time [hr]", "Efficiency [%]", "P"]
        self.figures = []
        if self.averages:
            fig = px.scatter()
            df = pd.DataFrame(columns=column_names)
            for avg in self.averages:
                df1 = pd.DataFrame(columns=column_names)
                df1[column_names[0]] = avg.time * ureg("hr")
                df1[column_names[1]] = avg.efficiency
                df1[column_names[2]] = avg.name
                df = pd.concat([df, df1])

            fig = px.scatter(df, x=column_names[0], y=column_names[1],
                             color=column_names[2], symbol=column_names[2], title="Averages")
            fig.update_traces(marker=dict(size=4))
            fig.update_layout(showlegend=True, xaxis=dict(fixedrange=False), yaxis=dict(fixedrange=False))
            self.figures.append(PlotlyFigure(label='Averages', index=0, figure=fig.to_plotly_json()))

        if self.best_pixels:
            df = pd.DataFrame(columns=column_names)
            for bp in self.best_pixels:
                df1 = pd.DataFrame(columns=column_names)
                df1[column_names[0]] = bp.time * ureg("hr")
                df1[column_names[1]] = bp.efficiency
                df1[column_names[2]] = bp.name
                df = pd.concat([df, df1])

            fig = px.scatter(df, x=column_names[0], y=column_names[1],
                             color=column_names[2], symbol=column_names[2], title="Best Pixels")
            fig.update_traces(marker=dict(size=4))
            fig.update_layout(showlegend=True, xaxis=dict(fixedrange=False), yaxis=dict(fixedrange=False))
            self.figures.append(PlotlyFigure(label='Best Pixel', index=1, figure=fig.to_plotly_json()))

        super(HySprint_MPPTracking,
              self).normalize(archive, logger)


class HySprint_TimeResolvedPhotoluminescence(
        TimeResolvedPhotoluminescence, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])),
        a_plot=[
            {
                'x': 'trpl_properties/:/time',
                'y': 'trpl_properties/:/counts',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False,
                        'type': 'log'},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data_file is not None:
            # if self.trpl_properties is not None:
            #     return
            trpl_properties_list = []
            for data_file in self.data_file:
                # todo detect file format
                if os.path.splitext(data_file)[-1] not in [".txt", ".dat"]:
                    continue

                from baseclasses.helper.utilities import get_encoding
                with archive.m_context.raw_file(self.data_file, "br") as f:
                    encoding = get_encoding(f)

                with archive.m_context.raw_file(data_file, encoding=encoding) as f:
                    from baseclasses.helper.file_parser.trpl_parser import get_trpl_measurement
                    data = get_trpl_measurement(f)

                from baseclasses.helper.archive_builder.trpl_archive import get_trpl_archive
                trpl_properties_list.append(get_trpl_archive(data, data_file))
            self.trpl_properties = trpl_properties_list
        super(HySprint_TimeResolvedPhotoluminescence,
              self).normalize(archive, logger)


class HySprint_OpticalMicroscope(
        OpticalMicroscope, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'detector_data_folder',
                'external_sample_url',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])),
    )


class HySprint_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'solution',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results', "eqe_data"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])),
        a_plot=[
            {
                'x': 'data/photon_energy_array',
                'y': 'data/eqe_array',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        if self.data is not None and self.data.eqe_data_file is not None and self.data.header_lines is not None:
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data.eqe_data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data.eqe_data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.eqe_parser import read_file
                photon_energy_raw, eqe_raw, photon_energy, eqe = read_file(f.name, self.data.header_lines)
                self.data.photon_energy_array = np.array(photon_energy)
                self.data.raw_photon_energy_array = np.array(photon_energy_raw)
                self.data.eqe_array = np.array(eqe)
                self.data.raw_eqe_array = np.array(eqe_raw)
            self.data.normalize(archive, logger)

        super(HySprint_EQEmeasurement, self).normalize(archive, logger)


class HySprint_PLmeasurement(PLMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])),
        a_plot=[
            {
                'x': 'data/wavelength',
                'y': 'data/intensity',
                'layout': {
                    "showlegend": True,
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.data_file and os.path.getsize(os.path.join(path, self.data_file)) < 1e7:
            # todo detect file format
            from baseclasses.helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                from baseclasses.helper.file_parser.pl_parser import get_pl_data
                from baseclasses.helper.archive_builder.pl_archive import get_pl_archive

                pl_dict, location = get_pl_data(f.name, encoding)
                self.location = location
                if pl_dict is not None:
                    get_pl_archive(pl_dict, self.data_file, self)

        super(HySprint_PLmeasurement, self).normalize(archive, logger)


class HySprint_PLImaging(PLImaging, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results', "solution"],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples"])))


class HySprint_UVvismeasurement(UVvisMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])))

    def normalize(self, archive, logger):
        measurements = []
        for data_file in self.data_file:
            if os.path.splitext(data_file)[-1] not in [".txt", ".csv"]:
                continue
            with archive.m_context.raw_file(data_file) as f:
                if os.path.splitext(data_file)[-1] == ".txt":
                    from baseclasses.helper.file_parser.uvvis_parser import get_uvvis_measurement_txt
                    data, datetime_object = get_uvvis_measurement_txt(f)

                if os.path.splitext(data_file)[-1] == ".csv":
                    from baseclasses.helper.file_parser.uvvis_parser import get_uvvis_measurement_csv
                    data, datetime_object = get_uvvis_measurement_csv(f)

            from baseclasses.helper.archive_builder.uvvis_archive import get_uvvis_archive
            measurements.append(get_uvvis_archive(
                data, datetime_object, data_file))
        self.measurements = measurements

        super(HySprint_UVvismeasurement,
              self).normalize(archive, logger)


# %%####################################### Data Transformations
class HZB_NKData(NKData, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location', "datetime",
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name", "data_file", "data_reference", "chemical_composition_or_formulas", "reference"
                ])))

    def normalize(self, archive, logger):
        from baseclasses.helper.utilities import get_encoding
        with archive.m_context.raw_file(self.data_file, "br") as f:
            encoding = get_encoding(f)

        with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
            from baseclasses.helper.file_parser.nk_parser import get_nk_data
            from baseclasses.helper.archive_builder.nk_archive import get_nk_archive

            nk_data, metadata = get_nk_data(f.name, encoding)

        self.description = metadata["Comment"] if "Comment" in metadata else ""
        self.chemical_composition_or_formulas = metadata["Formula"] if "Formula" in metadata else ""
        self.name = metadata["Name"] if "Name" in metadata else ""
        doi = metadata["Reference"] if "Reference" in metadata else ""
        if doi.startswith("doi:"):
            doi = doi.strip("doi:")
            doi = "https://doi.org/" + doi
        self.data_reference = doi
        self.name = metadata["Name"] if "Name" in metadata else ""
        self.data = get_nk_archive(nk_data)

        super(HZB_NKData, self).normalize(archive, logger)


# %%####################################### Generic Entries


class HySprint_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "data_file",
                    "batch",
                    "samples"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class HySprint_WetChemicalDepoistion(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "solution",
                    "layer",
                    "quenching",
                    "annealing"])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class HySprint_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "present",
                    "datetime", "previous_process",
                    "batch",
                    "samples",
                    "layer"
                ])))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


class HySprint_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    "name",
                    "data_file",
                    "samples", "solution"])))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))


m_package.__init_metainfo__()
