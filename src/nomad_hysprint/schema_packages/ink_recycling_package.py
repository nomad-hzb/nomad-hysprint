import numpy as np
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection
from baseclasses import BaseMeasurement
from hysprint.schema_packages.hysprint_package import HySprint_Ink

# Initialize the schema package
m_package = SchemaPackage()



class HySprint_Filter(ArchiveSection):
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


class HySprint_FunctionalLiquid(ArchiveSection):
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


class HySprint_RecyclingResults(ArchiveSection):
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


class HySprint_RecyclingExperiment(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users'],
        )
    )
    
    ink = SubSection(section_def=HySprint_Ink)

    FL = SubSection(
        section_def=HySprint_FunctionalLiquid,
    )

    filter = SubSection(
        section_def=HySprint_Filter,
    )

    results = SubSection(
        section_def=HySprint_RecyclingResults,
    )


m_package.__init_metainfo__()
