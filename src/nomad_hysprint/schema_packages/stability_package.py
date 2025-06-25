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

import numpy as np
from baseclasses import BaseMeasurement, BaseProcess
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.metainfo import Datetime, MEnum, Package, Quantity, Reference, Section, SubSection

from .hysprint_package import HySprint_JVmeasurement

m_package = Package()


class StabilityInitialCharacterization(BaseMeasurement, EntryData):
    """Records the initial performance parameters of the solar cell device
    before the stability test commences."""

    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
            properties=dict(
                order=['name', 'datetime', 'sample', 'jv_measurement', 'eqe_data_file', 'results']
            ),
        )
    )

    datetime = Quantity(
        type=Datetime,
        description='Date and time of initial characterization.',
        a_eln=dict(component='DateTimeEditQuantity'),
    )

    jv_measurement = SubSection(
        section_def=HySprint_JVmeasurement, description='Initial JV measurement characterization.'
    )

    eqe_data_file = Quantity(
        type=str,
        description='Reference to EQE data file or spectra.',
        a_eln=dict(component='FileEditQuantity'),
    )


class Stability_LightStressConditions(ArchiveSection):
    """Details of the light stress conditions applied."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'light_source_type',
                    'light_intensity',
                    'light_spectrum_details',
                    'uv_filter_used',
                    'illumination_type',
                ]
            ),
        )
    )

    light_source_type = Quantity(
        type=MEnum(
            [
                'Solar Simulator',
                'LED Array',
                'Xenon Lamp',
                'Metal Halide Lamp',
                'Tungsten Halogen',
                'Plasma Light Source',
                'Natural Sunlight',
                'Other',
            ]
        ),
        description='Type of light source used for the stability test.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    light_intensity = Quantity(
        type=np.float64,
        unit='W/m**2',
        description='Light intensity (e.g., 1000 W/m^2 for 1 sun).',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='W/m**2'),
    )

    light_spectrum_details = Quantity(
        type=str,
        description='Spectrum details, calibration method, and filters.',
        a_eln=dict(component='RichTextEditQuantity'),
    )

    uv_filter_used = Quantity(
        type=bool,
        default=False,
        description='Whether a UV filter was used during light stress.',
        a_eln=dict(component='BoolEditQuantity'),
    )

    illumination_type = Quantity(
        type=MEnum(['Continuous', 'Cycled']),
        description='Type of illumination.',
        a_eln=dict(component='EnumEditQuantity'),
    )


class Stability_ThermalStressConditions(ArchiveSection):
    """Details of the thermal stress conditions applied."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'temperature',
                    'temperature_cycling_parameters',
                    'temperature_sensor_type_and_location',
                ]
            ),
        )
    )

    temperature = Quantity(
        type=np.float64,
        unit='celsius',
        description='Applied temperature for the stress test.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='celsius'),
    )

    temperature_cycling_parameters = Quantity(
        type=str,
        description='Details of temperature cycling if applicable.',
        a_eln=dict(component='RichTextEditQuantity'),
    )

    temperature_sensor_type_and_location = Quantity(
        type=MEnum(
            [
                'Thermocouple on device',
                'Thermocouple on substrate',
                'Thermocouple in chamber',
                'RTD (Resistance Temperature Detector)',
                'IR Sensor',
                'Chamber built-in sensor',
                'Other',
            ]
        ),
        description='Type and location of the temperature sensor used.',
        a_eln=dict(component='EnumEditQuantity'),
    )


