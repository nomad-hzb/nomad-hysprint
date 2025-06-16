"""Process sequences for the excel creator.

This module contains predefined process sequences for creating excel templates
for different types of perovskite solar cell fabrication processes.

Each sequence is defined as a dictionary with the following structure:
{
    "name": "Name of the sequence",
    "description": "Detailed description of what this sequence is for",
    "author": "Name of the author/team",
    "sequence": [
        {"process": "Process Name", "config": {...}},
        ...
    ]
}
"""


# Complete test sequence with all implemented processes and configurations
TEST_SEQUENCE = {
    "name": "Test Process",
    "description": "Complete test sequence including vacuum and gas quenching, carbon paste, GAVD, and various coating methods",
    "author": "Test Team",
    "sequence": [
        {"process": "Experiment Info"},
        {'process': 'Laser Scribing'},
        {'process': 'Cleaning O2-Plasma', 'config': {'solvents': 2}},
        {'process': 'Cleaning UV-Ozone'},
        {'process': 'Dip Coating'},
        {'process': 'Spin Coating', 'config': {
            'solvents': 2, 'solutes': 2, 'spinsteps': 2, 'antisolvent': True }},
        {'process': 'Spin Coating', 'config': {
            'solvents': 1, 'solutes': 1, 'spinsteps': 1, 'vacuumquenching': True }},
        {'process': 'Spin Coating', 'config': {
            'solvents': 1, 'solutes': 1, 'spinsteps': 1, 'gasquenching': True }},
        {'process': 'Slot Die Coating'},    
        {'process': 'Inkjet Printing', 'config': {'annealing': True, 'gavd': True}},
        {'process': 'Evaporation', 'config': {'carbon_paste': True}},
        {'process': 'Sputtering'},
        {'process': 'ALD'},
        {'process': 'Generic Process'}
    ]
}

# Reduced test sequence with basic process types
REDUCED_TEST_SEQUENCE = {
    "name": "Reduced Test Process",
    "description": "A basic test sequence that includes fundamental process types for testing",
    "author": "Test Team",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 4}},
        {"process": "Cleaning UV-Ozone", "config": {"solvents": 2}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},
        {"process": "Dip Coating", "config": {"solvents": 2, "solutes": 5, "spinsteps": 2, "antisolvent": True}},
        {"process": "Slot Die Coating", "config": {"solvents": 1, "solutes": 2, "spinsteps": 1, "antisolvent": False}},
        {"process": "Inkjet Printing", "config": {"solvents": 1, "solutes": 2, "spinsteps": 1, "antisolvent": False}},
        {"process": "Evaporation"},
        {"process": "Sublimation"},
        {"process": "Seq-Evaporation"},
        {"process": "Co-Evaporation"},
        {"process": "Sputtering"},
        {"process": "Laser Scribing"},
        {"process": "ALD"},
        {"process": "Annealing"},
        {"process": "Generic Process"}
    ]
}

EIKE_SEQUENCE = {
    "name": "Eike Process",
    "description": "Standard process for perovskite solar cells with PEDOT-PSS or SAM",
    "author": "Eike",
    "sequence": [
        {'process': 'Experiment Info'},
        {'process': 'Cleaning UV-Ozone', 'config': {'solvents': 1}},
        {
            'process': 'Spin Coating',
            'config': {
                'solvents': 1,  # PEDOT-PSS or SAM
                'solutes': 1,
                'spinsteps': 2,
                'antisolvent': False,
            },
        },
        {
            'process': 'Spin Coating',
            'config': {
                'solvents': 1,  # Washing
                'solutes': 1,
                'spinsteps': 2,
                'antisolvent': False,
            },
        },
        {
            'process': 'Spin Coating',
            'config': {
                'solvents': 2,  # Perovskite
                'solutes': 6,
                'spinsteps': 2,
                'antisolvent': False,
            },
        },
        {'process': 'Evaporation'},  # C60
        {'process': 'ALD'},  # SnO2
        {'process': 'Sputtering'},  # TCO
        {'process': 'Evaporation'},  # BCP
        {'process': 'Evaporation'},  # Cupper
    ]
}

OSAIL_SEQUENCE = {
    "name": "Osail's Bypass Process",
    "description": "Bypass process with PEDOT-PSS and multiple evaporation steps",
    "author": "Osail",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 4}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEDOT-PSS
        {"process": "Evaporation"},  # BC60
        {"process": "Evaporation"},  # BCP
        {"process": "Evaporation"}   # Aluminium
    ]
}

ANNE_SEQUENCE = {
    "name": "Anne's Bypass Process",
    "description": "Bypass process with PEDOT-PSS/SAM and perovskite layers",
    "author": "Anne",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning UV-Ozone", "config": {"solvents": 3}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEDOT-PSS or SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 5, "spinsteps": 1, "antisolvent": True}},  # Perovskite
        {"process": "Evaporation"},  # BC60
        {"process": "Evaporation"},  # BCP
        {"process": "Evaporation"}   # Cupper
    ]
}

