"""Standalone Panel app: NOMAD JV viewer.

Run with:
    NOMAD_CLIENT_ACCESS_TOKEN=... panel serve app.py --show
"""

import pandas as pd
import panel as pn

from .config import DEFAULT_PCE_MIN

# from api_calls import get_batch_ids
from .data import filter_batch_list

pn.extension('plotly', sizing_mode='stretch_width')


def get_batch_ids(user_id, batch_type='HySprint_Batch'):

    from nomad import files
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    # search for all archives referencing this archive
    query = {'entry_type': batch_type}
    pagination = MetadataPagination()
    pagination.page_size = 10000
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=user_id,
    )
    results = []
    for res in search_result.data:
        # Open Archives
        with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(entry_id=res['entry_id']) as arch:
            entry_id = res['entry_id']
            entry_data = arch[entry_id]['data']
            results.append(entry_data['lab_id'])
    return results


# ---------------------------------------------------------------------------
# Batch selection
# ---------------------------------------------------------------------------


def build_dashboard(user_id):
    all_batches = filter_batch_list(get_batch_ids(user_id))

    batch_selector = pn.widgets.MultiChoice(
        name='Batches',
        options=all_batches,
        value=[],
        placeholder='Search and select one or more batches…',
        height=180,
    )

    pce_min_slider = pn.widgets.FloatSlider(
        name='Minimum PCE (%) for boxplots',
        start=0.0,
        end=30.0,
        step=0.5,
        value=DEFAULT_PCE_MIN,
    )

    load_button = pn.widgets.Button(
        name='Load data',
        button_type='primary',
        icon='download',
        # disabled=not auth.ok,
    )

    status = pn.pane.Markdown('')
    summary = pn.pane.Markdown('')

    # Plot panes (populated on click)
    # box_pane = pn.pane.Plotly(sizing_mode='stretch_width', height=720)
    # jv_pane = pn.pane.Plotly(sizing_mode='stretch_width', height=620)
    # table_pane = pn.widgets.Tabulator(
    #     pd.DataFrame(),
    #     pagination='local',
    #     page_size=20,
    #     sizing_mode='stretch_width',
    #     height=500,
    #     show_index=False,
    # )

    # Held in module state so the PCE slider can re-filter without re-fetching
    _state = {'df_raw': pd.DataFrame()}

    # def _refresh_plots():
    #     df = _state['df_raw']
    #     if df.empty:
    #         box_pane.object = make_boxplots(df)
    #         jv_pane.object = make_jv_curves(df)
    #         table_pane.value = df
    #         return
    #     df_filt = df[df['PCE(%)'].fillna(-1) > pce_min_slider.value]
    #     box_pane.object = make_boxplots(df_filt)
    #     jv_pane.object = make_jv_curves(df_filt)
    #     # Drop the array columns for the table view
    #     display_cols = [c for c in df_filt.columns if c not in ('Voltage(V)', 'Current(mA/cm2)')]
    #     table_pane.value = df_filt[display_cols].reset_index(drop=True)

    # def on_load(event):
    #     if not auth.ok:
    #         return
    #     selected = batch_selector.value
    #     if not selected:
    #         status.object = '⚠️ Select at least one batch.'
    #         return
    #     status.object = f'⏳ Loading {len(selected)} batch(es)…'
    #     load_button.disabled = True
    #     try:
    #         df = load_jv_dataframe(NOMAD_URL, auth.token, list(selected))
    #         _state['df_raw'] = df
    #         if df.empty:
    #             status.object = 'No JV measurements found for the selected batches.'
    #             summary.object = ''
    #         else:
    #             n_samples = df['lab_id'].nunique()
    #             n_curves = len(df)
    #             n_cond = df['condition'].nunique()
    #             status.object = '✅ Loaded.'
    #             summary.object = (
    #                 f'**{n_samples}** samples · **{n_curves}** JV curves · **{n_cond}** conditions'
    #             )
    #         _refresh_plots()
    #     except Exception as e:
    #         status.object = f'❌ Load failed: {e}'
    #     finally:
    #         load_button.disabled = False

    # load_button.on_click(on_load)
    # pce_min_slider.param.watch(lambda *_: _refresh_plots(), "value")

    # ---------------------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------------------

    sidebar = pn.Column(
        '## Controls',
        batch_selector,
        pce_min_slider,
        load_button,
        status,
        summary,
        width=380,
    )

    # tabs = pn.Tabs(
    #    ("Boxplots", box_pane),
    #    ("JV curves", jv_pane),
    #    ("Table", table_pane),
    #    dynamic=True,
    # )

    app = pn.Row(sidebar)  # , tabs)

    template = pn.template.FastListTemplate(
        title='NOMAD JV Viewer',
        main=[app],
        accent_base_color='#1f77b4',
        header_background='#1f77b4',
    )

    return template
