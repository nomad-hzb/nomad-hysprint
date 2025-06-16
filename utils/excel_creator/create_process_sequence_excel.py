from experiment_excel_builder import ExperimentExcelBuilder

# Define the sequence of processes with custom configurations

# # Test process with all processes
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning O2-Plasma", "config": {"solvents": 4}},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 2}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Dip Coating", "config":  {"solvents": 2,
#                                             "solutes": 5, "spinsteps": 2, "antisolvent": True}},
#     {"process": "Slot Die Coating", "config":  {"solvents": 1, "solutes": 2,
#                                             "spinsteps": 1, "antisolvent": False}},
#     {"process": "Inkjet Printing", "config":  {"solvents": 1, "solutes": 2,
#                                             "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},
#     {"process": "Sublimation"},
#     {"process": "Seq-Evaporation"},
#     {"process": "Co-Evaporation"},
#     {"process": "Sputtering"},
#     {"process": "Laser Scribing"},
#     {"process": "ALD"},
#     {"process": "Annealing"},
#     {"process": "Generic Process"},
# ]

# # Micha's test
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning O2-Plasma", "config": {"solvents": 1}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": True}},
#     {"process": "Inkjet Printing", "config":  {"solvents": 1, "solutes": 2,
#                                             "spinsteps": 1, "antisolvent": False}},
#     {"process": "ALD"},
#     {"process": "Laser Scribing"},
#      {"process": "Slot Die Coating", "config":  {"solvents": 1, "solutes": 2,
#                                              "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},
#     {"process": "Generic Process"},

# # Osail's bypass
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning O2-Plasma", "config": {"solvents": 4}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PEDOT-PSS
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},  # BC60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"},  # Aluminium
#     ]

# # Anne's bypass
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 3}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PEDOT-PSS or SAM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # Perovskite
#                                             "solutes": 5, "spinsteps": 1, "antisolvent": True}},
#     {"process": "Evaporation"},  # BC60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"},  # Cupper
#     ]

# # Printer process
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PEDOT-PSS or SAM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Inkjet Printing", "config":  {"solvents": 3,  # Perovskite
#                                             "solutes": 5, "antisolvent": True}},
#     {"process": "Evaporation"},  # BC60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"},  # Cupper
#     ]

# # Eike process
# process_sequence = [
#     {'process': 'Experiment Info'},
#     {'process': 'Cleaning UV-Ozone', 'config': {'solvents': 1}},
#     {
#         'process': 'Spin Coating',
#         'config': {
#             'solvents': 1,  # PEDOT-PSS or SAM
#             'solutes': 1,
#             'spinsteps': 2,
#             'antisolvent': False,
#         },
#     },
#     {
#         'process': 'Spin Coating',
#         'config': {
#             'solvents': 1,  # Washing
#             'solutes': 1,
#             'spinsteps': 2,
#             'antisolvent': False,
#         },
#     },
#     {
#         'process': 'Spin Coating',
#         'config': {
#             'solvents': 2,  # Perovskite
#             'solutes': 6,
#             'spinsteps': 2,
#             'antisolvent': False,
#         },
#     },
#     {
#         'process': 'Spin Coating',
#         'config': {
#             'solvents': 1,  # Interlayer
#             'solutes': 1,
#             'spinsteps': 1,
#             'antisolvent': False,
#         },
#     },
#     {'process': 'Evaporation'},  # C60
#     {'process': 'ALD'},  # SnO2
#     {'process': 'Sputtering'},  # TCO
#     {'process': 'Evaporation'},  # BCP
#     {'process': 'Evaporation'},  # Cupper
# ]

# # Kevin Prince
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # NiOx
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # SAM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # all-inorganic PK
#                                             "solutes": 8, "spinsteps": 2, "antisolvent": True}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # PEAI Treatment
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PCBM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PEIE
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "ALD"},  # SnOx
#     {"process": "Sputtering"},  # SnOx
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # SAM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # all-inorganic PK
#                                             "solutes": 4, "spinsteps": 2, "antisolvent": True}},
#     {"process": "Spin Coating", "config": {"solvents": 1,  # treatment
#                                            "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},  # C60
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PEIE
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "ALD"},  # SnOx
#     {"process": "Sputtering"},  # ITO
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # pedot:pss
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 2, # narrow PK
#                                             "solutes": 8, "spinsteps": 2, "antisolvent": True}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # Treatment
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},  # C60
#     {"process": "ALD"},  # SnOx
#     {"process": "Evaporation"},  # Cu
# ]

