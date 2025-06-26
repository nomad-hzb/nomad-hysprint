from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.solar_cell_batch_mapping import get_reference, get_value
from baseclasses.solution import SolutionChemical
from nomad.datamodel.metainfo.basesections import CompositeSystemReference

from nomad_hysprint.schema_packages.ink_recycling_package import (
    InkRecycling_Filter,
    InkRecycling_FunctionalLiquid,
    InkRecycling_Ink,
    InkRecycling_Results,
)


def map_ink_recycling(i, j, lab_ids, data, upload_id, ink_recycling_class):
    ink_recycling_archive = ink_recycling_class()

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
                chemical_volume=get_value(data, f'{solvent} volume [ml]', None, unit='mL'),
            )
        )

    for solute in sorted(set(solutes)):
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solute} name', None, False),
                    load_data=False,
                ),
                chemical_mass=get_value(data, f'{solute} amount [g]', None, unit='g'),
                amount_mol=get_value(data, f'{solute} moles [mol]', None, unit='mol'),
                concentration_mol=get_value(data, f'{solute} concentration [M]', None, unit='M'),
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

    ink = InkRecycling_Ink(solvent=final_solvents, solute=final_solutes, precursor=final_precursors)
    ink_recycling_archive.ink = ink

    ink_recycling_archive.FL = InkRecycling_FunctionalLiquid(
        name=get_value(data, 'Functional liquid name', None, False),
        volume=get_value(data, 'Functional liquid volume [ml]', None, unit='mL'),
        dissolving_temperature=get_value(data, 'Dissolving temperature [°C]', None, unit='°C'),
    )

    ink_recycling_archive.filter = InkRecycling_Filter(
        filter_type=get_value(data, 'Filter material', None, False),
        size=get_value(data, 'Filter size [mm]', None, unit='mm'),
        weight=get_value(data, 'Filter weight [g]', None, unit='g'),
    )

    ink_recycling_archive.recycling_results = InkRecycling_Results(
        recovered_solute=get_value(data, 'Recovered solute [g]', None, unit='g'),
        yield_=get_value(data, 'Yield [%]', None, True),
    )

    ink_recycling_archive.samples = [
        CompositeSystemReference(
            reference=get_reference(upload_id, f'{lab_id}.archive.json'),
            lab_id=lab_id,
        )
        for lab_id in lab_ids
    ]

    ink_recycling_archive.description = get_value(data, 'Notes', None, False)

    return (f'{i}_{j}_ink_recycling', ink_recycling_archive)
