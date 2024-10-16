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

from baseclasses import LayerProperties
from baseclasses.material_processes_misc import (
    AirKnifeGasQuenching,
    Annealing,
    AntiSolventQuenching,
)
from baseclasses.vapour_based_deposition.atomic_layer_deposition import (
    ALDProperties, 
    ALDPropertiesIris, 
    ALDMaterial,
)
from baseclasses.vapour_based_deposition.evaporation import (
    InorganicEvaporation,
    OrganicEvaporation,
)
from baseclasses.vapour_based_deposition.sputtering import SputteringProcess
from baseclasses.wet_chemical_deposition import PrecursorSolution
from baseclasses.wet_chemical_deposition.slot_die_coating import (
    SlotDieCoatingProperties,
)
from baseclasses.wet_chemical_deposition.spin_coating import SpinCoatingRecipeSteps
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference,
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


def get_entry_id_from_file_name(file_name, upload_id):
    from nomad.utils import hash

    return hash(upload_id, file_name)


def get_reference(upload_id, file_name):
    entry_id = get_entry_id_from_file_name(file_name, upload_id)
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def convert_quantity(value, factor):
    try:
        return float(value) * factor
    except Exception:
        return None


def get_value(data, key, default=None, number=True):
    try:
        if key not in data:
            return default
        if pd.isna(data[key]):
            return default
        if number:
            return float(data[key])
        return str(data[key]).strip()
    except Exception as e:
        raise e


def map_basic_sample(data, substrate_name, upload_id):
    archive = HySprint_Sample(
        name=data['Nomad ID'],
        lab_id=data['Nomad ID'],
        substrate=get_reference(upload_id, substrate_name),
        description=get_value(data, 'Variation', None, False),
    )
    return (data['Nomad ID'], archive)


def map_batch(batch_ids, batch_id, upload_id):
    archive = HySprint_Batch(
        name=batch_id,
        lab_id=batch_id,
        entities=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in batch_ids
        ],
    )
    return (batch_id, archive)


def map_solutions(data):
    solvents = []
    solutes = []
    for col in data.index:
        if 'solvent' in col.lower():
            solvents.append(' '.join(col.split(' ')[:2]))
        if 'solute' in col.lower():
            solutes.append(' '.join(col.split(' ')[:2]))

    final_solvents = []
    final_solutes = []
    for solvent in sorted(set(solvents)):
        if not get_value(data, f'{solvent} name', None, False) and not get_value(
            data, f'{solvent} volume [uL]', None
        ):
            continue
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solvent} name', None, False),
                    load_data=False,
                ),
                chemical_volume=convert_quantity(
                    get_value(data, f'{solvent} volume [uL]', None), 1 / 1000
                ),
            )
        )
    for solute in sorted(set(solutes)):
        if not get_value(data, f'{solute} type', None, False) and not get_value(
            data, f'{solute} Concentration [mM]', None
        ):
            continue
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solute} type', None, False), load_data=False
                ),
                concentration_mol=convert_quantity(
                    get_value(data, f'{solute} Concentration [mM]', None), 1 / 1000
                ),
            )
        )

    archive = Solution(solvent=final_solvents, solute=final_solutes)

    return archive


