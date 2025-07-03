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

import os
import random
import string

import numpy as np
from baseclasses import BaseMeasurement, BaseProcess, Batch, LayerDeposition, ReadableIdentifiersCustom
from baseclasses.assays import EnvironmentMeasurement
from baseclasses.characterizations import XPS, XRD, XPSSpecsLabProdigySettings, XRDData
from baseclasses.characterizations.electron_microscopy import SEM_Microscope_Merlin
from baseclasses.chemical import Chemical
from baseclasses.chemical_energy import (
    CyclicVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    ElectroChemicalSetup,
    Electrode,
    Environment,
    OpenCircuitVoltage,
)
from baseclasses.data_transformations import NKData
from baseclasses.experimental_plan import ExperimentalPlan
from baseclasses.helper.add_solar_cell import add_band_gap
from baseclasses.helper.utilities import convert_datetime, get_encoding, set_sample_reference
from baseclasses.material_processes_misc import (
    Cleaning,
    LaserScribing,
    PlasmaCleaning,
    SolutionCleaning,
    Storage,
    UVCleaning,
)
from baseclasses.solar_energy import (
    BasicSampleWithID,
    EQEMeasurement,
    JVMeasurement,
    MPPTracking,
    MPPTrackingHsprintCustom,
    MPPTrackingProperties,
    OpticalMicroscope,
    PLImaging,
    PLMeasurement,
    SolarCellEQECustom,
    SolarCellProperties,
    SolcarCellSample,
    StandardSampleSolarCell,
    Substrate,
    TimeResolvedPhotoluminescence,
    UVvisMeasurement,
    trSPVMeasurement,
)
from baseclasses.solution import Ink, Solution, SolutionPreparationStandard
from baseclasses.vapour_based_deposition import (
    ALDPropertiesIris,
    AtomicLayerDeposition,
    Evaporations,
    Sputtering,
)
from baseclasses.voila import VoilaNotebook
from baseclasses.wet_chemical_deposition import (
    BladeCoating,
    Crystallization,
    DipCoating,
    LP50InkjetPrinting,
    SlotDieCoating,
    SpinCoating,
    SpinCoatingRecipe,
    SprayPyrolysis,
    VaporizationAndDropCasting,
    WetChemicalDeposition,
)
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.hdf5 import HDF5Reference
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import ELN, Material, Properties, Results
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection
from nomad.units import ureg
from pynxtools.dataconverter.convert import convert

m_package = SchemaPackage()


# %% ####################### Entities


def randStr(chars=string.ascii_uppercase + string.digits, N=6):
    return ''.join(random.choice(chars) for _ in range(N))


class HySprint_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class HySprint_ExperimentalPlan(ExperimentalPlan, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(
                order=[
                    'name',
                    'standard_plan',
                    'load_standard_processes',
                    'create_samples_and_processes',
                    'number_of_substrates',
                    'substrates_per_subbatch',
                    'lab_id',
                ]
            ),
        ),
        a_template=dict(institute='HZB_Hysprint'),
    )

    solar_cell_properties = SubSection(section_def=SolarCellProperties)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        from baseclasses.helper.execute_solar_sample_plan import execute_solar_sample_plan

        execute_solar_sample_plan(self, archive, HySprint_Sample, HySprint_Batch, logger)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ['HySprint_ExperimentalPlan']


class HySprint_StandardSample(StandardSampleSolarCell, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users'],
            properties=dict(order=['name', 'architecture', 'substrate', 'processes', 'lab_id']),
        )
    )


class HySprint_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users']))


class HySprint_Chemical(Chemical, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id', 'users']))


class Hysprint_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'origin'],
            properties=dict(order=['name', 'lab_id', 'chemical_composition_or_formulas']),
        )
    )


class HySprint_ElectroChemicalSetup(ElectroChemicalSetup, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'origin'],
            properties=dict(
                order=[
                    'name',
                    'lab_id',
                    'chemical_composition_or_formulas',
                    'setup',
                    'reference_electrode',
                    'counter_electrode',
                ]
            ),
        ),
    )

    setup_id = SubSection(section_def=ReadableIdentifiersCustom)


