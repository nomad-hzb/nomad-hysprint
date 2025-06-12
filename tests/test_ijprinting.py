import os

from nomad.client import parse
from nomad.units import ureg

from utils import delete_json


def test_ijprinting(monkeypatch):  # noqa: PLR0915
    file = '20250603_experiment_file.xlsx'
    file_name = os.path.join('tests', 'data', file)
    parse(file_name)[0]

    measurement_archives = []
    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    for m in measurement_archives:
        if 'Inkjet' in str(type(m.data)):
            assert m.data.layer[0].layer_type == 'Absorber'
            assert m.data.layer[0].layer_material_name == 'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3'
            assert m.data.location == 'HZB-HySprintBox'
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == 'PbI2'
            assert m.data.solution[0].solution_details.solute[0].concentration_mol == 1.42 * ureg('mM').to(
                'mole/milliliter'
            )
            assert m.data.solution[0].solution_details.solute[0].chemical_id == '2393-752-02-3'
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == 'DMF'
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 10 * ureg('uL').to('mL')
            assert m.data.solution[0].solution_details.solvent[0].chemical_id == '1592-461-04-2'
            assert m.data.annealing.temperature == ureg.Quantity(120, ureg('°C'))
            assert m.data.annealing.atmosphere == 'Nitrogen'
            assert m.data.annealing.time == 30 * ureg('minute')
            assert m.data.properties.print_head_properties.active_nozzles == 'all'
            assert m.data.properties.print_head_properties.number_of_active_print_nozzles == 128
            assert m.data.properties.print_head_properties.print_head_angle == 13 * ureg('deg')
            assert m.data.properties.print_head_properties.print_head_distance_to_substrate == 12 * ureg('mm')
            assert m.data.properties.print_head_properties.print_speed == 10 * ureg('mm/s')
            assert m.data.properties.substrate_height == 20 * ureg('mm')
            assert m.data.properties.print_head_properties.print_nozzle_drop_frequency == 5000 * ureg('1/s')
            assert m.data.properties.print_head_properties.print_nozzle_drop_volume == 10 * ureg('pL')
            assert m.data.properties.print_head_properties.print_head_temperature == ureg.Quantity(
                35, ureg('°C')
            )
            assert m.data.properties.print_head_properties.print_head_name == 'Spectra 0.8uL'
            assert m.data.properties.cartridge_pressure == ureg.Quantity(0.3, ureg('bar')).to('mbar')
            assert m.data.properties.substrate_temperature == ureg.Quantity(40, ureg('°C'))
            assert m.data.properties.drop_density == 400 * ureg('1/in')
            assert m.data.properties.drop_density_y == 300 * ureg('1/in')
            assert m.data.properties.printed_area == 100 * ureg('mm**2')
            assert m.data.properties.image_used == 'Square inch 300 dpi'
            assert m.data.print_head_path.quality_factor == '3'
            assert m.data.print_head_path.step_size == '10'
            assert m.data.print_head_path.directional == '10'
            assert m.data.print_head_path.swaths == 10
            assert m.data.nozzle_voltage_profile.config_file == 'testfile.txt'
            assert m.data.atmosphere.relative_humidity == 45
            assert m.data.quenching.vacuum_properties.pressure == 10 * ureg('mbar')
            assert m.data.quenching.vacuum_properties.start_time == 5 * ureg('s')
            assert m.data.quenching.vacuum_properties.duration == 15 * ureg('s')
            assert m.data.quenching.vacuum_properties.temperature == ureg.Quantity(25, ureg('°C'))
            assert m.data.quenching.gas_quenching_properties.gas == 'Nitrogen'
            assert m.data.quenching.gas_quenching_properties.duration == 15 * ureg('s')
            assert m.data.quenching.gas_quenching_properties.pressure == 100 * ureg('mbar').to('bar')
            assert m.data.quenching.gas_quenching_properties.nozzle_shape == 'round'
            assert m.data.quenching.gas_quenching_properties.nozzle_type == 'mesh'
            assert m.data.quenching.comment == 'blabla'

    delete_json()
