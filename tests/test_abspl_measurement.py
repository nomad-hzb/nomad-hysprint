import numpy as np
from nomad.datamodel import EntryArchive
from nomad_luqy_plugin import AbsPLMeasurementELN


def test_basic_parser_on_gaas():
    archive = EntryArchive()
    m = AbsPLMeasurementELN()
    m.data_file = 'tests/data/GaAs5_Large_Spot_center.txt'
    m.normalize(archive, logger=archive.logger)

    r = m.results[0]
    assert r.luqy > 0
    assert r.bandgap > 1.3
    assert len(r.wavelength) > 10
    assert len(r.raw_spectrum_counts) == len(r.wavelength)


def test_basic_parser_on_silicon():
    archive = EntryArchive()
    m = AbsPLMeasurementELN()
    m.data_file = 'tests/data/0_1_0-ecf314iynbrwtd33zkk5auyebh.txt'
    m.normalize(archive, logger=archive.logger)

    r = m.results[0]
    assert r.luqy > 0
    assert r.bandgap > 2.0
    assert len(r.wavelength) > 10
    assert isinstance(r.luminescence_flux_density, np.ndarray)