class HySprint_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'origin'],
            properties=dict(
                editable=dict(exclude=['chemical_composition_or_formulas']),
                order=[
                    'name',
                    'lab_id',
                    'chemical_composition_or_formulas',
                    'ph_value',
                    'solvent',
                ],
            ),
        )
    )

    environment_id = SubSection(section_def=ReadableIdentifiersCustom)


class HySprint_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'components', 'elemental_composition'],
            properties=dict(
                order=[
                    'name',
                    'substrate',
                    'conducting_material',
                    'solar_cell_area',
                    'pixel_area',
                    'number_of_pixels',
                ]
            ),
        )
    )


class HySprint_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'components',
                'elemental_composition',
                'method',
                'temperature',
                'time',
                'speed',
                'solvent_ratio',
                'washing',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'description',
                    'preparation',
                    'solute',
                    'solvent',
                    'other_solution',
                    'additive',
                    'storage',
                ],
            ),
        ),
        a_template=dict(temperature=45, time=15, method='Shaker'),
    )

    preparation = SubSection(section_def=SolutionPreparationStandard)

    # def normalize(self, archive, logger):
    #     super(HySprint_Solution, self).normalize(archive, logger)
    #     print(Solution.schema())


class HySprint_Ink(Ink, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition', 'chemical_formula'],
            properties=dict(
                order=[
                    'name',
                    'method',
                    'temperature',
                    'time',
                    'speed',
                    'solvent_ratio',
                ]
            ),
        ),
        a_template=dict(temperature=45, time=15, method='Shaker'),
    )


class HySprint_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition'],
            properties=dict(order=['name', 'substrate', 'architecture']),
        ),
        a_template=dict(institute='HZB_Hysprint'),
        label_quantity='sample_id',
    )


class HySprint_BasicSample(BasicSampleWithID, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition']),
        a_template=dict(institute='HZB_Hysprint'),
        label_quantity='sample_id',
    )


class HySprint_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(order=['name', 'export_batch_ids', 'csv_export_file']),
        )
    )


# %% ####################### Cleaning


class HySprint_BasicCrystallization(Crystallization, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'batch',
                'present',
                'positon_in_experimental_plan',
            ],
            properties=dict(order=['name', 'location', 'datetime', 'samples']),
        )
    )


# %% ####################### Cleaning
class HySprint_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['HySprint', 'IRIS Printerlab', 'IRIS Preparationlab']),
        ),
    )

    cleaning = SubSection(section_def=SolutionCleaning, repeats=True)

    cleaning_uv = SubSection(section_def=UVCleaning, repeats=True)

    cleaning_plasma = SubSection(section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition
class HySprint_SprayPyrolysis(SprayPyrolysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['HySprint HTFumeHood']),
        ),
    )


# %% ### Dropcasting


class HySprint_VaporizationAndDropCasting(VaporizationAndDropCasting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'previous_process',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Non-functional layer',
        ),
    )


# %% ### Printing


class HySprint_Inkjet_Printing(LP50InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe_used',
                    'print_head_used',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'print_head_path',
                    'nozzle_voltage_profile',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['IRIS HZBGloveBoxes Pero3Inkjet']),
        ),
    )


# %% ### Spin Coating
class HySprint_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'recipe',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'HySprint HyFlowBox',
                    'HySprint HyPeroSpin',
                    'HySprint HySpin',
                    'HySprint ProtoVap',
                    'IRIS HZBGloveBoxes Pero2Spincoater',
                ]
            ),
        ),
    )


# %% ### Dip Coating


class HySprint_DipCoating(DipCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['HySprint'])),
    )


class HySprint_BladeCoating(BladeCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )


# %% ### Slot Die Coating


class HySprint_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(layer_type='Absorber Layer'),
    )

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['HySprint HySDC'])),
    )


# %% ### Sputterring
class HySprint_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['IRIS', 'HySprint'])),
    )


# %% ### AtomicLayerDepositio
class HySprint_AtomicLayerDeposition(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['IRIS', 'HySprint'])),
    )


class IRIS_AtomicLayerDeposition(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['IRIS'])),
    )

    properties = SubSection(section_def=ALDPropertiesIris)


