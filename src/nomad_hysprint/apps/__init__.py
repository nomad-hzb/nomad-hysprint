from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Axis,  # added for histogram x-axis
    Column,
    Columns,
    Dashboard,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    Layout,
    Menu,  # for settings menu
    MenuItemHistogram,
    MenuItemTerms,  # use histogram for numeric data
    MenuSizeEnum,  # for menu sizing
    ModeEnum,
    RowActionNorth,
    RowActions,
    RowDetails,
    Rows,
    RowSelection,
    SearchQuantities,
    WidgetScatterPlot,
    WidgetTerms,
)

from nomad_hysprint.apps.solar_cell_overview import solar_cell_overview

solar_cell_overview_entry_point = AppEntryPoint(
    name='SOlarCellOverview',
    description="""
      This app allows you to search **solar cell data** within NOMAD. The filter
      menu on the left and the shown default columns are specifically designed
      for solar cell exploration. The dashboard directly shows useful
      interactive statistics about the data.
    """,
    app=solar_cell_overview,
)


schema_name = 'nomad_hysprint.schema_packages.hysprint_package.HySprint_VoilaNotebook'
hysprint_voila_app = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app=App(
        # Label of the App
        label='Voila',
        # Path used in the URL, must be unique
        path='voila',
        # Used to categorize apps in the explore menu
        category='use cases',
        # Brief description used in the app menu
        description='Find and launch your Voila Tools.',
        # Longer description that can also use markdown
        readme='Find and launch your Voila Tools.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=[
                f'*#{schema_name}',
            ]
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={'section_defs.definition_qualified_name': schema_name},
        filter_menus=FilterMenus(
            options={
                'custom_quantities': FilterMenu(label='Notebooks', size=FilterMenuSizeEnum.L),
                'author': FilterMenu(label='Author', size=FilterMenuSizeEnum.M),
                'metadata': FilterMenu(label='Visibility / IDs'),
            }
        ),
        columns=[
            Column(quantity=f'data.name#{schema_name}', selected=True),
            Column(quantity='entry_type', label='Entry type', align='left', selected=True),
            Column(
                quantity='entry_create_time',
                label='Entry time',
                align='left',
                selected=True,
                format=Format(mode=ModeEnum.DATE),
            ),
            Column(
                quantity='upload_name',
                label='Upload name',
                align='left',
                selected=True,
            ),
            Column(
                quantity='authors',
                label='Authors',
                align='left',
                selected=True,
            ),
            Column(quantity='entry_id'),
            Column(quantity='upload_id'),
            Column(quantity=f'data.notebook_file#{schema_name}'),
        ],
        rows=Rows(
            actions=RowActions(
                options={
                    'launch': RowActionNorth(
                        tool_name='voila',
                        filepath=f'data.notebook_file#{schema_name}',
                    )
                }
            ),
            details=RowDetails(),
            selection=RowSelection(),
        ),
        dashboard=Dashboard(
            widgets=[
                WidgetTerms(
                    title='Voila Notebook Tags',
                    quantity='results.eln.tags',
                    scale='linear',
                    layout={
                        'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=0),
                        'md': Layout(h=5, minH=3, minW=3, w=7, x=0, y=0),
                        'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                    },
                ),
                WidgetTerms(
                    title='Authors',
                    quantity='authors.name',
                    scale='linear',
                    layout={
                        'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=0),
                        'md': Layout(h=5, minH=3, minW=3, w=7, x=0, y=0),
                        'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                    },
                ),
            ]
        ),
    ),
)


schema = 'nomad_hysprint.schema_packages.hysprint_package.HySprint_AbsPLMeasurement'

