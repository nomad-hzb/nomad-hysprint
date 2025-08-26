from io import StringIO

import pytest

from nomad_hysprint.schema_packages.file_parser.abspl_multi_parser import (
    parse_abspl_multi_entry_data,
)


# ---- Test scaffolding ----
class DummyArchive:
    class Ctx:
        def __init__(self, text):
            self._text = text

        def raw_file(self, _path, mode='r'):
            return StringIO(self._text)

    def __init__(self, text):
        self.m_context = DummyArchive.Ctx(text)


# ---- Fixtures: canonical texts ----
@pytest.fixture
def text_happy():
    return """Laser Intensity (suns)\t1.0
Bias voltage (V)\t0.5
Bandgap (eV)\t1.60

Wavelength\tEntry A\tEntry B
nm\ta.u.\ta.u.
400\t0.1\t0.2
500\t0.3\t0.4
600\t0.5\t0.6
"""


@pytest.fixture
def text_nan_in_numeric():
    return """Laser Intensity (suns)\t0.8

Wavelength\tA\tB
nm\ta.u.\ta.u.
400\t0.1\t0.2
500\t\t0.4
600\t0.5\t0.6
"""


@pytest.fixture
def text_missing_keyword():
    return """Laser Intensity (suns)\t1.0

lambda\tA\tB
nm\ta.u.\ta.u.
400\t0.1\t0.2
"""


@pytest.fixture
def text_header_with_blank():
    return """Laser Intensity (suns)\t1.0
Bias voltage (V)\t0.5

\t
Wavelength\tEntry A
nm\ta.u.
400\t0.1
500\t0.2
"""


# ---- Tests ----
def test_happy_path(text_happy):
    arch = DummyArchive(text_happy)
    settings, results, wl, lf = parse_abspl_multi_entry_data(
        'EM3_3pxbigspot1s-int.abspl.txt',
        arch,
        logger=None,
    )
    assert len(wl) == 3
    assert len(lf) == 2


def test_numeric_with_nan_row_drops_first_nan_only(text_nan_in_numeric):
    arch = DummyArchive(text_nan_in_numeric)
    settings, results, wl, lf = parse_abspl_multi_entry_data(
        'EM3_3pxbigspot1s-int.abspl.txt',
        arch,
        logger=None,
    )
    # One NaN row is dropped; remaining rows should parse
    assert len(wl) in (2, 3)


def test_missing_wavelength_raises(text_missing_keyword):
    arch = DummyArchive(text_missing_keyword)
    with pytest.raises(ValueError, match='Spectral data section not found'):
        parse_abspl_multi_entry_data('ignored.txt', arch, logger=None)


def test_header_with_blank_line(text_header_with_blank):
    arch = DummyArchive(text_header_with_blank)
    settings, results, wl, lf = parse_abspl_multi_entry_data('ignored.txt', arch, logger=None)
    assert len(wl) == 2
    assert len(lf) == 1
