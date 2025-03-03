import os

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from utils import delete_json, set_monkey_patch


def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name = os.path.join('tests', 'data', file_base)
    file_archive = parse(file_name)[0]
    assert file_archive.data

    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archive = parse(measurement)[0]

    return measurement_archive


@pytest.fixture(
    params=[
        '20240915_test_experiment.xlsx',
        'c-Si.nk',
        'HZB_MiGo_20240604_exp_0_0.eqe.txt',
        'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt',
        'AA142-2s10_10ms.pli.txt',
        'Cu.nk',
        'HZB_AlFl_20231009_Solarcells-Batch-2-varyHTL_1_0.pl.csv',
        'HZB_Test_1_1_C-1.sem.tif',
        'HZB_MiGo_20230913_Batch-Test-1_0_0.notessfdsf.jv.txt',
        'HZB_Z_20230911_BatchZ_0_0.M01_encapsulatedGlass_front_TD3_withBE_ambient_intens.spv.txt',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)
    delete_json()


def test_hy_jv_parser(monkeypatch):
    file = 'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.data.jv_curve[0].voltage[0]
    assert abs(archive.data.jv_curve[2].efficiency - 0.37030243333333296) < 1e-6
    delete_json()


def test_hy_batch_parser(monkeypatch):  # noqa: PLR0915
    file = '20250114_experiment_file.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == 27

    measurement_archives = []
    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    count_samples_batches = 0
    for m in measurement_archives:
        if 'Sample' in str(type(m.data)) or 'Batch' in str(type(m.data)):
            count_samples_batches += 1
            if 'Sample' in str(type(m.data)):
                assert m.data.description == 'A'
                assert m.data.number_of_junctions == 1
        elif 'Substrate' in str(type(m.data)):
            assert m.data.solar_cell_area == 10 * ureg('cm**2')
            assert m.data.pixel_area == 0.16 * ureg('cm**2')
            assert m.data.number_of_pixels == 6
            assert m.data.description == 'Normal'
            assert m.data.substrate == 'Glass'
            assert m.data.conducting_material[0] == 'ITO'

        elif m.data.positon_in_experimental_plan == 1:
            assert 'Cleaning' in str(type(m.data))
            assert m.data.cleaning[0].time == 100 * ureg('s')
            assert m.data.cleaning[0].temperature == ureg.Quantity(10, ureg('°C'))
            assert m.data.cleaning[0].solvent_2.name == 'Isopropanol'
            assert m.data.cleaning[1].time == 10 * ureg('minute')
            assert m.data.cleaning[1].temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.cleaning[1].solvent_2.name == 'Ethanol'
            assert m.data.cleaning_plasma[0].time == 20 * ureg('s')
            assert m.data.cleaning_plasma[0].power == 50 * ureg('W')
            assert m.data.cleaning_plasma[0].plasma_type == 'O2'

        elif m.data.positon_in_experimental_plan == 2:
            assert 'SpinCoating' in str(type(m.data))
            assert m.data.description == 'Bla'
            assert m.data.layer[0].layer_type == 'Absorber Layer'
            assert m.data.layer[0].layer_material_name == 'CsMAFA'
            assert m.data.annealing.temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.annealing.atmosphere == 'Ar'
            assert m.data.annealing.time == 10 * ureg('minute')
            assert m.data.solution[0].solution_volume == (1 * ureg('uL')).to('ml')
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == 'Ethanol'
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == (
                1 * ureg('uL')).to('ml')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == 'PbI2'
            assert m.data.solution[0].solution_details.solute[0].concentration_mass == 2 * ureg(
                'mg/ml')
            assert m.data.solution[0].solution_details.solute[0].amount_relative == 0.5
            assert m.data.recipe_steps[0].speed == 100 * ureg('rpm')
            assert m.data.recipe_steps[0].time == 10 * ureg('s')
            assert m.data.recipe_steps[0].acceleration == 100 * ureg('rpm/s')
            assert m.data.recipe_steps[1].speed == 10 * ureg('rpm')
            assert m.data.recipe_steps[1].time == 100 * ureg('s')
            assert m.data.recipe_steps[1].acceleration == 10 * ureg('rpm/s')
            assert m.data.quenching.anti_solvent_volume == 10 * ureg('ml')
            assert m.data.quenching.anti_solvent_dropping_time == 15 * ureg('s')
            assert m.data.quenching.anti_solvent_dropping_height == 10 * ureg('mm')
            assert m.data.quenching.anti_solvent_dropping_flow_rate == 100 * \
                ureg('uL/s')
            assert m.data.quenching.anti_solvent_2.name == 'Ethanol'

        elif m.data.positon_in_experimental_plan == 3:
            assert 'Inkjet' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'HTL'
            assert m.data.layer[0].layer_material_name == 'NiO2'
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == 'Ni'
            assert m.data.annealing.temperature == ureg.Quantity(14, ureg('°C'))
            assert m.data.annealing.atmosphere == 'N2'
            assert m.data.annealing.time == 100 * ureg('minute')
            assert m.data.properties.print_head_properties.number_of_active_print_nozzles == 10
            assert m.data.properties.print_head_properties.print_nozzle_drop_frequency == 10 * \
                ureg('1/s')
            assert m.data.properties.print_head_properties.print_nozzle_drop_volume == 10 * \
                ureg('pL')
            assert m.data.properties.print_head_properties.print_head_temperature == ureg.Quantity(
                10, ureg('°C')
            )
            assert m.data.properties.print_head_properties.print_head_name == 'abc'
            assert m.data.properties.cartridge_pressure == ureg.Quantity(
                1, ureg('bar')).to('mbar')
            assert m.data.properties.substrate_temperature == ureg.Quantity(
                500, ureg('°C'))
            assert m.data.properties.drop_density == 1 * ureg('1/in')
            assert m.data.properties.printed_area == 5 * ureg('mm**2')
            assert m.data.print_head_path.quality_factor == 'QF3'
            assert m.data.print_head_path.step_size == 'SS1'
            assert m.data.atmosphere.relative_humidity == 23

        elif m.data.positon_in_experimental_plan == 4:
            assert 'Atomic' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'ETL'
            assert m.data.layer[0].layer_material_name == 'Ar'
            assert m.data.properties.source == 'aa'
            assert m.data.properties.thickness == 10 * ureg('nm')
            assert m.data.properties.temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.properties.rate == 1 * ureg('angstrom/s')
            assert m.data.properties.time == 12 * ureg('s')
            assert m.data.properties.number_of_cycles == 10
            assert m.data.properties.material.material.name == '1'
            assert m.data.properties.material.pulse_duration == 12 * ureg('s')
            assert m.data.properties.material.manifold_temperature == ureg.Quantity(
                12, ureg('°C'))
            assert m.data.properties.material.bottle_temperature == ureg.Quantity(
                12, ureg('°C'))
            assert m.data.properties.oxidizer_reducer.material.name == '2'
            assert m.data.properties.oxidizer_reducer.pulse_duration == 2 * ureg('s')
            assert m.data.properties.oxidizer_reducer.manifold_temperature == ureg.Quantity(
                3, ureg('°C'))

        elif m.data.positon_in_experimental_plan == 5:
            assert 'Laser' in str(type(m.data))
            assert m.data.properties.laser_wavelength == 400 * ureg('nm')
            assert m.data.properties.laser_pulse_time == 10 * ureg('ps')
            assert m.data.properties.laser_pulse_frequency == 1 * ureg('kHz')
            assert m.data.properties.speed == 12 * ureg('mm/s')
            assert m.data.properties.fluence == 12 * ureg('J/cm**2')
            assert m.data.properties.power_in_percent == 3

        elif m.data.positon_in_experimental_plan == 6:
            assert 'SlotDie' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Absorber Layer'
            assert m.data.layer[0].layer_material_name == 'CsMaFa'
            assert m.data.annealing.temperature == ureg.Quantity(5, ureg('°C'))
            assert m.data.annealing.atmosphere == 'N2'
            assert m.data.annealing.time == 2 * ureg('minute')
            assert m.data.properties.flow_rate == (
                12 * ureg('uL/minute')).to('ml/minute')
            assert m.data.properties.slot_die_head_distance_to_thinfilm == 4 * \
                ureg('mm')
            assert m.data.properties.slot_die_head_speed == 2 * ureg('mm/s')
            assert m.data.quenching.air_knife_angle == 1 * ureg('°')
            assert m.data.quenching.bead_volume == 12 * ureg('mm/s')
            assert m.data.quenching.drying_speed == 12 * ureg('cm/minute')
            assert m.data.quenching.air_knife_distance_to_thin_film == (
                1 * ureg('cm')).to('um')

        elif m.data.positon_in_experimental_plan == 7:
            assert 'Evaporation' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Electron Transport Layer'
            assert m.data.layer[0].layer_material_name == 'Ar'
            assert m.data.inorganic_evaporation
            assert m.data.inorganic_evaporation[0].thickness == 10 * ureg('nm')
            assert m.data.inorganic_evaporation[0].pressure == (
                10 * ureg('bar')).to('mbar')
            assert m.data.inorganic_evaporation[0].pressure_start == 1 * ureg('mbar')
            assert m.data.inorganic_evaporation[0].pressure_end == 2 * ureg('mbar')
            assert m.data.inorganic_evaporation[0].tooling_factor is None
            assert m.data.inorganic_evaporation[0].substrate_temparature == ureg.Quantity(
                50, ureg('°C'))
            assert m.data.inorganic_evaporation[0].start_rate == 0.1 * \
                ureg('angstrom/s')
            assert m.data.inorganic_evaporation[0].target_rate == 1.5 * \
                ureg('angstrom/s')
            assert m.data.inorganic_evaporation[0].temparature[0] == ureg.Quantity(
                100, ureg('°C'))
            assert m.data.inorganic_evaporation[0].temparature[1] == ureg.Quantity(
                120, ureg('°C'))
        elif m.data.positon_in_experimental_plan == 8:
            assert 'Sputtering' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'HTL'
            assert m.data.layer[0].layer_material_name == 'Pd'
            assert m.data.processes[0].thickness == 10 * ureg('nm')
            assert m.data.processes[0].gas_flow_rate == 1 * ureg('cm**3/minute')
            assert m.data.processes[0].rotation_rate == 100 * ureg('rpm')
            assert m.data.processes[0].power == 23 * ureg('W')
            assert m.data.processes[0].temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.processes[0].deposition_time == 12 * ureg('s')
            assert m.data.processes[0].burn_in_time == 1 * ureg('s')
            assert m.data.processes[0].pressure == 1 * ureg('mbar')
            assert m.data.processes[0].target_2.name == 'Pd'
            assert m.data.processes[0].gas_2.name == 'N2'

        elif m.data.positon_in_experimental_plan == 9:
            assert 'Process' in str(type(m.data))
            assert m.data.name == 'Another process'

        else:
            assert False

    assert count_samples_batches == 17
    delete_json()


def test_hy_eqe_parser(monkeypatch):
    """Test the EQE parser integration with NOMAD."""
    # Use the provided EQE test file
    file = 'hzb_TestP_AA_2_c-5.eqe.txt'

    # Get archive using the helper function
    archive = get_archive(file, monkeypatch)

    # Normalize the archive
    normalize_all(archive)

    # Assert that data exists
    assert archive.data

    # Clean up
    delete_json()


def test_hy_batch_parser(monkeypatch):  # noqa: PLR0915
    file = '20250114_experiment_file.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == 27

    measurement_archives = []
    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    count_samples_batches = 0
    for m in measurement_archives:
        if 'Sample' in str(type(m.data)) or 'Batch' in str(type(m.data)):
            count_samples_batches += 1
            if 'Sample' in str(type(m.data)):
                assert m.data.description == 'A'
                assert m.data.number_of_junctions == 1
        elif 'Substrate' in str(type(m.data)):
            assert m.data.solar_cell_area == 10 * ureg('cm**2')
            assert m.data.pixel_area == 0.16 * ureg('cm**2')
            assert m.data.number_of_pixels == 6
            assert m.data.description == 'Normal'
            assert m.data.substrate == 'Glass'
            assert m.data.conducting_material[0] == 'ITO'

        # NEW TEST STARTS HERE
        # Test each process based on its position in the experimental plan
        if m.data.positon_in_experimental_plan == 1:
            # Test Step 1: Cleaning O2-Plasma
            assert 'CleaningProcess' in str(type(m.data))
            assert len(m.data.cleaning_steps) == 2
            assert m.data.cleaning_steps[0].solvent.name == "Hellmanex"
            assert m.data.cleaning_steps[0].time == 31 * ureg('s')
            assert m.data.cleaning_steps[0].temperature == 61 * ureg('°C')
            assert m.data.cleaning_steps[1].solvent.name == "Hellmanex"
            assert m.data.cleaning_steps[1].time == 32 * ureg('s')
            assert m.data.cleaning_steps[1].temperature == 62 * ureg('°C')
            assert m.data.plasma_cleaning.gas == "Oxygen"
            assert m.data.plasma_cleaning.time == 180 * ureg('s')
            assert m.data.plasma_cleaning.power == 50 * ureg('W')

        elif m.data.positon_in_experimental_plan == 2:
            # Test Step 2: Cleaning UV-Ozone
            assert 'CleaningProcess' in str(type(m.data))
            assert len(m.data.cleaning_steps) == 2
            assert m.data.cleaning_steps[0].solvent.name == "Hellmanex"
            assert m.data.cleaning_steps[0].time == 31 * ureg('s')
            assert m.data.cleaning_steps[0].temperature == 61 * ureg('°C')
            assert m.data.cleaning_steps[1].solvent.name == "Hellmanex"
            assert m.data.cleaning_steps[1].time == 32 * ureg('s')
            assert m.data.cleaning_steps[1].temperature == 62 * ureg('°C')
            assert m.data.uv_ozone_cleaning.time == 900 * ureg('s')

        elif m.data.positon_in_experimental_plan == 3:
            # Test Step 3: Spin Coating
            assert 'SpinCoating' in str(type(m.data))
            assert m.data.name == "spin coating Perovskite"
            assert m.data.location == "HyprintBox"
            assert m.data.description == "Test annealing"
            assert m.data.layer[0].layer_type == "Active Layer"
            assert m.data.layer[0].layer_material_name == "Perovskite"
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == "DMF"
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 10 * \
                ureg('uL')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1.5
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == "Lead Iodide"
            assert m.data.solution[0].solution_details.solute[0].concentration_molar == 1.42 * ureg(
                'mM')
            assert m.data.solution[0].solution_volume == 100 * ureg('uL')
            assert m.data.recipe_steps[0].speed == 1500 * ureg('rpm')
            assert m.data.recipe_steps[0].time == 30 * ureg('s')
            assert m.data.recipe_steps[0].acceleration == 500 * ureg('rpm/s')
            assert m.data.annealing.temperature == 120 * ureg('°C')
            assert m.data.annealing.atmosphere == "Nitrogen"
            assert m.data.annealing.time == 30 * ureg('minute')

        elif m.data.positon_in_experimental_plan == 4:
            # Test Step 4: Dip Coating
            assert 'DipCoating' in str(type(m.data))
            assert m.data.name == "dip coating Perovskite"
            assert m.data.location == "HyprintBox"
            assert m.data.description == "Test annealing"
            assert m.data.layer[0].layer_type == "Active Layer"
            assert m.data.layer[0].layer_material_name == "Perovskite"
            assert len(m.data.solution[0].solution_details.solvent) == 2
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == "DMF"
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 10 * \
                ureg('uL')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1.5
            assert m.data.solution[0].solution_details.solvent[1].chemical_2.name == "DMF"
            assert m.data.solution[0].solution_details.solvent[1].chemical_volume == 20 * \
                ureg('uL')
            assert m.data.solution[0].solution_details.solvent[1].amount_relative == 1.5
            assert len(m.data.solution[0].solution_details.solute) == 5
            for i in range(5):
                assert m.data.solution[0].solution_details.solute[i].chemical_2.name == "Lead Iodide"
                assert m.data.solution[0].solution_details.solute[i].concentration_molar == 1.42 * ureg(
                    'mM')
            assert m.data.dipping_duration == 15 * ureg('s')
            assert m.data.annealing.temperature == 120 * ureg('°C')
            assert m.data.annealing.atmosphere == "Nitrogen"
            assert m.data.annealing.time == 30 * ureg('minute')

        elif m.data.positon_in_experimental_plan == 5:
            # Test Step 5: Slot Die Coating
            assert 'SlotDieCoating' in str(type(m.data))
            assert m.data.name == "slot die coating Perovskite"
            assert m.data.location == "HyprintBox"
            assert m.data.description == "Test annealing"
            assert m.data.layer[0].layer_type == "Active Layer"
            assert m.data.layer[0].layer_material_name == "Perovskite"
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == "DMF"
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 10 * \
                ureg('uL')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1.5
            assert len(m.data.solution[0].solution_details.solute) == 2
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == "Lead Iodide"
            assert m.data.solution[0].solution_details.solute[0].concentration_molar == 1.42 * ureg(
                'mM')
            assert m.data.solution[0].solution_details.solute[1].chemical_2.name == "Lead Iodide"
            assert m.data.solution[0].solution_details.solute[1].concentration_molar == 1.42 * ureg(
                'mM')
            assert m.data.solution[0].solution_volume == 100 * ureg('uL')
            assert m.data.flow_rate == 25 * ureg('uL/min')
            assert m.data.head_gap == 0.3 * ureg('mm')
            assert m.data.speed == 15 * ureg('mm/s')
            assert m.data.air_knife_angle == 45 * ureg('degree')
            assert m.data.air_knife_gap == 0.5 * ureg('cm')
            assert m.data.bead_volume == 2 * ureg('mm/s')
            assert m.data.drying_speed == 30 * ureg('cm/min')
            assert m.data.annealing.temperature == 120 * ureg('°C')
            assert m.data.annealing.atmosphere == "Nitrogen"
            assert m.data.annealing.time == 30 * ureg('minute')

        elif m.data.positon_in_experimental_plan == 6:
            # Test Step 6: Inkjet Printing
            assert 'InkjetPrinting' in str(type(m.data))
            assert m.data.name == "inkjet printing Perovskite"
            assert m.data.location == "HyprintBox"
            assert m.data.description == "Test annealing"
            assert m.data.layer[0].layer_type == "Active Layer"
            assert m.data.layer[0].layer_material_name == "Perovskite"
            assert m.data.solution[0].solution_details.solvent[0].chemical_2.name == "DMF"
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == 10 * \
                ureg('uL')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1.5
            assert len(m.data.solution[0].solution_details.solute) == 2
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == "Lead Iodide"
            assert m.data.solution[0].solution_details.solute[0].concentration_molar == 1.42 * ureg(
                'mM')
            assert m.data.solution[0].solution_details.solute[1].chemical_2.name == "Lead Iodide"
            assert m.data.solution[0].solution_details.solute[1].concentration_molar == 1.42 * ureg(
                'mM')
            assert m.data.printhead_name == "Spectra 0.8uL"
            assert m.data.number_of_active_nozzles == 128
            assert m.data.droplet_density == 400 * ureg('dpi')
            assert m.data.quality_factor == 3
            assert m.data.step_size == 10
            assert m.data.printed_area == 100 * ureg('mm**2')
            assert m.data.droplet_per_second == 5000 * ureg('1/s')
            assert m.data.droplet_volume == 10 * ureg('pl')
            assert m.data.ink_reservoir_pressure == 0.3 * ureg('bar')
            assert m.data.table_temperature == 40 * ureg('°C')
            assert m.data.nozzle_temperature == 35 * ureg('°C')
            assert m.data.rel_humidity == 45 * ureg('percent')
            assert m.data.annealing.temperature == 120 * ureg('°C')
            assert m.data.annealing.atmosphere == "Nitrogen"
            assert m.data.annealing.time == 30 * ureg('minute')

        elif m.data.positon_in_experimental_plan == 7:
            # Test Step 7: Evaporation
            assert 'Evaporation' in str(type(m.data))
            assert m.data.name == "evaporation PCBM"
            assert m.data.location == "Hysprint Evap"
            assert m.data.description == "Test note"
            assert m.data.layer[0].layer_type == "Electron Transport Layer"
            assert m.data.layer[0].layer_material_name == "PCBM"
            assert m.data.organic == True
            assert m.data.base_pressure == 0.000001 * ureg('bar')
            assert m.data.pressure_start == 0.000005 * ureg('bar')
            assert m.data.pressure_end == 0.000003 * ureg('bar')
            assert m.data.source_temperature_start == 150 * ureg('°C')
            assert m.data.source_temperature_end == 160 * ureg('°C')
            assert m.data.substrate_temperature == 25 * ureg('°C')
            assert m.data.thickness == 100 * ureg('nm')
            assert m.data.rate_start == 0.5 * ureg('angstrom/s')
            assert m.data.rate_target == 1 * ureg('angstrom/s')
            assert m.data.tooling_factor == 1.5

        elif m.data.positon_in_experimental_plan == 8:
            # Test Step 8: Sublimation
            assert 'Sublimation' in str(type(m.data))
            assert m.data.name == "sublimation PCBM"
            assert m.data.location == "Hysprint Evap"
            assert m.data.description == "Test note"
            assert m.data.layer[0].layer_type == "Electron Transport Layer"
            assert m.data.layer[0].layer_material_name == "PCBM"
            assert m.data.organic == True
            assert m.data.base_pressure == 0.000001 * ureg('bar')
            assert m.data.pressure_start == 0.000005 * ureg('bar')
            assert m.data.pressure_end == 0.000003 * ureg('bar')
            assert m.data.source_temperature_start == 150 * ureg('°C')
            assert m.data.source_temperature_end == 160 * ureg('°C')
            assert m.data.substrate_temperature == 25 * ureg('°C')
            assert m.data.thickness == 100 * ureg('nm')
            assert m.data.rate_start == 0.5 * ureg('angstrom/s')
            assert m.data.rate_target == 1 * ureg('angstrom/s')
            assert m.data.tooling_factor == 1.5

        elif m.data.positon_in_experimental_plan == 9:
            # Test Step 9: Sequential Evaporation
            assert 'SequentialEvaporation' in str(type(m.data))
            assert m.data.name == "sequential evaporation Aluminium"
            assert m.data.location == "IRIS Evap"
            assert m.data.layer[0].layer_type == "Electrode"
            assert m.data.layer[0].layer_material_name == "Aluminium"
            assert m.data.base_pressure == 0.000001 * ureg('bar')
            assert m.data.pressure_start == 0.000005 * ureg('bar')
            assert m.data.pressure_end == 0.000003 * ureg('bar')
            assert m.data.substrate_temperature == 25 * ureg('°C')

        elif m.data.positon_in_experimental_plan == 10:
            # Test Step 10: Co-Evaporation
            assert 'CoEvaporation' in str(type(m.data))
            assert m.data.name == "co-evaporation Aluminium"
            assert m.data.location == "IRIS Evap"
            assert m.data.layer[0].layer_type == "Electrode"
            assert m.data.layer[0].layer_material_name == "Aluminium"
            assert m.data.base_pressure == 0.000001 * ureg('bar')
            assert m.data.pressure_start == 0.000005 * ureg('bar')
            assert m.data.pressure_end == 0.000003 * ureg('bar')
            assert m.data.substrate_temperature == 25 * ureg('°C')

        elif m.data.positon_in_experimental_plan == 11:
            # Test Step 11: Sputtering
            assert 'Sputtering' in str(type(m.data))
            assert m.data.name == "sputtering TiO2"
            assert m.data.location == "Hysprint tool"
            assert m.data.description == "Test Sputtering"
            assert m.data.layer[0].layer_type == "Electron Transport Layer"
            assert m.data.layer[0].layer_material_name == "TiO2"
            assert m.data.gas == "Argon"
            assert m.data.temperature == 200 * ureg('°C')
            assert m.data.pressure == 0.01 * ureg('mbar')
            assert m.data.deposition_time == 300 * ureg('s')
            assert m.data.burn_in_time == 60 * ureg('s')
            assert m.data.power == 150 * ureg('W')
            assert m.data.rotation_rate == 30 * ureg('rpm')
            assert m.data.thickness == 50 * ureg('nm')
            assert m.data.gas_flow_rate == 20 * ureg('cm**3/min')

        elif m.data.positon_in_experimental_plan == 12:
            # Test Step 12: Laser Scribing
            assert 'LaserScribing' in str(type(m.data))
            assert m.data.laser_wavelength == 532 * ureg('nm')
            assert m.data.laser_pulse_time == 8 * ureg('ps')
            assert m.data.laser_pulse_frequency == 80 * ureg('kHz')
            assert m.data.speed == 100 * ureg('mm/s')
            assert m.data.fluence == 0.5 * ureg('J/cm**2')
            assert m.data.power == 75 * ureg('percent')
            assert m.data.recipe_file == "test_scribing_recipe.xml"

        elif m.data.positon_in_experimental_plan == 13:
            # Test Step 13: ALD
            assert 'AtomicLayerDeposition' in str(type(m.data))
            assert m.data.name == "atomic layer deposition Al2O3"
            assert m.data.location == "IRIS ALD"
            assert m.data.layer[0].layer_type == "Electron Transport Layer"
            assert m.data.layer[0].layer_material_name == "Al2O3"
            assert m.data.source == "TMA"
            assert m.data.thickness == 25 * ureg('nm')
            assert m.data.temperature == 150 * ureg('°C')
            assert m.data.rate == 0.1 * ureg('A/s')
            assert m.data.time == 1800 * ureg('s')
            assert m.data.number_of_cycles == 250
            assert len(m.data.precursors) == 2
            assert m.data.precursors[0].name == "TMA"
            assert m.data.precursors[0].pulse_duration == 0.2 * ureg('s')
            assert m.data.precursors[0].manifold_temperature == 80 * ureg('°C')
            assert m.data.precursors[0].bottle_temperature == 25 * ureg('°C')
            assert m.data.precursors[1].name == "H2O"
            assert m.data.precursors[1].pulse_duration == 0.1 * ureg('s')
            assert m.data.precursors[1].manifold_temperature == 70 * ureg('°C')

        elif m.data.positon_in_experimental_plan == 14:
            # Test Step 14: Annealing
            assert 'Annealing' in str(type(m.data))
            assert m.data.description == "Test annealing process"
            assert m.data.temperature == 150 * ureg('°C')
            assert m.data.atmosphere == "Nitrogen"  # Note: fixing the typo in the data
            assert m.data.time == 60 * ureg('minute')
            assert m.data.relative_humidity == 35 * ureg('percent')

        elif m.data.positon_in_experimental_plan == 15:
            # Test Step 15: Generic Process
            assert 'GenericProcess' in str(type(m.data))
            assert m.data.name == "Test Generic Process"
            assert m.data.description == "This is a test generic process"

        else:
            assert False

    assert count_samples_batches == 17
    delete_json()


# def test_hy_batch_parser_2(monkeypatch):
#     file = '20240915_test_experiment.xlsx'
#     file_name = os.path.join('tests', 'data', file)
#     file_archive = parse(file_name)[0]
#     assert len(file_archive.data.processed_archive) == 13

#     measurement_archives = []
#     for file in os.listdir(os.path.join('tests/data')):
#         if 'archive.json' not in file:
#             continue
#         measurement = os.path.join('tests', 'data', file)
#         measurement_archives.append(parse(measurement)[0])
#     measurement_archives.sort(key=lambda x: x.metadata.mainfile)

#     count_samples_batches = 0
#     for m in measurement_archives:
#         if 'HySprint_Sample' in str(type(m.data)) or 'HySprint_Batch' in str(type(m.data)):
#             count_samples_batches += 1
#         if 'SlotDieCoating' in str(type(m.data)):
#             assert (
#                 m.data.layer[0].layer_material_name == 'Me4PACz'
#                 or m.data.layer[0].layer_material_name == 'MAFA'
#             )
#     assert count_samples_batches == 5
#     delete_json()
