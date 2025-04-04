#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import numpy as np
from baseclasses import (
    BaseProcess,
)
from baseclasses.helper.add_solar_cell import add_solar_cell
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.basesections import CompositeSystem
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.datamodel.results import Material
from nomad.metainfo import MEnum, Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage()

# %%####################################### SOL-AI


class SOLAI_PLImage(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)
    data_type = Quantity(type=MEnum('Relative', 'Absolute'))

    pl_image = Quantity(
        type=ArchiveSection,
    )

    pl_image_data = Quantity(type=np.dtype(np.float64), shape=['*', '*'])


class SOLAI_JVMeasurement(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)
    scan_type = Quantity(
        type=MEnum(
            'Forward Light',
            'Reverse Light',
            'Forward Dark',
            'Reverse Dark',
            'Simulated',
        )
    )

    jv_measurement = Quantity(
        type=ArchiveSection,
    )
    current_density = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00000064',
            'https://purl.archive.org/tfsco/TFSCO_00005061',
        ],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA/cm^2',
        description='Current density array of the *JV* curve.',
    )

    voltage = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001464',
            'https://purl.archive.org/tfsco/TFSCO_00005005',
        ],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='V',
        description='Voltage array of the of the *JV* curve.',
    )


class SOLAI_UVVISMeasurement(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)
    # scan_type = Quantity(
    #     type=MEnum('Forward Light', 'Reverse Light', 'Forward Dark', 'Reverse Dark')
    # )

    uvvis_measurement = Quantity(
        type=ArchiveSection,
    )
    intensity = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001128'],
        type=np.dtype(np.float64),
        shape=['*'],
    )

    wavelength = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001242',
            'https://purl.archive.org/tfsco/TFSCO_00002040',
        ],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='nm',
        a_plot=[
            {
                'x': 'wavelength',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )


class SOLAI_EQEMeasurement(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    eqe_measurement = Quantity(
        type=ArchiveSection,
    )
    intensity = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001128'],
        type=np.dtype(np.float64),
        shape=['*'],
    )

    wavelength = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001242',
            'https://purl.archive.org/tfsco/TFSCO_00002040',
        ],
        type=np.dtype(np.float64),
        shape=['*'],
        unit='nm',
        a_plot=[
            {
                'x': 'wavelength',
                'y': 'intensity',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
                'config': {'editable': True, 'scrollZoom': True},
            }
        ],
    )


class SOLAI_SimulationInput(ArchiveSection):
    variation_name = Quantity(
        type=str,
        description="""
        The name or identifier of a paramter which is varied over a simulation
        """,
    )

    variation_value_number = Quantity(
        type=float,
        description="""
        The numerical value of a continous parameter which is varied over a simulation
        """,
    )

    variation_value_unit = Quantity(
        type=str,
        description="""
        The unit of a continous parameter which is varied over a simulation
        """,
    )

    variation_value_string = Quantity(
        type=str,
        description="""
        The string value of a categorical paramter which is varied over a simulation
        """,
    )


def cell_params(voltage, current_density):
    """
    Calculates basic solar cell parametes form a current density (mA/cm**2)
    voltage (V) curve.

    Returns:
        Voc (V) open circuit voltage
        Jsc (mA/cm**2) short circuit current density
        FF fill factor in absolute values (0-1)
        efficiency power conversion efficiency in percentage (0-100)
    """
    from scipy import interpolate

    j_v_interpolated = interpolate.interp1d(current_density, voltage, fill_value='extrapolate')
    Voc = j_v_interpolated(0).item()
    v_j_interpolated = interpolate.interp1d(voltage, current_density, fill_value='extrapolate')
    Isc = v_j_interpolated(0).item()
    if Isc >= 0:
        idx = np.argmax(voltage * current_density)
    else:
        idx = np.argmin(voltage * current_density)
    Vmp = voltage[idx]
    Imp = current_density[idx]
    Isc = abs(Isc)
    FF = abs(Vmp.magnitude * Imp.magnitude / (Voc * Isc))
    efficiency = Voc * FF * Isc
    return Voc, Isc, FF, efficiency


