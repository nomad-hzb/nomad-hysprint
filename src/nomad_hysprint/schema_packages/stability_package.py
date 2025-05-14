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
from baseclasses.helper.utilities import set_sample_reference
from nomad.datamodel.data import EntryData
from nomad.datamodel.results import Properties
from nomad.metainfo import Datetime, MEnum, Package, Quantity, Section, SubSection

m_package = Package()


class StabilityInitialCharacterization(BaseMeasurement, EntryData):
    '''Records the initial performance parameters of the solar cell device
    before the stability test commences.'''

    m_def = Section(a_eln=dict(
        hide=['lab_id', 'users'],
        properties=dict(order=['name', 'datetime', 'sample', 'results'])
    ))

    datetime = Quantity(
        type=Datetime,
        description='Date and time of initial characterization.'
    )

    jv_scan_parameters = Quantity(
        type=str,
        description=(
            'Details of J-V scan including light source, intensity, spectrum, '
            'scan speed, direction, and delay time.'
        ),
        a_eln=dict(component='RichTextEditQuantity')
    )

    eqe_data_file = Quantity(
        type=str,
        description='Reference to EQE data file or spectra.',
        a_eln=dict(component='FileEditQuantity')
    )

    def normalize(self, archive, logger):
        if self.eqe_data_file:
            # Add EQE data processing logic here if needed
            pass
        super().normalize(archive, logger)


class LightStressConditions(Properties):
    '''Details of the light stress conditions applied.
    Based on Khenkin et al., 2020, Tables 1 & 4.'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'light_source_type',
            'light_intensity',
            'light_spectrum_details',
            'uv_filter_used',
            'illumination_type'
        ])
    ))

    light_source_type = Quantity(
        type=str,
        description='Type of light source (e.g., Solar simulator, LED, Xenon).'
    )
    
    light_intensity = Quantity(
        type=np.float64,
        unit='W/m**2',
        description='Light intensity (e.g., 1000 W/m^2 for 1 sun).'
    )
    
    light_spectrum_details = Quantity(
        type=str,
        description='Spectrum details, calibration method, and filters.',
        a_eln=dict(component='RichTextEditQuantity')
    )
    
    uv_filter_used = Quantity(
        type=bool,
        default=False,
        description='Whether a UV filter was used during light stress.'
    )
    
    illumination_type = Quantity(
        type=MEnum(['Continuous', 'Cycled']),
        description='Type of illumination.'
    )


class ThermalStressConditions(Properties):
    '''Details of the thermal stress conditions applied.
    Based on Khenkin et al., 2020, Table 1.'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'temperature',
            'temperature_cycling_parameters',
            'temperature_sensor_type_and_location'
        ])
    ))

    temperature = Quantity(
        type=np.float64,
        unit='celsius',
        description='Applied temperature for the stress test.'
    )
    
    temperature_cycling_parameters = Quantity(
        type=str,
        description='Details of temperature cycling if applicable.',
        a_eln=dict(component='RichTextEditQuantity')
    )
    
    temperature_sensor_type_and_location = Quantity(
        type=str,
        description='Type and location of the temperature sensor used.'
    )


class BiasStressConditions(Properties):
    '''Details of the electrical bias stress conditions applied.
    Based on Khenkin et al., 2020, Table 1 (ISOS-V).'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'electrical_bias_condition',
            'bias_voltage',
            'bias_current_density'
        ])
    ))

    electrical_bias_condition = Quantity(
        type=MEnum([
            'Open Circuit (OC)',
            'Maximum Power Point (MPP)',
            'Short Circuit (SC)',
            'Constant Voltage',
            'Constant Current',
            'Positive Bias',
            'Negative Bias'
        ]),
        description='Electrical bias condition applied during stress test.'
    )
    
    bias_voltage = Quantity(
        type=np.float64,
        unit='V',
        description=(
            'Applied bias voltage for constant or positive/negative bias.'
        )
    )
    
    bias_current_density = Quantity(
        type=np.float64,
        unit='mA/cm**2',
        description='Applied bias current density if under constant current.'
    )


class AtmosphericStressConditions(Properties):
    '''Details of the atmospheric conditions during the stress test.
    Based on Khenkin et al., 2020, Tables 1 & 2.'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'environment',
            'relative_humidity',
            'atmosphere_composition_details'
        ])
    ))

    environment = Quantity(
        type=MEnum([
            'Ambient Air',
            'Inert Atmosphere (N2)',
            'Inert Atmosphere (Ar)',
            'Controlled Humidity Chamber',
            'Sealed Pouch',
            'Environmental Chamber'
        ]),
        description='Testing environment.'
    )
    
    relative_humidity = Quantity(
        type=np.float64,
        description='Relative humidity (RH).'
    )
    
    atmosphere_composition_details = Quantity(
        type=str,
        description='Specific composition if not standard air.',
        a_eln=dict(component='RichTextEditQuantity')
    )


