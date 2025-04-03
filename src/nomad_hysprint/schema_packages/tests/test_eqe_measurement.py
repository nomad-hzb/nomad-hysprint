import pytest
import numpy as np
from nomad.datamodel import EntryArchive
from nomad_hysprint.schema_packages.parsers.eqe_parser import HySprint_EQEmeasurement
from nomad_hysprint.schema_packages.file_parser.eqe_parser import read_file, read_file_multiple


@pytest.fixture
def mock_eqe_file(tmp_path):
    """Creates a mock EQE file for testing"""
    file_path = tmp_path / 'test_eqe.txt'
    file_path.write_text('[Header]\nPhoton Energy: 1.2 1.5 1.8\nEQE: 0.8 0.85 0.9')
    return str(file_path)


def test_eqe_parser_valid(mock_eqe_file, mocker):
    parser = HySprint_EQEmeasurement()
    archive = EntryArchive()

    # Mock file reading functions
    mocker.patch(
        'nomad_hysprint.schema_packages.file_parser.eqe_parser.read_file',
        return_value={'photon_energy': np.array([1.2, 1.5, 1.8]), 'intensity': np.array([0.8, 0.85, 0.9])},
    )

    parser.data_file = mock_eqe_file
    parser.normalize(archive, logger=None)

    assert len(parser.eqe_data) > 0  # Ensure data was processed
    assert parser.eqe_data[0].photon_energy_array[0] == 1.2  # Check first value
    assert parser.eqe_data[0].eqe_array[0] == 0.8  # Check first EQE value


def test_eqe_parser_empty_file(tmp_path):
    """Test that an empty file raises an error"""
    empty_file = tmp_path / 'empty_eqe.txt'
    empty_file.write_text('')

    parser = HySprint_EQEmeasurement()
    archive = EntryArchive()

    parser.data_file = str(empty_file)

    with pytest.raises(ValueError, match='File is empty or invalid'):
        parser.normalize(archive, logger=None)


def test_eqe_parser_malformed_file(tmp_path):
    """Test a malformed file that doesn't match expected format"""
    bad_file = tmp_path / 'bad_eqe.txt'
    bad_file.write_text('This is not an EQE file format')

    parser = HySprint_EQEmeasurement()
    archive = EntryArchive()

    parser.data_file = str(bad_file)

    with pytest.raises(Exception):  # Adjust based on actual exceptions
        parser.normalize(archive, logger=None)


def test_eqe_parser_bandgap_calculation(mocker):
    """Test if the bandgap calculation is performed correctly"""
    parser = HySprint_EQEmeasurement()
    archive = EntryArchive()

    mocker.patch(
        'nomad_hysprint.schema_packages.file_parser.eqe_parser.read_file',
        return_value={'photon_energy': np.array([1.2, 1.5, 1.8]), 'intensity': np.array([0.8, 0.85, 0.9])},
    )

    parser.data_file = 'test_eqe.txt'
    parser.normalize(archive, logger=None)

    assert hasattr(parser, 'eqe_data')
    assert len(parser.eqe_data) > 0
    assert np.isfinite(parser.eqe_data[0].bandgap_eqe.magnitude)


def test_eqe_parser_encoding(mocker, tmp_path):
    """Test different encodings"""
    eqe_file = tmp_path / 'test_eqe_utf16.txt'
    eqe_file.write_text('[Header]\nPhoton Energy: 1.2 1.5 1.8\nEQE: 0.8 0.85 0.9', encoding='utf-16')

    parser = HySprint_EQEmeasurement()
    archive = EntryArchive()

    parser.data_file = str(eqe_file)

    mocker.patch('nomad_hysprint.schema_packages.file_parser.eqe_parser.get_encoding', return_value='utf-16')

    parser.normalize(archive, logger=None)

    assert len(parser.eqe_data) > 0  # Ensure data was extracted
