import sys
import types
from io import BytesIO, StringIO

import numpy as np

# ⬇️ Adjust this import to your real module path
from nomad_hysprint.schema_packages import HySprint_AbsPLMeasurement  # noqa: E402

# ---------- Test scaffolding ----------


class DummyArchive:
    """Mimics archive.m_context.raw_file(file_path, mode)."""

    class Ctx:
        def __init__(self, text_bytes: bytes):
            self._bytes = text_bytes

        def raw_file(self, _path, mode='rb'):
            if mode == 'rb':
                return BytesIO(self._bytes)
            elif mode == 'r':
                return StringIO(self._bytes.decode('cp1252', errors='replace'))
            raise AssertionError(f'unexpected mode: {mode}')

    def __init__(self, text: str):
        self.m_context = DummyArchive.Ctx(text.encode('cp1252', errors='replace'))


class DummyLogger:
    def __init__(self):
        self.debugs = []
        self.warnings = []

    def debug(self, *a, **k):
        self.debugs.append((a, k))

    def warning(self, *a, **k):
        self.warnings.append((a, k))


# ---------- Heuristic detector tests ----------


def test_is_multi_entry_abspl_file_true():
    text = (
        'Laser Intensity (suns)\t1.0\n\n'
        'Wavelength\tA\tB\tC\tD\tE\n'  # >4 tab-separated columns
        'nm\ta.u.\ta.u.\ta.u.\ta.u.\ta.u.\n'
        '400\t0.1\t0.2\t0.3\t0.4\t0.5\n'
    )
    arch = DummyArchive(text)
    assert HySprint_AbsPLMeasurement.is_multi_entry_abspl_file('ignored.txt', arch, DummyLogger()) is True


def test_is_multi_entry_abspl_file_false():
    text = (
        'Laser Intensity (suns)\t1.0\n\n'
        'Wavelength\tA\tB\n'  # <= 4 columns total
        'nm\ta.u.\ta.u.\n'
        '400\t0.1\t0.2\n'
    )
    arch = DummyArchive(text)
    assert HySprint_AbsPLMeasurement.is_multi_entry_abspl_file('ignored.txt', arch, DummyLogger()) is False


# ---------- normalize(): multi-entry branch ----------


def test_normalize_multi_entry_monkeypatched(monkeypatch, tmp_path):
    logger = DummyLogger()

    # Prepare a file that triggers the multi-entry heuristic (line startswith 'Wavelength' and >4 columns)
    text = (
        'Some header\tvalues\n'
        'Wavelength\tA\tB\tC\tD\tE\n'
        'nm\ta.u.\ta.u.\ta.u.\ta.u.\ta.u.\n'
        '400\t1\t2\t3\t4\t5\n'
        '500\t6\t7\t8\t9\t10\n'
    )
    arch = DummyArchive(text)

    # Create a fake module to satisfy
    fake_multi_mod = types.ModuleType('nomad_hysprint.schema_packages.file_parser.abspl_multi_parser')

    def fake_parse_multi(data_file, archive, logger_):
        # Return shapes that match your class expectations
        settings = {'laser_intensity_suns': 1.0}
        results = {'bandgap': 1.6}
        wavelengths = [400.0, 500.0]
        # multiple entries -> multiple spectra; your code ravel()s this
        lum_flux = [[1.0, 2.0], [3.0, 4.0]]
        return settings, results, wavelengths, lum_flux

    fake_multi_mod.parse_abspl_multi_entry_data = fake_parse_multi

    # Install the fake module so the import inside normalize() resolves to this
    sys.modules['nomad_hysprint.schema_packages.file_parser.abspl_multi_parser'] = fake_multi_mod

    m = HySprint_AbsPLMeasurement()
    m.data_file = 'whatever.abspl.txt'

    m.normalize(archive=arch, logger=logger)

    # Assert settings/results set via setattr
    assert hasattr(m.settings, 'laser_intensity_suns')
    assert m.settings.laser_intensity_suns == 1.0

    assert m.results and hasattr(m.results[0], 'bandgap')
    assert m.results[0].bandgap == 1.6

    # Wavelength and luminescence set; luminescence is raveled for multi
    np.testing.assert_allclose(m.results[0].wavelength, [400.0, 500.0])
    np.testing.assert_allclose(m.results[0].luminescence_flux_density, [1.0, 2.0, 3.0, 4.0])


# ---------- normalize(): single-entry branch ----------


def test_normalize_single_entry_monkeypatched(monkeypatch):
    logger = DummyLogger()

    # Prepare a file that **does not** trigger the multi-entry heuristic
    text = 'Header\tvalues\nWavelength\tA\tB\nnm\ta.u.\ta.u.\n400\t1\t2\n500\t3\t4\n'
    arch = DummyArchive(text)

    # Fake the single-entry parser:
    fake_single_mod = types.ModuleType('nomad_hysprint.schema_packages.file_parser.abspl_normalizer')

    def fake_parse_single(data_file, archive, logger_):
        settings = {'bias_voltage': 0.2}
        results = {'i_voc': 1.05}
        wavelengths = [400.0, 500.0]
        lum_flux = [10.0, 20.0]
        raw_counts = [100, 200]
        dark_counts = [1, 2]
        return settings, results, wavelengths, lum_flux, raw_counts, dark_counts

    fake_single_mod.parse_abspl_data = fake_parse_single
    sys.modules['nomad_hysprint.schema_packages.file_parser.abspl_normalizer'] = fake_single_mod

    m = HySprint_AbsPLMeasurement()
    m.data_file = 'single.abspl.txt'

    m.normalize(archive=arch, logger=logger)

    # Settings/results applied
    assert hasattr(m.settings, 'bias_voltage')
    assert m.settings.bias_voltage == 0.2

    assert m.results and hasattr(m.results[0], 'i_voc')
    assert m.results[0].i_voc == 1.05

    # Arrays set (no ravel for single-entry)
    assert m.results[0].wavelength.tolist() == [400.0, 500.0]
    assert m.results[0].luminescence_flux_density.tolist() == [10.0, 20.0]
    assert m.results[0].raw_spectrum_counts.tolist() == [100.0, 200.0]
    assert m.results[0].dark_spectrum_counts.tolist() == [1.0, 2.0]