# %% ### Evaporation
class HySprint_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'IRIS HZBGloveBoxes Pero5Evaporation',
                    'HySprint HyVap',
                    'HySprint HyPeroVap',
                    'HySprint ProtoVap',
                ]
            ),
        ),
    )


# %% ## Laser Scribing
class HySprint_LaserScribing(LaserScribing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'location', 'present', 'datetime', 'batch', 'samples']),
        )
    )


# %% ## Storage


class HySprint_Storage(Storage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )


# %%####################################### Measurements
class HZB_EnvironmentMeasurement(EnvironmentMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
                'location',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'label': 'Temperature Sensors',
                'x': 'data/time',
                'y': 'data/temperature_sensors/:/temperature',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            },
            {
                'label': 'Environment',
                'x': 'data/time',
                'y': ['data/humidity', 'data/temperature'],
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            },
        ],
    )


class HySprint_trSPVmeasurement(trSPVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'steps',
                'instruments',
                'results',
                'location',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'data/time',
                'y': 'data/voltages/:/voltage',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False, 'type': 'log'},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )

    def normalize(self, archive, logger):
        from baseclasses.helper.archive_builder.spv_archive import get_spv_archive

        from nomad_hysprint.schema_packages.file_parser.spv_parser import get_spv_data

        if self.data_file and self.data is None and self.properties is None:
            # todo detect file format
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                spv_dict, spv_data = get_spv_data(f.read())
                get_spv_archive(spv_dict, spv_data, f.name, self)
        super().normalize(archive, logger)


class HySprint_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'corrected_active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from baseclasses.helper.archive_builder.jv_archive import get_jv_archive

        from nomad_hysprint.schema_packages.file_parser.jv_parser import get_jv_data

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        if self.data_file:
            # todo detect file format
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                jv_dict, location = get_jv_data(f.read())
                self.location = location
                get_jv_archive(jv_dict, self.data_file, self)

        super().normalize(archive, logger)


class HySprint_SimpleMPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'time',
                'y': 'power_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from nomad_hysprint.schema_packages.file_parser.mppt_simple import read_mppt_file

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                data = read_mppt_file(f.read())

            self.time = data['time_data']
            self.voltage = data['voltage_data']
            self.current_density = data['current_density_data']
            self.power_density = data['power_data']
            self.efficiency = data.get('efficiency_data')
            self.properties = MPPTrackingProperties(
                time=data['total_time'], perturbation_voltage=data.get('step_size')
            )
        super().normalize(archive, logger)


class HySprint_MPPTracking(MPPTrackingHsprintCustom, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
                'location',
                'figures',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        )
    )

    def normalize(self, archive, logger):
        from baseclasses.helper.archive_builder.mpp_hysprint_archive import get_mpp_hysprint_samples
        from baseclasses.helper.utilities import rewrite_json

        from nomad_hysprint.schema_packages.file_parser.load_mpp_hysprint import load_mpp_file

        if self.data_file and self.load_data_from_file:
            self.load_data_from_file = False
            rewrite_json(['data', 'load_data_from_file'], archive, False)

            # from baseclasses.helper.utilities import get_encoding
            # with archive.m_context.raw_file(self.data_file, "br") as f:
            #     encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding='ascii') as f:
                data = load_mpp_file(f.read())  # , encoding)

            self.samples = get_mpp_hysprint_samples(self, data)
        import pandas as pd
        import plotly.express as px

        column_names = ['Time [hr]', 'Efficiency [%]', 'P']
        self.figures = []
        if self.averages:
            fig = px.scatter()
            df = pd.DataFrame(columns=column_names)
            for avg in self.averages:
                df1 = pd.DataFrame(columns=column_names)
                df1[column_names[0]] = avg.time * ureg('hr')
                df1[column_names[1]] = avg.efficiency
                df1[column_names[2]] = avg.name
                df = pd.concat([df, df1])

            fig = px.scatter(
                df,
                x=column_names[0],
                y=column_names[1],
                color=column_names[2],
                symbol=column_names[2],
                title='Averages',
            )
            fig.update_traces(marker=dict(size=4))
            fig.update_layout(
                showlegend=True,
                xaxis=dict(fixedrange=False),
                yaxis=dict(fixedrange=False),
            )
            self.figures.append(PlotlyFigure(label='Averages', index=0, figure=fig.to_plotly_json()))

        if self.best_pixels:
            df = pd.DataFrame(columns=column_names)
            for bp in self.best_pixels:
                df1 = pd.DataFrame(columns=column_names)
                df1[column_names[0]] = bp.time * ureg('hr')
                df1[column_names[1]] = bp.efficiency
                df1[column_names[2]] = bp.name
                df = pd.concat([df, df1])

            fig = px.scatter(
                df,
                x=column_names[0],
                y=column_names[1],
                color=column_names[2],
                symbol=column_names[2],
                title='Best Pixels',
            )
            fig.update_traces(marker=dict(size=4))
            fig.update_layout(
                showlegend=True,
                xaxis=dict(fixedrange=False),
                yaxis=dict(fixedrange=False),
            )
            self.figures.append(PlotlyFigure(label='Best Pixel', index=1, figure=fig.to_plotly_json()))

        super().normalize(archive, logger)