absolute_pl_app = AppEntryPoint(
    name='Absolute Luminescence',
    description='A search app for absolute photoluminescence experiments.',
    app=App(
        label='Absolute Luminescence',
        path='abs-luminescence',
        category='Measurements',
        breadcrumb='Explore Absolute Luminescence Measurements',
        search_quantities=SearchQuantities(include=[f'*#{schema}']),
        columns=Columns(
            selected=[
                'entry_id',
            ],
            options={
                'entry_id': Column(
                    quantity='entry_id',
                    selected=False,
                ),
                'sample_name': Column(
                    quantity=f'data.samples[0].name#{schema}',  # noqa: E501
                    selected=True,
                    label='Sample Name',
                ),
                'luqy': Column(
                    quantity=f'data.results[0].luminescence_quantum_yield#{schema}',  # noqa: E501
                    selected=True,
                    label='LuQY (%)',
                ),
                'bandgap': Column(
                    quantity=f'data.results[0].bandgap#{schema}',  # noqa: E501
                    selected=True,
                ),
                'quasi_fermi_level_splitting': Column(
                    quantity=f'data.results[0].quasi_fermi_level_splitting#{schema}',  # noqa: E501
                    selected=True,
                    label='QFLS',
                ),
                'derived_jsc': Column(
                    quantity=f'data.results[0].derived_jsc#{schema}',  # noqa: E501
                    selected=True,
                    format={'decimals': 3, 'mode': 'standard'},
                    unit='mA/cm**2',
                    label='Jsc',
                ),
            },
        ),
        menu=Menu(
            items=[
                Menu(
                    title='Measurement Settings',
                    size=MenuSizeEnum.MD,
                    items=[
                        MenuItemHistogram(
                            x={
                                'search_quantity': f'data.settings.laser_intensity_suns#{schema}'  # noqa: E501
                            },  # noqa: E501
                            title='Laser Intensity (suns)',
                            show_input=True,
                            nbins=30,
                        ),
                        MenuItemHistogram(
                            x=Axis(
                                search_quantity=f'data.settings.bias_voltage#{schema}',  # noqa: E501
                            ),
                            title='Bias Voltage',
                            show_input=True,
                            nbins=30,
                        ),
                        MenuItemHistogram(
                            x=Axis(
                                search_quantity=f'data.settings.smu_current_density#{schema}',  # noqa: E501
                                unit='mA/cm**2',
                            ),
                            title='SMU Current Density',
                            show_input=True,
                            nbins=30,
                        ),
                    ],
                ),
                # New Menu for Entry Information (changed from FilterMenu to Menu)
                Menu(
                    title='Author | Sample | Dataset',
                    size='md',
                    items=[
                        MenuItemTerms(search_quantity='authors.name'),
                        MenuItemTerms(
                            search_quantity=f'data.samples.name#{schema}',
                            title='Sample Name',
                        ),
                        MenuItemHistogram(x={'search_quantity': 'upload_create_time'}),
                        MenuItemTerms(search_quantity='datasets.dataset_name'),
                    ],
                ),
                # New Menu for Results Histograms
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results.luminescence_quantum_yield#{schema}',  # noqa: E501
                    ),
                    title='LuQY (%)',
                    show_input=True,
                    nbins=30,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results.bandgap#{schema}',  # noqa: E501
                    ),
                    title='Bandgap',
                    show_input=True,
                    nbins=30,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results.quasi_fermi_level_splitting#{schema}',  # noqa: E501
                    ),
                    title='QFLS',
                    show_input=True,
                    nbins=30,
                ),
                MenuItemHistogram(
                    x=Axis(
                        search_quantity=f'data.results.derived_jsc#{schema}',  # noqa: E501
                        unit='mA/cm**2',
                        format={'decimals': 3, 'mode': 'standard'},
                    ),
                    title='Jsc',
                    show_input=True,
                    nbins=30,
                ),
            ],
        ),
        dashboard=Dashboard(
            widgets=[
                WidgetScatterPlot(
                    title='Bandgap vs. LuQY',
                    autorange=True,
                    layout={
                        'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=0),
                        'md': Layout(h=5, minH=3, minW=3, w=7, x=0, y=0),
                        'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                    },
                    x=Axis(
                        search_quantity=f'data.results[0].bandgap#{schema}',  # noqa: E501
                    ),
                    y=Axis(
                        search_quantity=f'data.results[0].luminescence_quantum_yield#{schema}',  # noqa: E501
                        title='LuQY (%)',
                    ),
                    color=f'data.results[0].quasi_fermi_level_splitting#{schema}',  # noqa: E501
                    size=1000,
                ),
            ]
        ),
        filters_locked={
            'results.eln.sections': [
                'HySprint_AbsPLMeasurement',
            ]
        },
    ),
)