# Process for Daniel Spinbot
# process_sequence = [
#    {"process": "Experiment Info"},
#    {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
#    {"process": "Spin Coating", "config":  {"solvents": 1,
#                                            "solutes": 1, "spinsteps": 1, "antisolvent": False}},  # SAM
#    {"process": "Spin Coating", "config":  {"solvents": 2,
#                                            "solutes": 5, "spinsteps": 2, "antisolvent": True}},  # PSK
#    {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 2,
#                                            "spinsteps": 1, "antisolvent": False}},  # Passivation Sol
#    {"process": "Evaporation"},  # Passivation Evap
#    {"process": "Evaporation"},  # C60
#    {"process": "Evaporation"},  # BCP
#    {"process": "ALD"},  # SnO2
#    {"process": "Evaporation"}  # Ag
# ]


# Process for Spinbot gasquenched
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
#     {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps": 1}},  # SAM
#     {"process": "Spin Coating", "config":  {"solvents": 2, "solutes": 5, "spinsteps": 2, "gasquenching": True}},  # PSK
#     {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 2, "spinsteps": 1}},  # Passivation Sol
#     {"process": "Evaporation"},  # Passivation Evap
#     {"process": "Evaporation"},  # C60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"}   # Ag
# ]

# process_sequence = [
#     # Philippe process
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}}, #FTO
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # NiOx
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # SAM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 2,  # Perovkiste
#                                             "solutes": 4, "spinsteps": 2, "antisolvent": True}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # PCBM
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Spin Coating", "config":  {"solvents": 1,  # BCP
#                                             "solutes": 1, "spinsteps": 1, "antisolvent": False}},
#     {"process": "Evaporation"},
# ]

# Process for Hybrid
# Process_sequence = [
#   {"process": "Experiment Info"},
#   {"process": "Cleaning O2-Plasma", "config": {"solvents": 2}},
#   {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "antisolvent": False}},   #SAM
#   {"process": "Seq-Evaportation", "config":  {"materials": 2} },                                                 #PSK inorganic
#   {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 3, "spinsteps":1 , "antisolvent": False}},   #PSK organic
#   {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 2, "spinsteps":1 , "antisolvent": False}},   #Passivation Sol
#   {"process": "Evaporation"},    #Passivation Evap
#   {"process": "Evaporation"},    #C60
#   {"process": "Evaporation"},    #BCP
#   {"process": "ALD"},            #SnO2
#   {"process": "Evaporation"}     #Ag
# ]


# Process for SOP
# process_sequence = [
#    {"process": "Experiment Info"},
#    {"process": "Cleaning O2-Plasma", "config": {"solvents": 3}},
#    {"process": "Spin Coating", "config":  {"solvents": 2, "solutes": 1, "spinsteps":1 , "antisolvent": False}}, #NiO
#    {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "antisolvent": False}}, #SAM
#    {"process": "Spin Coating", "config":  {"solvents": 2, "solutes": 6, "spinsteps":2 , "antisolvent": True}}, #PSK
#    {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "antisolvent": False}}, #PEAI
#    {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "antisolvent": False}}, #PCBM
#    {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "antisolvent": False}}, #BCP
#    {"process": "Evaporation"} #Ag
# ]


# Test Process
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1}},   #SAM
#     {"process": "Spin Coating", "config":  {"solvents": 2, "solutes": 5, "spinsteps":2 , "antisolvent": True}},    #PSK
#     {"process": "Spin Coating", "config":  {"solvents": 1, "solutes": 1, "spinsteps":1 , "gasquenching": True}},   #Passivation Sol
# ]