class HySprint_TimeResolvedPhotoluminescence(TimeResolvedPhotoluminescence, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
        a_plot=[
            {
                'x': 'trpl_properties/:/time',
                'y': 'trpl_properties/:/counts',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False, 'type': 'log'},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


class HySprint_OpticalMicroscope(OpticalMicroscope, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'detector_data_folder',
                'external_sample_url',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'data',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


class HySprint_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'data',
                'header_lines',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'eqe_data/:/photon_energy_array',
                'y': 'eqe_data/:/eqe_array',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        from nomad_hysprint.schema_packages.file_parser.eqe_parser import read_eqe_file

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)
            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                filedata = f.read()
                data_list = read_eqe_file(filedata)

            eqe_data = []
            for d in data_list:
                entry = SolarCellEQECustom(
                    photon_energy_array=d.get('photon_energy'),
                    raw_photon_energy_array=d.get('photon_energy_raw'),
                    eqe_array=d.get('intensity'),
                    raw_eqe_array=d.get('intensty_raw'),
                )
                entry.normalize(archive, logger)
                eqe_data.append(entry)
            self.eqe_data = eqe_data

        if eqe_data:
            band_gaps = np.array([d.bandgap_eqe.magnitude for d in eqe_data])

            add_band_gap(archive, band_gaps[np.isfinite(band_gaps)].mean())

        super().normalize(archive, logger)


class HySprint_PLmeasurement(PLMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        ),
        a_plot=[
            {
                'x': 'data/wavelength',
                'y': 'data/intensity',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


class HySprint_SEM(SEM_Microscope_Merlin, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'detector_data_folder',
                'external_sample_url',
            ],
            properties=dict(order=['name', 'detector_data', 'samples']),
        )
    )

    def normalize(self, archive, logger):
        self.method = 'SEM'
        if not self.samples and self.detector_data:
            search_id = self.detector_data[0].split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


class HySprint_XRD_XY(XRD, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'metadata_file',
                'shifted_data',
                'identifier',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': ['data/angle'],
                'y': ['data/intensity'],
                'layout': {
                    'yaxis': {'fixedrange': False, 'title': 'Counts'},
                    'xaxis': {'fixedrange': False},
                },
            },
        ],
    )

    def normalize(self, archive, logger):
        import pandas as pd

        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'tr') as f:
                if os.path.splitext(self.data_file)[-1] == '.xy' and self.data is None:
                    if 'Id' in f.readline():
                        skiprows = 1
                        data = pd.read_csv(f, sep=' |\t', header=None, skiprows=skiprows)
                    else:
                        skiprows = 0
                        data = pd.read_csv(f, sep=' |\t', header=None, skiprows=skiprows)
                    print(data)
                    self.data = XRDData(angle=data[0], intensity=data[1])
        super().normalize(archive, logger)