def map_spin_coating(i, j, lab_ids, data, upload_id):
    archive = HySprint_SpinCoating(
        name='spin coating ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=[
            LayerProperties(
                layer_type=get_value(data, 'Layer type', None, False),
                layer_material_name=get_value(data, 'Material name', None, False),
            )
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        quenching=AntiSolventQuenching(
            anti_solvent_volume=get_value(data, 'Anti solvent volume [ml]', None),
            anti_solvent_dropping_time=get_value(
                data, 'Anti solvent dropping time [s]', None
            ),
            anti_solvent_2=PubChemPureSubstanceSectionCustom(
                name=get_value(data, 'Anti solvent name', None, False), load_data=False
            ),
        ),
        annealing=Annealing(
            temperature=get_value(data, 'Annealing temperature [°C]', None),
            time=convert_quantity(get_value(data, 'Annealing time [min]', None), 60),
        ),
        recipe_steps=[
            SpinCoatingRecipeSteps(
                speed=get_value(data, 'Rotation speed [rpm]', None),
                time=get_value(data, 'Rotation time [s]', None),
            )
        ],
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_spin_coating_{material}', archive)


def map_sdc(i, j, lab_ids, data, upload_id):
    archive = HySprint_SlotDieCoating(
        name='slot die coating ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=convert_quantity(
                    get_value(data, 'Solution volume [um]', None), 1 / 1000
                ),
            )
        ],
        layer=[
            LayerProperties(
                layer_type=get_value(data, 'Layer type', None, False),
                layer_material_name=get_value(data, 'Material name', None, False),
            )
        ],
        annealing=Annealing(
            temperature=get_value(data, 'Annealing temperature [°C]', None),
            time=convert_quantity(get_value(data, 'Annealing time [min]', None), 60),
        ),
        properties=SlotDieCoatingProperties(
            flow_rate=convert_quantity(data.get('Flow rate [ul/min]', None), 1 / 1000),
            slot_die_head_distance_to_thinfilm=get_value(data, 'Head gap [mm]'),
            slot_die_head_speed=get_value(data, 'Speed [mm/s]'),
        ),
        quenching=AirKnifeGasQuenching(
            air_knife_angle=get_value(data, 'Air knife angle [°]', None),
            bead_volume=get_value(data, 'Bead volume [mm/s]', None),
            drying_speed=get_value(data, 'Drying speed [cm/min]', None),
            air_knife_distance_to_thin_film=convert_quantity(
                data.get('Air knife gap [cm]', None), 10000
            ),
        ),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_slot_die_coating_{material}', archive)


def map_cleaning(i, j, lab_ids, data, upload_id):
    archive = HySprint_Cleaning(
        name='Cleaning',
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
    )
    return (f'{i}_{j}_cleaning', archive)


def map_substrate(data):
    archive = HySprint_Substrate(
        name='Substrate '
        + get_value(data, 'Sample dimension', '', False)
        + ' '
        + get_value(data, 'Substrate material', '', False)
        + ' '
        + get_value(data, 'Substrate conductive layer', '', False),
        solar_cell_area=get_value(data, 'Sample area [cm^2]', ''),
        substrate=get_value(data, 'Substrate material', '', False),
        conducting_material=[get_value(data, 'Substrate conductive layer', '', False)],
    )
    return archive


def map_evaporation(i, j, lab_ids, data, upload_id):
    archive = HySprint_Evaporation(
        name='evaporation ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=[
            LayerProperties(
                layer_type=get_value(data, 'Layer type', None, False),
                layer_material_name=get_value(data, 'Material name', None, False),
            )
        ],
    )

    if get_value(data, 'Organic', '', False).lower().startswith('n'):
        inorganic_evaporation = InorganicEvaporation(
            thickness=get_value(data, 'Thickness [nm]'),
            start_rate=get_value(data, 'Rate [angstrom/s]'),
            chemical_2=PubChemPureSubstanceSectionCustom(
                name=get_value(data, 'Material name', None, False), load_data=False
            ),
        )
        archive.inorganic_evaporation = [inorganic_evaporation]

    if get_value(data, 'Organic', '', False).lower().startswith('y'):
        organic_evaporation = OrganicEvaporation(
            thickness=get_value(data, 'Thickness [nm]'),
            start_rate=get_value(data, 'Rate [angstrom/s]'),
            temparature=[get_value(data, 'Temperature [°C]', None)] * 2
            if get_value(data, 'Temperature [°C]', None)
            else None,
            chemical_2=PubChemPureSubstanceSectionCustom(
                name=get_value(data, 'Material name', None, False), load_data=False
            ),
        )
        archive.organic_evaporation = [organic_evaporation]
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_evaporation_{material}', archive)


def map_sputtering(i, j, lab_ids, data, upload_id):
    archive = HySprint_Sputtering(
        name='sputtering ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=[
            LayerProperties(
                layer_type=get_value(data, 'Layer type', None, False),
                layer_material_name=get_value(data, 'Material name', None, False),
            )
        ],
    )
    process = SputteringProcess(
        thickness=get_value(data, 'Thickness [nm]'),
        gas_flow_rate=get_value(data, 'Gas flow rate [cm^3/min]'),
        rotation_rate=get_value(data, 'Rotation rate [rpm]'),
        power=get_value(data, 'Power [W]'),
        temperature=get_value(data, 'Temperature [°C]'),
        deposition_time=get_value(data, 'Deposition time [s]'),
        burn_in_time=get_value(data, 'Burn in time [s]'),
        pressure=get_value(data, 'Pressure [mbar]'),
        target_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Material name', None, False), load_data=False
        ),
        gas_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Gas', None, False), load_data=False
        ),
    )
    archive.processes = [process]
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_sputtering_{material}', archive)