# All inclusive test file. Sublimation, coevap and Annealing class are not added at the moment
process_sequence = [
    {"process": "Experiment Info"},
    {'process': 'Laser Scribing'},
    {'process': 'Cleaning O2-Plasma', 'config': {'solvents': 2}},
    {'process': 'Cleaning UV-Ozone'},
    {'process': 'Dip Coating'},
    {'process': 'Spin Coating', 'config': {
        'solvents': 2, 'solutes': 2, 'spinsteps': 2, 'antisolvent': True }},
    {'process': 'Spin Coating', 'config': {
        'solvents': 1, 'solutes': 1, 'spinsteps':1, 'vacuumquenching': True }},
    {'process': 'Spin Coating', 'config': {
        'solvents': 1, 'solutes': 1, 'spinsteps':1, 'gasquenching': True }},
    {'process': 'Slot Die Coating'},    
    {'process': 'Inkjet Printing', 'config' : {'annealing': True, 'gavd': True}},
    {'process': 'Evaporation', 'config': {'carbon_paste': True}},
    {'process': 'Sputtering'},
    {'process': 'ALD'},
    {'process': 'Generic Process'},
]

# Aleja's process
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 4}},
#     {
#         "process": "Spin Coating",
#         "config": {
#             "solvents": 1,  # NiOx
#             "solutes": 1,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Slot Die Coating",
#         "config": {
#             "solvents": 1,  # NiOx
#             "solutes": 1,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Slot Die Coating",
#         "config": {
#             "solvents": 1,  # Alumina
#             "solutes": 1,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Spin Coating",
#         "config": {
#             "solvents": 1,  # SAM
#             "solutes": 1,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Slot Die Coating",
#         "config": {
#             "solvents": 1,  # SAM
#             "solutes": 1,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Slot Die Coating",
#         "config": {
#             "solvents": 4,  # Perovskite
#             "solutes": 4,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {"process": "Evaporation"},  # C60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"},  # Metal contact
# ]

# wide bandgap slot die tandem Yiran 2025-05-19
# Process sequence for 2025-05-19 multi-layer stack
process_sequence = [
    {"process": "Experiment Info"},
    {"process": "Cleaning UV-Ozone", "config": {"solvents": 2}},
    {
        "process": "Spin Coating",
        "config": {
            "solvents": 2,  # NiOx
            "solutes": 2,
            "spinsteps": 2,
            "antisolvent": False
        }
    },
    {
        "process": "Spin Coating",
        "config": {
            "solvents": 2,  # SAM
            "solutes": 2,
            "spinsteps": 2,
            "antisolvent": False
        }
    },
    {
        "process": "Slot Die Coating",
        "config": {
            "solvents": 3,  # Perovskite
            "solutes": 8,
        }
    },
    {"process": "Evaporation"},  # LiF
    {
        "process": "Spin Coating",
        "config": {
            "solvents": 2,  # Passivation
            "solutes": 2,
            "spinsteps": 2,
            "antisolvent": False
        }
    },
    {"process": "Evaporation"},  # C60
    {"process": "ALD"},          # SnO2
    {"process": "Sputtering"},   # IZO
    {"process": "Evaporation"}   # Silver
]

# wide bandgap slot die single juction Yiran 2025-05-19
# process_sequence = [
#     {"process": "Experiment Info"},
#     {"process": "Cleaning UV-Ozone", "config": {"solvents": 2}},
#     {
#         "process": "Spin Coating",
#         "config": {
#             "solvents": 2,  # NiOx
#             "solutes": 2,
#             "spinsteps": 1,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Spin Coating",
#         "config": {
#             "solvents": 2,  # SAM
#             "solutes": 2,
#             "spinsteps": 2,
#             "antisolvent": False
#         }
#     },
#     {
#         "process": "Slot Die Coating",
#         "config": {
#             "solvents": 3,  # Perovskite
#             "solutes": 8,
#         }
#     },
#     {
#         "process": "Spin Coating",
#         "config": {
#             "solvents": 2,  # Passivation
#             "solutes": 2,
#             "spinsteps": 2,
#             "antisolvent": False
#         }
#     },
#     {"process": "Evaporation"},  # LiF
#     {"process": "Evaporation"},  # C60
#     {"process": "Evaporation"},  # BCP
#     {"process": "Evaporation"}   # Silver
# ]

# Ink recycling process
process_sequence = [
    {"process": "Experiment Info"},
    {"process": "Ink Recycling", "config": {
        "solvents": 2,
        "solutes": 1,
        "precursors": 2
    }}
]
builder = ExperimentExcelBuilder(process_sequence, is_testing=True)
builder.build_excel()
builder.save()