class HySprint_XPS(XPS, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        )
    )

    nxs_file = Quantity(type=HDF5Reference)
    specs_lab_prodigy_metadata = SubSection(section_def=XPSSpecsLabProdigySettings)

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'tr') as f:
                from nomad_hysprint.schema_packages.file_parser.xps_parser import (
                    map_specs_lab_prodigy_data,
                    parse_xps_xy_file,
                )

                results = parse_xps_xy_file(f.read())
                self.specs_lab_prodigy_metadata, method = map_specs_lab_prodigy_data(results)
                self.datetime = convert_datetime(
                    results['Acquisition Date'], datetime_format='%Y-%m-%d %H:%M:%S UTC', utc=True
                )
                self.description = results.get('Experiment Description')

                output_file = archive.metadata.mainfile.replace('archive.json', 'nxs').replace(' ', '')
                with archive.m_context.raw_file(output_file, 'w') as outfile:
                    if not archive.metadata.published:
                        convert(
                            input_file=(f.name),
                            reader='xps',
                            nxdl='NXxps',
                            output=outfile.name,
                            skip_verify=True,
                        )  # TODO only call if upload not published
                    self.nxs_file = f'/uploads/{archive.metadata.upload_id}/raw/{output_file}#/'
        self.method = method
        super().normalize(archive, logger)


class HySprint_PLImaging(PLImaging, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'solution',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        )
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


class HySprint_UVvismeasurement(UVvisMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        )
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id)
        super().normalize(archive, logger)