def map_laser_scribing(i, j, lab_ids, data, upload_id):
    archive = HySprint_LaserScribing(
        name='laser scribing',
        positon_in_experimental_plan=i,
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        properties=LaserScribingProperties(
            laser_wavelength=get_value(data, 'Laser wavelength [nm]', None),
            laser_pulse_time=get_value(data, 'Laser pulse time [ps]', None),
            laser_pulse_frequency=get_value(data, 'Laser pulse frequency [kHz]', None),
            speed=get_value(data, 'Speed [mm/s]', None),
            fluence=get_value(data, 'Fluence [J/cm2]', None),
            power_in_percent=get_value(data, 'Power [%]', None),
        ),
    )

    return (f'{i}_{j}_laser_scribing', archive)

def map_atomic_layer_deposition(i, j, lab_ids, data, upload_id):

    archive = IRIS_AtomicLayerDeposition(
        name="atomic layer deposition " + get_value(data, "Material name", "", number = False),
        position_in_experimental_plan = i,
        description = get_value(data, "Notes", "", number = False),
        samples = [CompositeSystemReference(reference=get_reference(
            upload_id, f"{lab_id}.archive.json"), lab_id=lab_id) for lab_id in lab_ids],
        layer = [LayerProperties(layer_type=get_value(data, "Layer type", None, number = False),
                               layer_material_name=get_value(data, "Material name", None, number = False)
                               )])
        
    process = ALDPropertiesIris(
        source = get_value(data, "Source", None, number = False),
        thickness = get_value(data, "Thickness [nm]", None),
        temperature = get_value(data, "Temperature [°C]", None),
        rate = get_value(data, "Rate [A/s]", None),
        time = get_value(data, "Time [s]", None),
        number_of_cycles = get_value(data, "Number of cycles", None),
        material = ALDMaterial(
            material = PubChemPureSubstanceSectionCustom(name=get_value(data, "Precursor 1", None, number = False), load_data=False),
            pulse_duration = get_value(data, "Pulse duration 1 [s]", None),
            manifold_temperature = get_value(data, "Manifold temperature 1 [°C]", None),
            bottle_temperature = get_value(data, "Bottle temperature 1 [°C]", None)
            )
            
                               
        oxidizer = ALDMaterial(
            material = PubChemPureSubstanceSectionCustom(name=get_value(data, "Precursor 2", None, number = False), load_data=False),
            pulse_duration = get_value(data, "Pulse duration 2 [s]", None),
            manifold_temperature = get_value(data, "Manifold temperature 2 [°C]", None)
            )
        )
    archive.processes = [process]
    material = get_value(data, 'Material name', '', False)
    return (f"{i}_{j}_ALD_{material}", archive)


def map_generic(i, j, lab_ids, data, upload_id):
    archive = HySprint_Process(
        name=get_value(data, 'Name', '', False),
        positon_in_experimental_plan=i,
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
    )
    return (f'{i}_{j}_generic_process', archive)


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
        archives = [map_batch(sample_ids, batch_id, upload_id)]
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
            substrates.append((f'{i}_substrate', sub, map_substrate(sub)))

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
            archives.append(map_basic_sample(row, substrate_name, upload_id))

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
                    archives.append(map_cleaning(i, j, lab_ids, row, upload_id))

                if 'Laser Scribing' in col:
                    archives.append(map_laser_scribing(i, j, lab_ids, row, upload_id))

                if 'Generic Process' in col:  # move up
                    archives.append(map_generic(i, j, lab_ids, row, upload_id))

                if pd.isna(row.get('Material name')):
                    continue

                if 'Evaporation' in col:
                    archives.append(map_evaporation(i, j, lab_ids, row, upload_id))

                if 'Spin Coating' in col:
                    archives.append(map_spin_coating(i, j, lab_ids, row, upload_id))

                if 'Slot Die Coating' in col:
                    archives.append(map_sdc(i, j, lab_ids, row, upload_id))

                if 'Sputtering' in col:
                    archives.append(map_sputtering(i, j, lab_ids, row, upload_id))
                    
                if "ALD" in col:
                    archives.append(map_atomic_layer_deposition(i, j, lab_ids, row, upload_id))

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