class SOLAI_SolarCell(CompositeSystem, PlotSection, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['results', 'elemental_composition', 'components'],
        ),
    )

    simulated = Quantity(type=bool)

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity', props=dict(height=200)),
    )

    synthesis_processes = Quantity(type=BaseProcess, shape=['*'])

    substrate_reference = Quantity(type=CompositeSystem)

    pl_images = SubSection(section_def=SOLAI_PLImage, repeats=True)
    jv_measurements = SubSection(section_def=SOLAI_JVMeasurement, repeats=True)
    jv_measurements_dark = SubSection(section_def=SOLAI_JVMeasurement, repeats=True)
    uvvis_measurements = SubSection(section_def=SOLAI_UVVISMeasurement, repeats=True)
    eqe_measurements = SubSection(section_def=SOLAI_EQEMeasurement, repeats=True)
    simulation_inputs = SubSection(section_def=SOLAI_SimulationInput, repeats=True)

    def set_solar_cell_params(self, archive, voc, jsc, ff, eff, intensity):
        solar_cell = archive.results.properties.optoelectronic.solar_cell
        solar_cell.open_circuit_voltage = voc
        solar_cell.short_circuit_current_density = jsc
        solar_cell.fill_factor = ff
        solar_cell.efficiency = eff
        solar_cell.illumination_intensity = intensity

    def get_solar_cell_params_1(self, archive):
        # export to results section
        max_idx = -1
        eff = -1
        for i, curve in enumerate(self.jv_measurements):
            if curve.jv_measurement.efficiency and curve.jv_measurement.efficiency > eff:
                eff = curve.jv_measurement.efficiency
                max_idx = i
        if max_idx >= 0:
            self.set_solar_cell_params(
                archive,
                self.jv_measurements[max_idx].jv_measurement.open_circuit_voltage,
                self.jv_measurements[max_idx].jv_measurement.short_circuit_current_density,
                self.jv_measurements[max_idx].jv_measurement.fill_factor,
                self.jv_measurements[max_idx].jv_measurement.efficiency,
                self.jv_measurements[max_idx].jv_measurement.light_intensity,
            )

    def get_solar_cell_params_2(self, archive):
        # export to results section
        max_idx = -1
        eff = -1
        for i, curve in enumerate(self.jv_measurements):
            if (
                curve.jv_measurement.efficiency_in_percent
                and curve.jv_measurement.efficiency_in_percent > eff
            ):
                eff = curve.jv_measurement.efficiency_in_percent
                max_idx = i
        if max_idx >= 0:
            self.set_solar_cell_params(
                archive,
                self.jv_measurements[max_idx].jv_measurement.open_circuit_voltage,
                self.jv_measurements[max_idx].jv_measurement.short_circuit_current_density,
                self.jv_measurements[max_idx].jv_measurement.fill_factor_in_percent / 100,
                self.jv_measurements[max_idx].jv_measurement.efficiency_in_percent,
                self.jv_measurements[max_idx].jv_measurement.light_intensity,
            )

    def get_solar_cell_params_3(self, archive):
        # export to results section
        max_idx = -1
        eff = -1
        params = []
        for i, curve in enumerate(self.jv_measurements):
            params.append(cell_params(curve.voltage, curve.current_density))
            if params[i][3] > eff:
                eff = params[i][3]
                max_idx = i
        if max_idx >= 0:
            self.set_solar_cell_params(
                archive,
                params[max_idx][0],
                params[max_idx][1],
                params[max_idx][2],
                params[max_idx][3],
                None,
            )

    def normalize(self, archive, logger):  # noqa: PLR0912
        super(CompositeSystem, self).normalize(archive, logger)
        import pandas as pd
        import plotly.graph_objects as go

        result_figures = []
        # overview
        overview = pd.DataFrame(columns=['Synthesis', 'JV', 'JV Dark', 'PLI', 'UVvis', 'EQE'])
        overview.loc[len(overview)] = [
            f'{len(self.synthesis_processes) if self.synthesis_processes else 0} Synthesis Processes',  # noqa E501
            f'{len(self.jv_measurements) if self.jv_measurements else 0} JV curves',
            f'{len(self.jv_measurements_dark) if self.jv_measurements_dark else 0} JV curves dark',  # noqa E501
            f'{len(self.pl_images) if self.pl_images else 0} PL Images',
            f'{len(self.uvvis_measurements) if self.uvvis_measurements else 0} UVvis curves',  # noqa E501
            f'{len(self.eqe_measurements) if self.eqe_measurements else 0} EQE curves',  # noqa E501
        ]

        fig_overview = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(overview.columns),
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left',
                    ),
                    cells=dict(
                        values=[overview[c] for c in overview.columns],  # 2nd column
                        line_color='darkslategray',
                        # fill_color='lightcyan',
                        align='left',
                    ),
                )
            ]
        )
        fig_overview.update_layout(height=180)
        result_figures.append(PlotlyFigure(label='Modalities', index=1, figure=fig_overview.to_plotly_json()))
        # plots
        if self.pl_images:
            from plotly.subplots import make_subplots

            number_of_images = len(self.pl_images)
            fig = make_subplots(
                int(np.ceil(number_of_images / 2)),
                2,
                subplot_titles=[p.name for p in self.pl_images],
            )

            for i in range(int(np.ceil(number_of_images / 2))):
                for j in range(2):
                    if 2 * i + j >= number_of_images:
                        continue
                    fig.add_trace(
                        go.Heatmap(z=self.pl_images[i].pl_image_data, colorscale='gray'),
                        i + 1,
                        j + 1,
                    )
            fig.update_layout(height=250 * number_of_images)

            result_figures.append(PlotlyFigure(label='PL Image', index=1, figure=fig.to_plotly_json()))

        if self.jv_measurements:
            import pandas as pd

            # Light JV curves
            fig2 = go.Figure()
            traces = []
            for curve in self.jv_measurements:
                show = True
                traces.append(
                    go.Scatter(
                        x=curve.voltage.to('V'),
                        y=curve.current_density.to('mA/cm**2'),
                        name=curve.scan_type,
                        visible=show,
                    )
                )
            fig2.add_traces(traces)
            layout_settings = {
                'title': 'Light JV-Curves',
                'xaxis': {'title': 'Voltage (V)', 'gridcolor': 'lightgrey'},
                'yaxis': {
                    'title': 'Current Density (mA/cm²)',
                    'showgrid': True,
                    'gridcolor': 'lightgrey',
                },
                'showlegend': True,
                'legend': {'x': 0.02, 'y': 0.98},
                'plot_bgcolor': 'white',
            }
            fig2.update_layout(layout_settings)
            result_figures.append(
                PlotlyFigure(
                    label='Light JV Curves',
                    index=2,
                    open=True,
                    figure=fig2.to_plotly_json(),
                )
            )

        if self.uvvis_measurements:
            import pandas as pd

            # Light JV curves
            fig2 = go.Figure()
            traces = []
            for curve in self.uvvis_measurements:
                show = True
                traces.append(
                    go.Scatter(
                        x=curve.wavelength.to('nm'),
                        y=curve.intensity,
                        name=curve.name,
                        visible=show,
                    )
                )
            fig2.add_traces(traces)
            layout_settings = {
                'title': 'UVVis Curves',
                'xaxis': {'title': 'Wavelength (nm)', 'gridcolor': 'lightgrey'},
                'yaxis': {
                    'title': 'Intensity',
                    'showgrid': True,
                    'gridcolor': 'lightgrey',
                },
                'showlegend': True,
                'legend': {'x': 0.02, 'y': 0.98},
                'plot_bgcolor': 'white',
            }
            fig2.update_layout(layout_settings)
            result_figures.append(
                PlotlyFigure(
                    label='UVVis Curves',
                    index=2,
                    open=True,
                    figure=fig2.to_plotly_json(),
                )
            )

        if self.eqe_measurements:
            import pandas as pd

            # Light JV curves
            fig2 = go.Figure()
            traces = []
            for curve in self.eqe_measurements:
                show = True
                traces.append(
                    go.Scatter(
                        x=curve.wavelength.to('nm'),
                        y=curve.intensity,
                        name=curve.name,
                        visible=show,
                    )
                )
            fig2.add_traces(traces)
            layout_settings = {
                'title': 'EQE Curves',
                'xaxis': {'title': 'Wavelength (nm)', 'gridcolor': 'lightgrey'},
                'yaxis': {
                    'title': 'Intensity',
                    'showgrid': True,
                    'gridcolor': 'lightgrey',
                },
                'showlegend': True,
                'legend': {'x': 0.02, 'y': 0.98},
                'plot_bgcolor': 'white',
            }
            fig2.update_layout(layout_settings)
            result_figures.append(
                PlotlyFigure(
                    label='EQE Curves',
                    index=2,
                    open=True,
                    figure=fig2.to_plotly_json(),
                )
            )

        self.figures = result_figures
        add_solar_cell(archive)
        if self.jv_measurements:
            try:
                self.get_solar_cell_params_1(archive)
            except Exception:
                try:
                    self.get_solar_cell_params_2(archive)
                except Exception:
                    self.get_solar_cell_params_3(archive)

        if self.substrate_reference:
            archive.results.properties.optoelectronic.solar_cell.substrate = []
            archive.results.properties.optoelectronic.solar_cell.device_stack = []
            if getattr(self.substrate_reference, 'substrate', None):
                if self.substrate_reference.substrate.substrate is not None:
                    archive.results.properties.optoelectronic.solar_cell.substrate = [
                        self.substrate_reference.substrate.substrate
                    ]
                    archive.results.properties.optoelectronic.solar_cell.device_stack.append(  # noqa E501
                        self.substrate_reference.substrate.substrate
                    )
                if self.substrate_reference.substrate.conducting_material is not None:
                    archive.results.properties.optoelectronic.solar_cell.substrate.extend(  # noqa E501
                        self.substrate_reference.substrate.conducting_material
                    )
                    archive.results.properties.optoelectronic.solar_cell.device_stack.extend(  # noqa E501
                        self.substrate_reference.substrate.conducting_material
                    )

            if getattr(self.substrate_reference, 'architecture', None):
                archive.results.properties.optoelectronic.solar_cell.device_architecture = (
                    self.substrate_reference.architecture
                )  # noqa E501

            if getattr(self.substrate_reference, 'substrate', None):
                if self.substrate_reference.substrate.pixel_area:
                    archive.results.properties.optoelectronic.solar_cell.device_area = (  # noqa E501
                        self.substrate_reference.substrate.pixel_area
                    )

        if self.synthesis_processes:
            from baseclasses.solar_energy.solarcellsample import (
                addLayerDepositionToStack,
            )

            archive.results.properties.optoelectronic.solar_cell.absorber = []
            archive.results.properties.optoelectronic.solar_cell.absorber_fabrication = []  # noqa E501
            archive.results.properties.optoelectronic.solar_cell.electron_transport_layer = []  # noqa E501
            archive.results.properties.optoelectronic.solar_cell.hole_transport_layer = []  # noqa E501
            archive.results.properties.optoelectronic.solar_cell.back_contact = []  # noqa E501

            if not archive.results.material:
                archive.results.material = Material()
            archive.results.material.elements = []

            if self.jv_measurements:
                archive.results.material.functional_type = [
                    'semiconductor',
                    'solarcell',
                ]

            for process in self.synthesis_processes:
                try:
                    if process.layer:
                        addLayerDepositionToStack(archive, process.m_to_dict())

                    if process.m_parent.results.material and process.m_parent.results.material.elements:
                        archive.results.material.elements.extend(process.m_parent.results.material.elements)
                except Exception:
                    continue


m_package.__init_metainfo__()
