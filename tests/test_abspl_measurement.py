import shutil
from pathlib import Path

import numpy as np
import pytest
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad_luqy_plugin.schema_packages.schema_package import (
    AbsPLMeasurementELN,
    parse_abspl_data,
)


class DummyLogger:
    def debug(self, msg, **kwargs):
        print('DEBUG:', msg, kwargs)

    def warning(self, msg):
        print('WARNING:', msg)

    def info(self, msg):
        print('INFO:', msg)

    def error(self, msg):
        print('ERROR:', msg)


@pytest.mark.parametrize(
    'filename,expected_bandgap',
    [
        ('GaAs5_Large_Spot_center.txt', 1.424),
        ('0_1_0-ecf314iynbrwtd33zkk5auyebh.txt', 2.095),
    ],
)
def test_parser(tmp_path, filename, expected_bandgap):
    # Prepare temp file
    src = Path('tests/data') / filename
    dst = tmp_path / filename
    shutil.copy(src, dst)

    archive = EntryArchive()
    archive.metadata = EntryMetadata()
    archive.metadata.entry_name = 'Test Entry'

    class DummyContext:
        def raw_file(self, name, mode='r'):
            return open(dst, mode)

    archive.m_context = DummyContext()

    settings, results, wl, flux, raw, dark = parse_abspl_data(
        data_file=filename, archive=archive, logger=DummyLogger()
    )

    assert isinstance(settings, dict)
    assert isinstance(results, dict)
    assert isinstance(wl, list) and wl
    print('Available result keys:', results.keys())
    key = 'Bandgap (eV)' if 'Bandgap (eV)' in results else 'bandgap'
    assert np.isclose(results[key], expected_bandgap, atol=0.01)


@pytest.mark.parametrize(
    'filename',
    [
        'GaAs5_Large_Spot_center.txt',
        '0_1_0-ecf314iynbrwtd33zkk5auyebh.txt',
    ],
)
def test_normalize(tmp_path, filename):
    src = Path('tests/data') / filename
    dst = tmp_path / filename
    shutil.copy(src, dst)

    measurement = AbsPLMeasurementELN()
    measurement.data_file = filename

    archive = EntryArchive()
    archive.metadata = EntryMetadata()
    archive.metadata.entry_name = 'Test Entry'
    archive.data = measurement

    class DummyContext:
        def raw_file(self, name, mode='r'):
            return open(dst, mode)

    archive.m_context = DummyContext()

    measurement.normalize(archive=archive, logger=DummyLogger())

    assert measurement.settings is not None
    assert measurement.results is not None
    result = measurement.results[0]
    assert hasattr(result.wavelength, 'magnitude')
    assert isinstance(result.wavelength.magnitude, np.ndarray)
    assert result.luminescence_flux_density.size > 0
    assert result.raw_spectrum_counts.size > 0
    assert result.dark_spectrum_counts.size > 0
