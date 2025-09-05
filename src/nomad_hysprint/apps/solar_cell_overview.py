from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Dashboard,
    Filters,
    Layout,
    Pagination,
    SearchQuantities,
    WidgetHistogram,
    WidgetPeriodicTable,
    WidgetScatterPlot,
    WidgetTerms,
)

schema = 'nomad_hysprint.schema_packages.hysprint_package.HySprint_Sample'

solar_cell_overview = App(
    label='Solar Cell Overview',
    path='solar-cells-overview',
    category='Solar cells',
    description='Search general solar cells',
    readme="""This page allows you to search ** solar cell data **
      within NOMAD. The filter menu on the left and the shown
      default columns are specifically designed for solar cell
      exploration. The dashboard directly shows useful
      interactive statistics about the data.""",
    search_quantities=SearchQuantities(include=[f'*#{schema}']),
    filters=Filters(
        include=[
            f'*#{schema}',
        ]
    ),
    filters_locked={'section_defs.definition_qualified_name': schema},
    pagination=Pagination(order_by='results.properties.optoelectronic.solar_cell.efficiency'),
    columns=[
        Column(quantity='authors', selected=True),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.absorber',
            selected=True,
            label='Absorber',
        ),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.efficiency',
            selected=True,
            format={'decimals': 2, 'mode': 'standard'},
            label='Efficiency (%)',
        ),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.open_circuit_voltage',
            selected=True,
            format={'decimals': 3, 'mode': 'standard'},
            unit='V',
        ),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.short_circuit_current_density',
            selected=True,
            format={'decimals': 3, 'mode': 'standard'},
            unit='A/m**2',
        ),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.fill_factor',
            selected=True,
            format={'decimals': 3, 'mode': 'standard'},
        ),
        Column(quantity='results.material.chemical_formula_hill', label='Formula'),
        Column(quantity='results.material.structural_type'),
        Column(
            quantity='results.properties.optoelectronic.solar_cell.illumination_intensity',
            format={'decimals': 3, 'mode': 'standard'},
            label='Illum. intensity',
            unit='W/m**2',
        ),
        Column(quantity='results.eln.lab_ids', selected=True),
        Column(quantity='results.eln.tags'),
        Column(quantity='entry_name', label='Name'),
        Column(quantity='entry_type'),
        Column(quantity='mainfile'),
        Column(quantity='upload_create_time', label='Upload time'),
        Column(quantity='comment'),
        Column(quantity='datasets'),
        Column(quantity='published', label='Access'),
    ],
    filter_menus={
        'options': {
            'material': {'label': 'Materials'},
            'elements': {'label': 'Elements / Formula', 'level': 1, 'size': 'xl'},
            'electronic': {'label': 'Electronic Properties'},
            'solarcell': {'label': 'Solar Cell Properties'},
            'eln': {'label': 'Electronic Lab Notebook'},
            'custom_quantities': {'label': 'User Defined Quantities', 'size': 'l'},
            'author': {'label': 'Author / Origin / Dataset', 'size': 'm'},
            'metadata': {'label': 'Visibility / IDs / Schema'},
        }
    },
    dashboard=Dashboard(
        widgets=[
            WidgetPeriodicTable(
                scale='linear',
                search_quantity='results.material.elements',
                layout={
                    'lg': Layout(h=8, minH=4, minW=10, w=10, x=0, y=0),
                    'md': Layout(h=8, minH=4, minW=10, w=10, x=0, y=0),
                    'sm': Layout(h=8, minH=4, minW=10, w=10, x=0, y=0),
                    'xl': Layout(h=8, minH=4, minW=10, w=10, x=0, y=0),
                    'xxl': Layout(h=8, minH=4, minW=10, w=10, x=0, y=0),
                },
            ),
            WidgetScatterPlot(
                title='Open Circut Voltage vs. Efficency',
                layout={
                    'lg': Layout(h=8, minH=8, minW=10, w=10, x=0, y=8),
                    'md': Layout(h=8, minH=8, minW=10, w=10, x=0, y=8),
                    'sm': Layout(h=8, minH=8, minW=10, w=10, x=0, y=8),
                    'xl': Layout(h=8, minH=8, minW=10, w=10, x=10, y=0),
                    'xxl': Layout(h=8, minH=8, minW=10, w=10, x=10, y=0),
                },
                x=Axis(
                    search_quantity='results.properties.optoelectronic.solar_cell.open_circuit_voltage',  # noqa: E501
                ),
                y=Axis(
                    search_quantity='results.properties.optoelectronic.solar_cell.efficiency',  # noqa: E501
                    title='Efficiency (%)',
                ),
                markers={
                    'color': {
                        'quantity': 'results.properties.optoelectronic.solar_cell.short_circuit_current_density',  # noqa: E501
                        'unit': 'mA/cm^2',
                    }
                },  # noqa: E501
                size=1000,
                autorange=True,
            ),
            WidgetScatterPlot(
                title='PCE Timeline',
                autorange=True,
                x=Axis(
                    search_quantity='entry_create_time',
                    title='Datetime',
                    scale='linear',
                ),
                y=Axis(
                    search_quantity='results.properties.optoelectronic.solar_cell.efficiency',
                    scale='linear',
                ),
                size=1000,  # maximum number of entries loaded
                layout={
                    'lg': Layout(h=8, minH=8, minW=10, w=10, x=0, y=16),
                    'md': Layout(h=8, minH=8, minW=10, w=10, x=0, y=16),
                    'sm': Layout(h=8, minH=8, minW=10, w=10, x=0, y=16),
                    'xl': Layout(h=8, minH=8, minW=10, w=10, x=20, y=0),
                    'xxl': Layout(h=8, minH=8, minW=10, w=10, x=20, y=0),
                },
            ),
            WidgetTerms(
                title='Device Stack',
                layout={
                    'lg': Layout(h=6, minH=3, minW=3, w=6, x=0, y=24),
                    'md': Layout(h=6, minH=3, minW=3, w=6, x=0, y=24),
                    'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=24),
                    'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=8),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=8),
                },
                search_quantity='results.properties.optoelectronic.solar_cell.device_stack',
                scale='linear',
                showinput=True,
            ),
            WidgetHistogram(
                title='Illumination Intensity',
                layout={
                    'lg': Layout(h=4, minH=3, minW=3, w=6, x=6, y=36),
                    'md': Layout(h=3, minH=3, minW=3, w=6, x=6, y=36),
                    'sm': Layout(h=3, minH=3, minW=3, w=6, x=6, y=36),
                    'xl': Layout(h=3, minH=3, minW=3, w=6, x=6, y=14),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=6, y=14),
                },
                x=Axis(search_quantity='results.properties.optoelectronic.solar_cell.illumination_intensity'),
                scale='1/4',
                showinput=True,
                nbins=30,
            ),
            WidgetHistogram(
                title='Bandgap',
                layout={
                    'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=36),
                    'md': Layout(h=3, minH=3, minW=3, w=6, x=0, y=36),
                    'sm': Layout(h=3, minH=3, minW=3, w=6, x=0, y=36),
                    'xl': Layout(h=3, minH=3, minW=3, w=6, x=0, y=14),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=14),
                },
                x=Axis(
                    search_quantity='results.properties.electronic.band_structure_electronic.band_gap.value',
                    unit='eV',
                ),
                scale='1/4',
                showinput=False,
                nbins=30,
            ),
            WidgetTerms(
                title='Absorber Fabrication',
                layout={
                    'lg': Layout(h=6, minH=3, minW=3, w=6, x=6, y=24),
                    'md': Layout(h=6, minH=3, minW=3, w=6, x=6, y=24),
                    'sm': Layout(h=6, minH=3, minW=3, w=6, x=6, y=24),
                    'xl': Layout(h=6, minH=3, minW=3, w=6, x=6, y=8),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=6, y=8),
                },
                search_quantity='results.properties.optoelectronic.solar_cell.absorber_fabrication',
                scale='linear',
                showinput=True,
            ),
            WidgetTerms(
                title='Absorber Layer',
                layout={
                    'lg': Layout(h=6, minH=3, minW=3, w=6, x=12, y=24),
                    'md': Layout(h=6, minH=3, minW=3, w=6, x=12, y=24),
                    'sm': Layout(h=6, minH=3, minW=3, w=6, x=12, y=24),
                    'xl': Layout(h=6, minH=3, minW=3, w=6, x=12, y=8),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=12, y=8),
                },
                search_quantity='results.properties.optoelectronic.solar_cell.absorber',
                scale='linear',
                showinput=True,
            ),
            WidgetTerms(
                title='Electron Transport Layer',
                layout={
                    'lg': Layout(h=6, minH=3, minW=3, w=6, x=0, y=30),
                    'md': Layout(h=6, minH=3, minW=3, w=6, x=0, y=30),
                    'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=30),
                    'xl': Layout(h=6, minH=3, minW=3, w=6, x=12, y=8),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=12, y=8),
                },
                search_quantity='results.properties.optoelectronic.solar_cell.electron_transport_layer',
                scale='linear',
                showinput=True,
            ),
            WidgetTerms(
                title='Hole Transport Layer',
                layout={
                    'lg': Layout(h=6, minH=3, minW=3, w=6, x=6, y=30),
                    'md': Layout(h=6, minH=3, minW=3, w=6, x=6, y=30),
                    'sm': Layout(h=6, minH=3, minW=3, w=6, x=6, y=30),
                    'xl': Layout(h=6, minH=3, minW=3, w=6, x=18, y=8),
                    'xxl': Layout(h=6, minH=3, minW=3, w=6, x=18, y=8),
                },
                search_quantity='results.properties.optoelectronic.solar_cell.hole_transport_layer',
                scale='linear',
                showinput=True,
            ),
        ]
    ),
)
