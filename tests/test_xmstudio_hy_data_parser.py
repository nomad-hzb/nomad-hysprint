from pathlib import Path

import pytest

TEST_FILE = 'tests/data/HZB_Test_1_3_C-3.03_S2_ITO-2PACz-DMF-old.hy.data'


@pytest.fixture(scope='module')
def raw_df():
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import (
        add_experiment_step_columns,
        import_xmstudio_binary_data,
    )

    blob = Path(TEST_FILE).read_bytes()
    return add_experiment_step_columns(import_xmstudio_binary_data(blob))


def test_raw_dataframe_shape(raw_df):
    assert raw_df.shape[0] == 12172
    for col in ('record_type', 'step_name', 'technique', 'experiment_step', 'cycle_number'):
        assert col in raw_df.columns


def test_record_types(raw_df):
    assert set(raw_df['record_type'].unique()) == {'timeseries', 'impedance', 'dpv'}


def test_techniques(raw_df):
    assert set(raw_df['technique'].unique()) == {'OCP', 'Impedance', 'Potentiostatic', 'DPV', 'CV'}


def test_step_names(raw_df):
    expected = {
        'Open Circuit',
        'Potentiostatic Impedance',
        'Potentiostatic',
        'Differential Pulse Voltammetry / Polarography',
        'Cycle 1',
        'Cycle 2',
        'Cycle 3',
        'Cycle 4',
    }
    assert set(raw_df['step_name'].unique()) == expected
    


def test_eis_extraction(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_impedance_data

    eis = extract_impedance_data(raw_df)
    assert not eis.empty
    assert list(eis.columns) == ['time', 'frequency', 'z_real', 'z_imaginary', 'z_modulus', 'z_angle']
    assert len(eis) == 71
    first = eis.iloc[0]
    assert first['time'] == pytest.approx(0.22, rel=1e-3)
    assert first['frequency'] == pytest.approx(1_000_000.0, rel=1e-3)
    assert first['z_real'] == pytest.approx(24.945, rel=1e-3)
    assert first['z_imaginary'] == pytest.approx(25.316, rel=1e-3)
    assert first['z_modulus'] == pytest.approx(35.541, rel=1e-3)
    assert first['z_angle'] == pytest.approx(-45.422, rel=1e-3)
    last = eis.iloc[-1]
    assert last['frequency'] == pytest.approx(0.1, rel=1e-3)
    assert last['z_real'] == pytest.approx(2786.177, rel=1e-3)


def test_dpv_extraction(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_dpv_data

    dpv = extract_dpv_data(raw_df)
    assert not dpv.empty
    assert list(dpv.columns) == ['time', 'voltage', 'current']
    assert len(dpv) == 150
    first = dpv.iloc[0]
    assert first['time'] == pytest.approx(1.124, rel=1e-3)
    assert first['voltage'] == pytest.approx(-0.2919, rel=1e-3)
    assert first['current'] == pytest.approx(1.1656e-05, rel=1e-3)


def test_ocp_extraction(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_ocp_data

    ocp = extract_ocp_data(raw_df)
    assert not ocp.empty
    assert list(ocp.columns) == ['time', 'voltage', 'current']
    assert len(ocp) == 11
    first = ocp.iloc[0]
    assert first['time'] == pytest.approx(0.01, rel=1e-3)
    assert first['voltage'] == pytest.approx(-0.22807, rel=1e-3)


def test_cv_scan_rates(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_cv_data_by_scan_rate

    cv = extract_cv_data_by_scan_rate(raw_df)
    assert set(cv.keys()) == {0.05, 0.1, 0.2, 0.3, 0.4, 0.5}


def test_cv_cycles(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_cv_data_by_scan_rate

    cv = extract_cv_data_by_scan_rate(raw_df)
    assert sorted(cv[0.05]['cycle_number'].dropna().unique().tolist()) == [1, 2, 3]
    assert sorted(cv[0.1]['cycle_number'].dropna().unique().tolist()) == [1, 2, 3, 4]
    
def test_cv_columns(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_cv_data_by_scan_rate

    cv = extract_cv_data_by_scan_rate(raw_df)
    for group in cv.values():
        for col in ('time', 'voltage', 'current', 'cycle_number', 'scan_rate'):
            assert col in group.columns


def test_cv_first_row_values(raw_df):
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import extract_cv_data_by_scan_rate

    cv = extract_cv_data_by_scan_rate(raw_df)
    first = cv[0.05].iloc[0]
    assert first['time'] == pytest.approx(2.023, rel=1e-3)
    assert first['voltage'] == pytest.approx(0.1983, rel=1e-3)
    assert first['current'] == pytest.approx(4.091e-05, rel=1e-3)


def test_empty_on_empty_bytes():
    from nomad_hysprint.schema_packages.file_parser.xmstudio_parser import import_xmstudio_binary_data

    result = import_xmstudio_binary_data(b'')
    assert result.empty
