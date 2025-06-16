"""Excel creator for process sequences.

This module provides functionality to create Excel templates for 
different perovskite solar cell fabrication processes.
"""

import argparse

from experiment_excel_builder import ExperimentExcelBuilder
from process_sequences import AVAILABLE_SEQUENCES


def create_excel(sequence_name, output_path=None, is_testing=True):
    """Create an Excel template for a specific process sequence.
    
    Args:
        sequence_name (str): Name of the sequence to use
        output_path (str, optional): Path to save the Excel file. Defaults to None.
        is_testing (bool, optional): Whether to include test values. Defaults to True.
    
    Raises:
        ValueError: If the sequence name is not found
    """
    if sequence_name not in AVAILABLE_SEQUENCES:
        raise ValueError(
            f"Unknown sequence '{sequence_name}'. Available sequences: {list(AVAILABLE_SEQUENCES.keys())}"
        )
    
    sequence = AVAILABLE_SEQUENCES[sequence_name]["sequence"]
    builder = ExperimentExcelBuilder(sequence, is_testing)
    builder.build_excel()
    if output_path:
        builder.save(output_path)
    else:
        builder.save()

def main():
    """Command line interface for creating Excel templates."""
    parser = argparse.ArgumentParser(description='Create an Excel template for a process sequence')
    parser.add_argument('sequence', choices=list(AVAILABLE_SEQUENCES.keys()),
                      help='Name of the sequence to use')
    parser.add_argument('--output', '-o', help='Output path for the Excel file')
    parser.add_argument('--no-test', action='store_false', dest='test',
                      help='Exclude test values from the template')
    
    args = parser.parse_args()
    create_excel(args.sequence, args.output, not args.no_test)

if __name__ == '__main__':
    main()
