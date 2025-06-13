from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.solar_cell_batch_mapping import get_value
from baseclasses.solution import SolutionChemical

from nomad_hysprint.schema_packages.ink_recycling_package import (
    InkRecycling_Filter,
    InkRecycling_FunctionalLiquid,
    InkRecycling_Ink,
    InkRecycling_Results,  # Corrected from InkRecycling_RecyclingResults if that was a typo
)


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
        type=get_value(
            data, 'Filter material', None, False
        ),  # 'type' is a reserved keyword, ensure schema uses a different name e.g. 'filter_type'
        size=get_value(data, 'Filter size [mm]', None, unit='mm'),
    )
    return archive


def map_results(data):
    archive = InkRecycling_Results(  # Corrected from InkRecycling_RecyclingResults if that was a typo
        recovered_solute=get_value(data, 'Recovered solute [g]', None, unit='g'),
        yield_=get_value(data, 'Yield [%]', None, True),
    )
    return archive
