import numpy as np
from baseclasses import BaseMeasurement
from baseclasses.solution import Solution, SolutionChemical
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

# Initialize the schema package
m_package = SchemaPackage()


class InkRecycling_Filter(ArchiveSection):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
            properties=dict(order=['type', 'size', 'weight']),
        )
    )
    type = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))
    size = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'),
    )
    weight = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
    )


class InkRecycling_FunctionalLiquid(ArchiveSection):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
            properties=dict(order=['name', 'volume', 'dissolving_temperature']),
        )
    )
    name = Quantity(type=str, a_eln=dict(component='StringEditQuantity'))
    volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )
    dissolving_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )


class InkRecycling_Results(ArchiveSection):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
        )
    )
    recovered_solute = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
    )
    yield_ = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity', props=dict(minValue=0)),
    )


class InkRecycling_Ink(Solution, ArchiveSection):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
        )
    )
    precursor = SubSection(section_def=SolutionChemical, repeats=True)


class InkRecycling_RecyclingExperiment(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'steps', 'samples', 'atmosphere', 'instruments', 'method', 'results'],
        )
    )

    ink = SubSection(section_def=InkRecycling_Ink)

    FL = SubSection(
        section_def=InkRecycling_FunctionalLiquid,
    )

    filter = SubSection(
        section_def=InkRecycling_Filter,
    )

    recycling_results = SubSection(
        section_def=InkRecycling_Results,
    )


m_package.__init_metainfo__()