PRINTER_SEQUENCE = {
    "name": "Printer Process",
    "description": "Process using inkjet printing for perovskite deposition",
    "author": "Printer Team",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEDOT-PSS or SAM
        {"process": "Inkjet Printing", "config": {"solvents": 3, "solutes": 5, "antisolvent": True}},  # Perovskite
        {"process": "Evaporation"},  # BC60
        {"process": "Evaporation"},  # BCP
        {"process": "Evaporation"}   # Cupper
    ]
}

KEVIN_SEQUENCE = {
    "name": "Kevin Prince Process",
    "description": "Complex process with multiple layers including NiOx and all-inorganic perovskite",
    "author": "Kevin Prince",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # NiOx
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 8, "spinsteps": 2, "antisolvent": True}},  # all-inorganic PK
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEAI Treatment
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PCBM
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEIE
        {"process": "ALD"},  # SnOx
        {"process": "Sputtering"}  # SnOx
    ]
}

DANIEL_SPINBOT_SEQUENCE = {
    "name": "Daniel Spinbot Process",
    "description": "Spinbot process with SAM and passivation layers",
    "author": "Daniel",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 5, "spinsteps": 2, "antisolvent": True}},  # PSK
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 2, "spinsteps": 1, "antisolvent": False}},  # Passivation Sol
        {"process": "Evaporation"},  # Passivation Evap
        {"process": "Evaporation"},  # C60
        {"process": "Evaporation"},  # BCP
        {"process": "ALD"},  # SnO2
        {"process": "Evaporation"}   # Ag
    ]
}

SPINBOT_GASQUENCHED_SEQUENCE = {
    "name": "Spinbot Gas-Quenched Process",
    "description": "Modified spinbot process using gas quenching",
    "author": "Spinbot Team",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1}},  # SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 5, "spinsteps": 2, "gasquenching": True}},  # PSK
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 2, "spinsteps": 1}},  # Passivation Sol
        {"process": "Evaporation"},  # Passivation Evap
        {"process": "Evaporation"},  # C60
        {"process": "Evaporation"},  # BCP
        {"process": "Evaporation"}   # Ag
    ]
}

PHILIPPE_SEQUENCE = {
    "name": "Philippe Process",
    "description": "Process with FTO and multiple transport layers",
    "author": "Philippe",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},  # FTO
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # NiOx
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 4, "spinsteps": 2, "antisolvent": True}},  # Perovskite
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PCBM
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # BCP
        {"process": "Evaporation"}
    ]
}

HYBRID_SEQUENCE = {
    "name": "Hybrid Process",
    "description": "Hybrid process combining inorganic and organic perovskites",
    "author": "Hybrid Team",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
        {"process": "Seq-Evaportation", "config": {"materials": 2}},  # PSK inorganic
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 3, "spinsteps": 1, "antisolvent": False}},  # PSK organic
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 2, "spinsteps": 1, "antisolvent": False}},  # Passivation Sol
        {"process": "Evaporation"},  # Passivation Evap
        {"process": "Evaporation"},  # C60
        {"process": "Evaporation"},  # BCP
        {"process": "ALD"},          # SnO2
        {"process": "Evaporation"}   # Ag
    ]
}

SOP_SEQUENCE = {
    "name": "Standard Operating Procedure",
    "description": "Standard process following established operating procedures",
    "author": "SOP Team",
    "sequence": [
        {"process": "Experiment Info"},
        {"process": "Cleaning O2-Plasma", "config": {"solvents": 3}},
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # NiO
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
        {"process": "Spin Coating", "config": {"solvents": 2, "solutes": 6, "spinsteps": 2, "antisolvent": True}},  # PSK
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PEAI
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # PCBM
        {"process": "Spin Coating", "config": {"solvents": 1, "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # BCP
        {"process": "Evaporation"}  # Ag
    ]
}

# Dictionary of all available sequences
AVAILABLE_SEQUENCES = {
    "test": TEST_SEQUENCE,
    "reduced": REDUCED_TEST_SEQUENCE,
    "eike": EIKE_SEQUENCE,
    "osail": OSAIL_SEQUENCE,
    "anne": ANNE_SEQUENCE,
    "printer": PRINTER_SEQUENCE,
    "kevin": KEVIN_SEQUENCE,
    "daniel": DANIEL_SPINBOT_SEQUENCE,
    "gasquenched": SPINBOT_GASQUENCHED_SEQUENCE,
    "philippe": PHILIPPE_SEQUENCE,
    "hybrid": HYBRID_SEQUENCE,
    "sop": SOP_SEQUENCE
}
