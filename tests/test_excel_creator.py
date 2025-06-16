"""Tests for the Excel template creator functionality."""

import os.path

import pytest

from utils import set_monkey_patch
from utils.excel_creator.excel_template_creator import create_excel
from utils.excel_creator.process_sequences import AVAILABLE_SEQUENCES


@pytest.fixture
def temp_excel_path(tmp_path):
    """Fixture to provide a temporary path for Excel files."""
    return tmp_path / 'test_template.xlsx'


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """Set up test environment."""
    set_monkey_patch(monkeypatch)


@pytest.fixture
def sequence_name():
    """Get a test sequence name."""
    return next(iter(AVAILABLE_SEQUENCES))


def test_create_excel_basic(tmp_path, sequence_name, monkeypatch):
    """Test basic Excel creation with default settings."""
    output_path = tmp_path / 'test_template.xlsx'
    create_excel(sequence_name, str(output_path))
    assert output_path.exists()


def test_create_excel_all_sequences(tmp_path, monkeypatch):
    """Test Excel creation with all available sequences."""
    for name in AVAILABLE_SEQUENCES:
        output_path = tmp_path / f'{name}_template.xlsx'
        create_excel(name, str(output_path))
        assert output_path.exists()


def test_create_excel_with_and_without_test_values(tmp_path, sequence_name, monkeypatch):
    """Test Excel creation with and without test values."""
    output_path = tmp_path / 'template.xlsx'

    # With test values (default)
    create_excel(sequence_name, str(output_path), is_testing=True)
    assert output_path.exists()
    with_tests_size = os.path.getsize(output_path)

    # Without test values
    create_excel(sequence_name, str(output_path), is_testing=False)
    assert output_path.exists()
    without_tests_size = os.path.getsize(output_path)

    # Files should be different sizes due to test values
    assert with_tests_size != without_tests_size


def test_create_excel_invalid_sequence(monkeypatch):
    """Test error handling for invalid sequence names."""
    with pytest.raises(ValueError) as exc_info:
        create_excel('invalid_sequence_name')
    assert 'Unknown sequence' in str(exc_info.value)


def test_create_excel_default_output(tmp_path, sequence_name, monkeypatch):
    """Test Excel creation with default output path."""
    # Change to temp directory for testing default output
    monkeypatch.chdir(tmp_path)
    create_excel(sequence_name)

    # Check if a file was created
    excel_files = list(tmp_path.glob('*.xlsx'))
    assert len(excel_files) == 1


def test_create_excel_file_location(tmp_path, sequence_name, monkeypatch):
    """Test that Excel files are created in the correct location."""
    # Test with explicit path
    explicit_path = tmp_path / 'subfolder' / 'test.xlsx'
    os.makedirs(explicit_path.parent, exist_ok=True)
    create_excel(sequence_name, str(explicit_path))
    assert explicit_path.exists()

    # Test with default path (should create in current directory)
    monkeypatch.chdir(tmp_path)
    create_excel(sequence_name)
    excel_files = list(tmp_path.glob('*.xlsx'))
    assert len(excel_files) == 1
    # Check if filename follows expected pattern (contains date)
    assert any(f.name.startswith('20') for f in excel_files)