class Stability_BiasStressConditions(ArchiveSection):
    """Details of the electrical bias stress conditions applied."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(order=['electrical_bias_condition', 'bias_voltage', 'bias_current_density']),
        )
    )

    electrical_bias_condition = Quantity(
        type=MEnum(
            [
                'Open Circuit (OC)',
                'Maximum Power Point (MPP)',
                'Short Circuit (SC)',
                'Constant Voltage',
                'Constant Current',
                'Positive Bias',
                'Negative Bias',
            ]
        ),
        description='Electrical bias condition applied during stress test.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    bias_voltage = Quantity(
        type=np.float64,
        unit='V',
        description=('Applied bias voltage for constant or positive/negative bias.'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    bias_current_density = Quantity(
        type=np.float64,
        unit='mA/cm**2',
        description='Applied bias current density if under constant current.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mA/cm**2'),
    )


class Stability_AtmosphericStressConditions(ArchiveSection):
    """Details of the atmospheric conditions during the stress test."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(order=['environment', 'relative_humidity', 'atmosphere_composition_details']),
        )
    )

    environment = Quantity(
        type=MEnum(
            [
                'Ambient Air',
                'Inert Atmosphere (N2)',
                'Inert Atmosphere (Ar)',
                'Controlled Humidity Chamber',
                'Environmental Chamber',
            ]
        ),
        description='Testing environment.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    relative_humidity = Quantity(
        type=np.float64,
        description='Relative humidity (RH), expressed as percentage from 0-100.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='%'),
    )

    atmosphere_composition_details = Quantity(
        type=str,
        description='Specific composition if not standard air.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


class Stability_CyclingStressProperties(ArchiveSection):
    """Details specific to cycled stress conditions."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'is_cycled_stress_protocol',
                    'cycle_period',
                    'number_of_cycles_applied',
                    'duty_cycle_description',
                ]
            ),
        )
    )

    is_cycled_stress_protocol = Quantity(
        type=bool,
        default=False,
        description='Is this test primarily a cycled stress protocol?',
        a_eln=dict(component='BoolEditQuantity'),
    )

    cycle_period = Quantity(
        type=np.float64,
        unit='hour',
        description='Duration of one full cycle.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    duty_cycle_description = Quantity(
        type=str,
        description='Description of the duty cycle for the cycled stress.',
        a_eln=dict(component='RichTextEditQuantity'),
    )

    number_of_cycles_applied = Quantity(
        type=int,
        description='Total number of stress cycles applied during the test.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit=''),
    )


class Stability_GlueBasedEncapsulation(ArchiveSection):
    """Defines the materials and process parameters for a glue-based encapsulation method."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'adhesive',
                    'coverslip',
                    'contacting',
                    'equipment',
                    'environment',
                    'temperature',
                    'curing_method',
                    'applied_pressure_type',
                    'applied_pressure_value',
                ]
            ),
        )
    )

    # --- Materials ---
    adhesive = Quantity(
        type=MEnum(['UV-curable acrylate', 'Two-part epoxy', 'Silicone']),
        description='Type of adhesive used.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    coverslip = Quantity(
        type=MEnum(['Glass', 'Polymer']),
        description='Material of the coverslip.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    contacting = Quantity(
        type=MEnum(['Tinned copper ribbons', 'Conductive paste/glue']),
        description='Method for making electrical contact.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    equipment = Quantity(
        type=MEnum(['UV Lamp', 'Manual Press']),
        description='Primary equipment used for the process.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    # --- Process Parameters ---
    environment = Quantity(
        type=MEnum(['Inert Atmosphere', 'Ambient Air', 'Controlled Humidity']),
        description='The environment in which the encapsulation was performed.',
    )
    temperature = Quantity(
        type=np.float64,
        unit='celsius',
        description='Process temperature.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='celsius'),
    )
    curing_method = Quantity(
        type=MEnum(['UV Irradiation', 'Thermal Curing', 'Room Temp Curing']),
        description='Method used to cure the adhesive.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    applied_pressure_type = Quantity(
        type=MEnum(['Manual', 'Controlled']),
        description='The type of pressure application.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    applied_pressure_value = Quantity(
        type=np.float64,
        unit='mbar',
        description='The value of the applied pressure, if controlled.',
        a_eln=dict(
            component='NumberEditQuantity',
            visible=dict(applied_pressure_type='Controlled'),
            defaultDisplayUnit='mbar',
        ),
    )


class Stability_LaminationBasedEncapsulation(ArchiveSection):
    """Defines the materials and process parameters for a lamination-based encapsulation method."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'encapsulant_film',
                    'edge_sealant',
                    'desiccant_in_sealant',
                    'encapsulation_glass',
                    'contacting',
                    'equipment',
                    'environment',
                    'temperature',
                    'lamination_duration',
                    'pressure_cycle_details',
                    'cooling_method',
                ]
            ),
        )
    )

    # --- Materials ---
    encapsulant_film = Quantity(
        type=MEnum(['Polyolefin (POE)', 'Ethylene vinyl acetate (EVA)', 'Ionomer', 'Polyurethane']),
        description='The polymer film used as the main encapsulant.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    edge_sealant = Quantity(
        type=MEnum(['Butyl rubber', 'Polyisobutylene (PIB)', 'Epoxy']),
        description='The material used to seal the edges of the package.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    desiccant_in_sealant = Quantity(
        type=bool,
        default=False,
        description='Whether a desiccant was included in the edge sealant.',
        a_eln=dict(component='BoolEditQuantity'),
    )
    encapsulation_glass = Quantity(
        type=MEnum(['Planiclear', 'Low-iron glass']),
        description='The type of glass used for the encapsulation sandwich.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    contacting = Quantity(
        type=MEnum(['Tinned copper ribbons', 'Busbars']),
        description='Method for making electrical contact.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    equipment = Quantity(
        type=MEnum(['Vacuum Laminator']),
        description='Primary equipment used for the process.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    # --- Process Parameters ---
    environment = Quantity(
        type=MEnum(['Ambient Air', 'Inert Atmosphere']),
        description='The environment in which the encapsulation was performed.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    temperature = Quantity(
        type=np.float64,
        unit='celsius',
        description='Process temperature.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='celsius'),
    )
    lamination_duration = Quantity(
        type=np.float64,
        unit='minute',
        description='Total duration of the lamination process.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='minute'),
    )
    pressure_cycle_details = Quantity(
        type=str,
        description='Description of the pressure and vacuum cycle during lamination.',
        a_eln=dict(component='RichTextEditQuantity'),
    )
    cooling_method = Quantity(
        type=MEnum(['Air Cooling', 'Controlled Ramp-down']),
        description='Method used to cool the sample after lamination.',
        a_eln=dict(component='EnumEditQuantity'),
    )


class Stability_MPPTrackingConditions(ArchiveSection):
    """Details of the Maximum Power Point (MPP) tracking during stability testing."""

    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id'],
            properties=dict(
                order=[
                    'mpp_tracking_type',
                    'tracking_algorithm',
                    'tracking_frequency',
                    'voltage_step_size',
                    'voltage_perturbation_range',
                    'irradiance_sensor_type',
                    'weather_data_collection',
                    'mpp_data_file',
                ]
            ),
        )
    )

    mpp_tracking_type = Quantity(
        type=MEnum(['Indoor Fixed Light', 'Outdoor Natural Light']),
        description='Type of MPP tracking environment.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    tracking_algorithm = Quantity(
        type=MEnum(
            ['Perturb and Observe', 'Incremental Conductance', 'Constant Voltage', 'Beta Method', 'Other']
        ),
        description='Algorithm used for MPP tracking.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    tracking_frequency = Quantity(
        type=np.float64,
        unit='Hz',
        description='Frequency of MPP tracking measurements.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='Hz'),
    )

    voltage_step_size = Quantity(
        type=np.float64,
        unit='V',
        description='Voltage step size used in the tracking algorithm.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    voltage_perturbation_range = Quantity(
        type=np.float64,
        unit='V',
        description='Range of voltage perturbation around MPP.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'),
    )

    irradiance_sensor_type = Quantity(
        type=MEnum(
            [
                'Silicon Reference Cell',
                'Pyranometer',
                'Spectroradiometer',
                'Photodiode',
                'Thermopile',
                'Other',
            ]
        ),
        description='Type of irradiance sensor used.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    weather_data_collection = Quantity(
        type=bool,
        default=False,
        description='Whether additional weather data is being collected (relevant for outdoor testing).',
        a_eln=dict(component='BoolEditQuantity'),
    )

    mpp_data_file = Quantity(
        type=str, description='Reference to MPP tracking data file.', a_eln=dict(component='FileEditQuantity')
    )


class StabilityMeasurement(BaseMeasurement, EntryData):
    """Key stability metrics derived from stability tests, as a standalone entry."""

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'positon_in_experimental_plan',
                'method',
                'batch',
                'steps',
                'atmosphere',
                'instruments',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'sample',
                    'burn_in_time',
                    'ts80',
                    't80',
                    'degradation_rate',
                    'notes',
                ]
            ),
        )
    )

    # sample = Quantity(
    #     type=Reference(SolcarCellSample.m_def),
    #     description='Reference to the sample for which these stability metrics are measured.',
    #     a_eln=dict(component='ReferenceEditQuantity', query_section='SolcarCellSample'),
    # )

    burn_in_time = Quantity(
        type=np.float64,
        unit='hour',
        description='Time until stabilization after initial burn-in.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    ts80 = Quantity(
        type=np.float64,
        unit='hour',
        description='Time to 80% of initial efficiency after stabilization.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    t80 = Quantity(
        type=np.float64,
        unit='hour',
        description='Time to 80% of initial efficiency from t=0.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'),
    )

    degradation_rate = Quantity(
        type=np.float64,
        description='Rate of performance degradation after stabilization (percentage per hour).',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='1/hour'),
    )

    notes = Quantity(
        type=str,
        description='Additional notes or observations about the stability metrics.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


class StabilityMeasurement_Section(ArchiveSection):
    """A link to the sample already in the stability test, with all stability metrics and plots"""

    # TODO
    pass


class StabilityTest(BaseProcess, EntryData):
    """Main stability test class including all conditions and measurements."""

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'positon_in_experimental_plan',
                'method',
                'batch',
                'steps',
                'atmosphere',
                'instruments',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'samples',
                    'isos_protocol',
                    'custom_protocol_description',
                    'stability_measurements',
                    'glue_encapsulation',
                    'lamination_encapsulation',
                    'light_stress',
                    'thermal_stress',
                    'bias_stress',
                    'atmospheric_stress',
                    'mpp_tracking',
                    'cycling_stress',
                ]
            ),
        )
    )

    isos_protocol = Quantity(
        type=MEnum(
            [
                'ISOS-D-1',
                'ISOS-D-2',
                'ISOS-D-3',
                'ISOS-L-1',
                'ISOS-L-2',
                'ISOS-L-3',
                'ISOS-O-1',
                'ISOS-O-2',
                'ISOS-O-3',
                'ISOS-T-1',
                'ISOS-T-2',
                'ISOS-T-3',
                'ISOS-LT-1',
                'ISOS-LT-2',
                'ISOS-LT-3',
                'ISOS-V-1',
                'ISOS-V-2',
                'ISOS-V-3',
                'ISOS-LC-1',
                'ISOS-LC-2',
                'ISOS-LC-3',
                'Custom Protocol',
            ]
        ),
        description='ISOS protocol followed.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    custom_protocol_description = Quantity(
        type=str,
        description='Description for custom protocols.',
        a_eln=dict(component='RichTextEditQuantity'),
    )

    glue_encapsulation = SubSection(
        section_def=Stability_GlueBasedEncapsulation,
        repeats=False,
        description='Glue-based encapsulation details.',
    )

    lamination_encapsulation = SubSection(
        section_def=Stability_LaminationBasedEncapsulation,
        repeats=False,
        description='Lamination-based encapsulation details.',
    )

    light_stress = SubSection(section_def=Stability_LightStressConditions, repeats=False)

    thermal_stress = SubSection(section_def=Stability_ThermalStressConditions, repeats=False)

    bias_stress = SubSection(section_def=Stability_BiasStressConditions, repeats=False)

    atmospheric_stress = SubSection(section_def=Stability_AtmosphericStressConditions, repeats=False)

    mpp_tracking = SubSection(section_def=Stability_MPPTrackingConditions, repeats=False)

    cycling_stress = SubSection(section_def=Stability_CyclingStressProperties, repeats=False)

    stability_measurements = Quantity(
        type=Reference(StabilityMeasurement.m_def),
        description='Reference to a standalone StabilityMeasurement for this test.',
        a_eln=dict(component='ReferenceEditQuantity', query_section='StabilityMeasurement'),
        shape=['*'],
    )


m_package.__init_metainfo__()
