"""Configuration constants for the JV Panel app."""

NOMAD_URL = 'https://nomad-hzb-se.de/nomad-oasis/api/v1'

BATCH_TYPE = 'HySprint_Batch'
JV_TYPE = 'HySprint_JVmeasurement'

# Current density threshold; rows with |J| above this are dropped from JV curves
J_MAX = 28.0

# Default minimum PCE for inclusion in boxplots
DEFAULT_PCE_MIN = 5.0

# Plotly qualitative palette used for JV curves (one color per condition)
JV_PALETTE = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
]

# Colors for the Reverse / Forward hue in boxplots
DIRECTION_COLORS = {'Reverse': '#1f77b4', 'Forward': '#ff7f0e'}

# Linestyles for the JV curve directions
DIRECTION_DASH = {'Reverse': 'solid', 'Forward': 'dot'}