class CyclingStressProperties(Properties):
    '''Details specific to cycled stress conditions.
    Based on Khenkin et al., 2020, Table 1 (ISOS-LC).'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'is_cycled_stress_protocol',
            'cycle_period',
            'duty_cycle_description',
            'number_of_cycles_applied'
        ])
    ))

    is_cycled_stress_protocol = Quantity(
        type=bool,
        default=False,
        description='Is this test primarily a cycled stress protocol?'
    )
    
    cycle_period = Quantity(
        type=np.float64,
        unit='hour',
        description='Duration of one full cycle.'
    )
    
    duty_cycle_description = Quantity(
        type=str,
        description='Description of the duty cycle for the cycled stress.'
    )
    
    number_of_cycles_applied = Quantity(
        type=int,
        description='Total number of stress cycles applied during the test.'
    )


class StabilityMetrics(Properties):
    '''Key stability metrics based on Khenkin et al., 2020.'''

    m_def = Section(a_eln=dict(
        hide=['name', 'lab_id'],
        properties=dict(order=[
            'burn_in_time',
            'ts80',
            't80',
            'degradation_rate'
        ])
    ))

    burn_in_time = Quantity(
        type=np.float64,
        unit='hour',
        description='Time until stabilization after initial burn-in.'
    )

    ts80 = Quantity(
        type=np.float64,
        unit='hour',
        description='Time to 80% of initial efficiency after stabilization.'
    )

    t80 = Quantity(
        type=np.float64,
        unit='hour',
        description='Time to 80% of initial efficiency from t=0.'
    )

    degradation_rate = Quantity(
        type=np.float64,
        description='Rate of performance degradation after stabilization.'
    )


class StabilityTest(BaseProcess, EntryData):
    '''Main stability test class including all conditions and measurements.'''

    m_def = Section(a_eln=dict(
        hide=['lab_id', 'users'],
        properties=dict(order=[
            'name',
            'datetime',
            'sample',
            'isos_protocol_type',
            'custom_protocol_description',
            'encapsulation_details',
            'light_stress',
            'thermal_stress',
            'bias_stress',
            'atmospheric_stress',
            'cycling_stress',
            'stability_metrics'
        ])
    ))

    isos_protocol_type = Quantity(
        type=MEnum([
            'ISOS-D-1', 'ISOS-D-2', 'ISOS-D-3',
            'ISOS-L-1', 'ISOS-L-2', 'ISOS-L-3',
            'ISOS-O-1', 'ISOS-O-2', 'ISOS-O-3',
            'ISOS-T-1', 'ISOS-T-2', 'ISOS-T-3',
            'ISOS-LT-1', 'ISOS-LT-2', 'ISOS-LT-3',
            'ISOS-V-1', 'ISOS-V-2', 'ISOS-V-3',
            'ISOS-LC-1', 'ISOS-LC-2', 'ISOS-LC-3',
            'Custom Protocol'
        ]),
        description='ISOS protocol followed.'
    )

    custom_protocol_description = Quantity(
        type=str,
        description='Description for custom protocols.',
        a_eln=dict(component='RichTextEditQuantity')
    )

    encapsulation_details = Quantity(
        type=str,
        description='Details of encapsulation materials and processing.',
        a_eln=dict(component='RichTextEditQuantity')
    )

    light_stress = SubSection(
        section_def=LightStressConditions,
        repeats=False
    )

    thermal_stress = SubSection(
        section_def=ThermalStressConditions,
        repeats=False
    )

    bias_stress = SubSection(
        section_def=BiasStressConditions,
        repeats=False
    )

    atmospheric_stress = SubSection(
        section_def=AtmosphericStressConditions,
        repeats=False
    )

    cycling_stress = SubSection(
        section_def=CyclingStressProperties,
        repeats=False
    )

    stability_metrics = SubSection(
        section_def=StabilityMetrics,
        repeats=False
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(
                archive, self, search_id, upload_id=archive.metadata.upload_id
            )
        super().normalize(archive, logger)


m_package.__init_metainfo__()