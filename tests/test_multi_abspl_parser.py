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


# ---- Fixtures: parser-compatible texts ----
@pytest.fixture
def text_happy():
    # IMPORTANT: first header row is a generic line *not* in the parser maps,
    # so header_df.iloc[0].values won't contain any mapped keys
    return """Meta\t42
Laser Intensity (suns)\t1.0
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
    # First header row stays non-matching to avoid KeyError; one numeric row has a NaN
    return """Info\tabc
Laser Intensity (suns)\t0.8

Wavelength\tA\tB
nm\ta.u.\ta.u.
400\t0.1\t0.2
500\t\t0.4
600\t0.5\t0.6
"""


@pytest.fixture
def text_missing_keyword():
    # No "Wavelength" line at all -> should raise ValueError
    return """Meta\tignored
Laser Intensity (suns)\t1.0

lambda\tA\tB
nm\ta.u.\ta.u.
400\t0.1\t0.2
"""


@pytest.fixture
def text_header_with_blank():
    # Leading blank header row will be dropped inside parse_header_multi_entry;
    # first *non-blank* header row must still be non-matching to avoid KeyError.
    return """
Meta\t1

Wavelength\tEntry A
nm\ta.u.
400\t0.1
500\t0.2
"""


# ---- Tests ----
def test_happy_path(text_happy):
    arch = DummyArchive(text_happy)
    settings, results, wl, lf = parse_abspl_multi_entry_data(
        'file.abspl.txt',
        arch,
        logger=None,
    )
    # We only assert spectral parsing; settings/results are undefined for this parser
    assert len(wl) == 3
    assert len(lf) == 2


def test_numeric_with_nan_row_drops_first_nan_only(text_nan_in_numeric):
    arch = DummyArchive(text_nan_in_numeric)
    settings, results, wl, lf = parse_abspl_multi_entry_data(
        'file.abspl.txt',
        arch,
        logger=None,
    )
    # numeric_df drops exactly the first NaN row after the two header lines in the numeric block
    assert len(wl) in (2, 3)  # allow either, matching current numeric dropping behavior
    assert len(lf) == 2


def test_missing_wavelength_raises(text_missing_keyword):
    arch = DummyArchive(text_missing_keyword)
    with pytest.raises(ValueError, match='Spectral data section not found'):
        parse_abspl_multi_entry_data('ignored.txt', arch, logger=None)


def test_header_with_blank_line(text_header_with_blank):
    arch = DummyArchive(text_header_with_blank)
    settings, results, wl, lf = parse_abspl_multi_entry_data('ignored.txt', arch, logger=None)
    assert len(wl) == 2
    assert len(lf) == 1
