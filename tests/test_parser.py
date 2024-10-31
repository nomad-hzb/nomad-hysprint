import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch): 
    def mockreturn_search(*args):
        return None
    monkeypatch.setattr(
     'nomad_hysprint.parsers.hysprint_parser.search_class', 
     mockreturn_search)
    monkeypatch.setattr(
     'nomad_hysprint.parsers.hysprint_parser.set_sample_reference', 
     mockreturn_search)
    monkeypatch.setattr(
     'nomad_hysprint.parsers.hysprint_parser.find_sample_by_id', 
     mockreturn_search)
    
    

@pytest.fixture(
    params=[
        '20240915_test_experiment.xlsx',
        'c-Si.nk',
        'ExampleData_TRPL_WithComments.txt',
        'HZB_MiGo_20240604_exp_0_0.eqe.txt',
        'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt',
        'A142-2s10_10ms.pli.txt',
        'Cu.nk',
        'HZB_AlFl_20231009_Solarcells-Batch-2-varyHTL_1_0.pl.csv',
        'HZB_Test_1_1_C-1.sem.tif',
        'AT-65.uvvis.dat',
        'HZB_MiGo_20230913_Batch-Test-1_0_0.notessfdsf.jv.txt',     
        'HZB_Z_20230911_BatchZ_0_0.M01_encapsulatedGlass_front_TD3_withBE_ambient_intens.spv.txt'
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
   
    set_monkey_patch(monkeypatch)

    rel_file = os.path.join('tests', 'data', request.param)
    file_archive = parse(rel_file)[0]
    measurement = os.path.join(
        'tests', 'data', request.param + '.archive.json'
    )
    assert file_archive.data.activity
    archive_json = ''
    for file in os.listdir(os.path.join("tests/data")):
        if "archive.json" not in file\
            or request.param.replace("#", "run") not in file:
            continue
        archive_json = file 
        measurement = os.path.join(
            'tests', 'data', archive_json
        )
        measurement_archive = parse(measurement)[0]


        if os.path.exists(measurement):
            os.remove(measurement)
    yield measurement_archive

    assert archive_json
   
    


def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)

    
def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name =  os.path.join('tests', 'data',file_base)
    parse(file_name)[0]
    for file in os.listdir(os.path.join("tests/data")):
        if "archive.json" not in file\
            or file_base.replace("#", "run") not in file:
            continue
        archive_json = file 
        measurement = os.path.join(
            'tests', 'data', archive_json
        )
        measurement_archive = parse(measurement)[0]


        if os.path.exists(measurement):
            os.remove(measurement)
        break
    normalize_all(measurement_archive)
    return measurement_archive

def test_hy_jv_parser(monkeypatch):
    file = 'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt'
    get_archive(file, monkeypatch)
    


   

   

    
    
    
   