class HySprint_CyclicVoltammetry(CyclicVoltammetry, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'station',
                'voltage',
                'current',
                'current_density',
                'charge_density',
                'control',
                'charge',
                'time',
                'voltage_rhe_uncompensated',
                'voltage_ref_compensated',
                'voltage_rhe_compensated',
            ],
            properties=dict(order=['name', 'data_file', 'environment', 'setup', 'samples']),
        ),
        a_plot=[
            {
                'x': 'cycles/:/voltage',
                'y': 'cycles/:/current',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
            {
                'label': 'Current Density over Voltage RHE',
                'x': 'cycles/:/voltage_rhe_compensated',
                'y': 'cycles/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            },
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpt':
                    from baseclasses.helper.archive_builder.mpt_get_archive import (
                        get_cv_properties,
                        get_voltammetry_data,
                    )

                    from nomad_hysprint.schema_packages.file_parser.mps_file_parser import read_mpt_file

                    metadata, data, technique = read_mpt_file(f)
                    get_voltammetry_data(data, self)

                    if 'Cyclic' in technique and self.properties is None:
                        self.properties = get_cv_properties(metadata)
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                file_content = f.read()
                if (
                    os.path.splitext(self.data_file)[-1] == '.csv'
                    and 'Experiment:' in file_content
                    and 'Start date:' in file_content
                    and 'Time (s)' in file_content
                ):
                    from io import StringIO

                    import pandas as pd
                    from baseclasses.chemical_energy.voltammetry import VoltammetryCycleWithPlot

                    data = pd.read_csv(StringIO(file_content), skiprows=3, sep=',', encoding='utf-8')
                    metadata = pd.read_csv(
                        StringIO(file_content), nrows=3, sep=',', encoding='utf-8', header=None
                    )
                    self.datetime = convert_datetime(
                        metadata.iloc[1, 1].strip(), datetime_format='%d %B %Y', utc=False
                    )
                    self.cycles = [
                        VoltammetryCycleWithPlot(
                            time=data['Time (s)'][63:] * ureg('seconds'),
                            voltage=data[' Voltage (V)'][63:] * ureg('V'),
                            current=data[' Current (A)'][63:] * ureg('A'),
                            charge=data[' Charge (C)'][63:] * ureg('C'),
                        )
                    ]

        super().normalize(archive, logger)


class HySprint_ElectrochemicalImpedanceSpectroscopy(ElectrochemicalImpedanceSpectroscopy, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'station',
            ],
            properties=dict(order=['name', 'data_file', 'environment', 'setup', 'samples']),
        ),
        a_plot=[
            {
                'label': 'Nyquist Plot',
                'x': 'z_real',
                'y': 'z_imaginary',
                'layout': {
                    'yaxis': {'fixedrange': False, 'title': '-Im(Z) (Ω)'},
                    'xaxis': {'fixedrange': False, 'title': 'Re(Z) (Ω)'},
                },
            },
            {
                'label': 'Bode Plot',
                'x': ['frequency', 'frequency'],
                'y': ['./z_modulus', './z_angle'],
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False, 'type': 'log'},
                },
            },
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpt':
                    from baseclasses.helper.archive_builder.mpt_get_archive import (
                        get_eis_data,
                        get_eis_properties,
                        get_meta_data,
                    )

                    from nomad_hysprint.schema_packages.file_parser.mps_file_parser import read_mpt_file

                    metadata, data, technique = read_mpt_file(f)
                    get_eis_data(data, self)
                    get_meta_data(metadata, self)

                    if 'Potentio' in technique and self.properties is None:
                        self.properties = get_eis_properties(metadata)

        super().normalize(archive, logger)


class HySprint_OpenCircuitVoltage(OpenCircuitVoltage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'metadata_file',
                'station',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'environment',
                    'setup',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'label': 'Voltage',
                'x': 'time',
                'y': 'voltage',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                if os.path.splitext(self.data_file)[-1] == '.mpt':
                    from baseclasses.helper.archive_builder.mpt_get_archive import (
                        get_ocv_properties,
                        get_voltammetry_data,
                    )

                    from nomad_hysprint.schema_packages.file_parser.mps_file_parser import read_mpt_file

                    metadata, data, technique = read_mpt_file(f)
                    get_voltammetry_data(data, self)

                    if 'Open Circuit Voltage' in technique and self.properties is None:
                        self.properties = get_ocv_properties(metadata)

            with archive.m_context.raw_file(self.data_file, 'rt') as f:
                file_content = f.read()
                if (
                    os.path.splitext(self.data_file)[-1] == '.csv'
                    and 'Experiment:' in file_content
                    and 'Start date:' in file_content
                    and 'Time (s)' in file_content
                ):
                    from io import StringIO

                    import pandas as pd

                    data = pd.read_csv(StringIO(file_content), skiprows=3, sep=',', encoding='utf-8')
                    metadata = pd.read_csv(
                        StringIO(file_content), skiprows=1, nrows=1, sep=',', encoding='utf-8', header=None
                    )

                    self.datetime = convert_datetime(
                        metadata.iloc[0, 2].strip() + ' ' + str(metadata.iloc[0, 3]).strip(),
                        datetime_format='%B %d %Y',
                        utc=False,
                    )

                    self.time = data['Time (s)'] * ureg('seconds')
                    self.voltage = data[' Voltage (V)'] * ureg('V')
                    self.current = data[' Current (A)'] * ureg('A')

        super().normalize(archive, logger)


# %%####################################### Data Transformations
class HZB_NKData(NKData, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'datetime',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'data_reference',
                    'chemical_composition_or_formulas',
                    'reference',
                ]
            ),
        )
    )

    def normalize(self, archive, logger):
        from baseclasses.helper.utilities import get_encoding

        with archive.m_context.raw_file(self.data_file, 'br') as f:
            encoding = get_encoding(f)

        with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
            from baseclasses.helper.archive_builder.nk_archive import get_nk_archive
            from nomad_hysprint.schema_packages.file_parser.nk_parser import get_nk_data

            nk_data, metadata = get_nk_data(f.read())

        self.description = metadata['Comment'] if 'Comment' in metadata else ''
        self.chemical_composition_or_formulas = metadata['Formula'] if 'Formula' in metadata else ''
        self.name = metadata['Name'] if 'Name' in metadata else ''
        doi = metadata['Reference'] if 'Reference' in metadata else ''
        if doi.startswith('doi:'):
            doi = doi.strip('doi:')
            doi = 'https://doi.org/' + doi
        self.data_reference = doi
        self.name = metadata['Name'] if 'Name' in metadata else ''
        self.data = get_nk_archive(nk_data)

        super().normalize(archive, logger)


# %%####################################### Generic Entries


class ProcessParameter(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(
        type=str,
        description="""
        The name of a paramter.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )

    value_number = Quantity(
        type=np.dtype(np.float64),
        description="""
        The numerical value of a continous paramter.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    value_string = Quantity(
        type=str,
        description="""
        The string value of a categorical paramter.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )


class HySprint_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'present', 'data_file', 'batch', 'samples']),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    process_parameters = SubSection(section_def=ProcessParameter, repeats=True)


class HySprint_WetChemicalDepoistion(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class HySprint_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class HySprint_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        )
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id, upload_id=archive.metadata.upload_id)
        super().normalize(archive, logger)


m_package.__init_metainfo__()
