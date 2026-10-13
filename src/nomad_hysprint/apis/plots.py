"""Plotly figures: 2x2 boxplots and JV curves."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import DIRECTION_COLORS, DIRECTION_DASH, JV_PALETTE

METRICS = [
    ('Voc(V)', 'V<sub>oc</sub> (V)'),
    ('Jsc(mA/cm2)', 'J<sub>sc</sub> (mA/cm<sup>2</sup>)'),
    ('FF(%)', 'FF (%)'),
    ('PCE(%)', 'PCE (%)'),
]


def _ordered_conditions(df, condition_order=None):
    if condition_order is None:
        # Natural sort: try numeric extraction first, fall back to string sort
        conds = sorted(df['condition'].dropna().unique().tolist())
        return conds
    seen = set()
    out = []
    for c in condition_order:
        if c in df['condition'].values and c not in seen:
            out.append(c)
            seen.add(c)
    # Append any remaining conditions not in the order list
    for c in sorted(df['condition'].dropna().unique()):
        if c not in seen:
            out.append(c)
    return out


def make_boxplots(df, condition_order=None):
    """2x2 grid: Voc, Jsc, FF, PCE, boxplot per condition split by direction."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text='No data', x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False, font=dict(size=18)
        )
        return fig

    conditions = _ordered_conditions(df, condition_order)
    df = df[df['direction'].isin(['Reverse', 'Forward'])].copy()

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[label for _, label in METRICS],
        horizontal_spacing=0.10,
        vertical_spacing=0.18,
    )

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    legend_seen = set()

    for (col_name, _label), (r, c) in zip(METRICS, positions):
        for direction in ['Reverse', 'Forward']:
            sub = df[df['direction'] == direction]
            show_in_legend = direction not in legend_seen
            legend_seen.add(direction)
            fig.add_trace(
                go.Box(
                    x=sub['condition'],
                    y=sub[col_name],
                    name=direction,
                    legendgroup=direction,
                    showlegend=show_in_legend,
                    marker_color=DIRECTION_COLORS[direction],
                    boxpoints='all',
                    pointpos=0,
                    jitter=0.4,
                    marker=dict(size=3, opacity=0.5, color='black'),
                    line=dict(width=1),
                ),
                row=r,
                col=c,
            )
        fig.update_yaxes(title_text=_label, row=r, col=c)
        fig.update_xaxes(categoryorder='array', categoryarray=conditions, tickangle=-15, row=r, col=c)

    fig.update_layout(
        boxmode='group',
        height=720,
        legend=dict(orientation='h', yanchor='bottom', y=1.06, xanchor='center', x=0.5, title=None),
        margin=dict(l=60, r=20, t=70, b=60),
    )
    return fig


def make_jv_curves(df, condition_order=None):
    """For each condition, pick the device closest to the condition's median PCE
    and plot both directions (Reverse solid, Forward dotted)."""
    fig = go.Figure()
    if df.empty:
        fig.add_annotation(
            text='No data', x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False, font=dict(size=18)
        )
        return fig

    conditions = _ordered_conditions(df, condition_order)
    legend_dir_seen = set()

    for i, cond in enumerate(conditions):
        group = df[df['condition'] == cond].dropna(subset=['PCE(%)'])
        if group.empty:
            continue
        color = JV_PALETTE[i % len(JV_PALETTE)]

        median_pce = group['PCE(%)'].median()
        idx = (group['PCE(%)'] - median_pce).abs().idxmin()
        lab_id = group.loc[idx, 'lab_id']
        cell = group.loc[idx, 'cell']

        device = group[(group['lab_id'] == lab_id) & (group['cell'] == cell)]
        for direction, g2 in device.groupby('direction'):
            row = g2.iloc[0]
            V = np.asarray(row['Voltage(V)'])
            J = np.asarray(row['Current(mA/cm2)'])
            if V.size == 0:
                continue
            fig.add_trace(
                go.Scatter(
                    x=V,
                    y=J,
                    mode='lines',
                    name=f'{cond} | {direction}',
                    line=dict(color=color, dash=DIRECTION_DASH.get(direction, 'solid'), width=2),
                    hovertemplate=(
                        f'<b>{cond}</b><br>{direction}<br>'
                        'V = %{x:.3f} V<br>J = %{y:.2f} mA/cm²<extra></extra>'
                    ),
                )
            )
            legend_dir_seen.add(direction)

    fig.add_hline(y=0, line=dict(color='grey', width=0.5))
    fig.add_vline(x=0, line=dict(color='grey', width=0.5))
    fig.update_layout(
        xaxis_title='Voltage (V)',
        yaxis_title='Current density (mA/cm<sup>2</sup>)',
        height=600,
        legend=dict(title='Condition | Direction'),
        margin=dict(l=60, r=20, t=40, b=60),
    )
    return fig
