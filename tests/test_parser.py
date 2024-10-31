import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch): 
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_hysprint.parsers.hysprint_measurement_parser.set_sample_reference', 
        mockreturn_search)
    
def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    file_name =  os.path.join('tests', 'data',file_base)
    file_archive = parse(file_name)[0]
    assert file_archive.data

    for file in os.listdir(os.path.join("tests/data")):
        if "archive.json" not in file:
            continue
        measurement = os.path.join(
            'tests', 'data', file
        )
        measurement_archive = parse(measurement)[0]

    for file in os.listdir(os.path.join("tests/data")):
        if not file.endswith("archive.json"):
            continue
        os.remove(os.path.join('tests', 'data', file))
        
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
        'HZB_Z_20230911_BatchZ_0_0.M01_encapsulatedGlass_front_TD3_withBE_ambient_intens.spv.txt'
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """         
    yield  get_archive(request.param, monkeypatch)

def test_normalize_all(parsed_archive, monkeypatch):
    normalize_all(parsed_archive)

    
def test_hy_jv_parser(monkeypatch):
    file = 'SE-ALM_RM_20231004_RM_KW40_0_8.jv.txt'
    archive =  get_archive(file, monkeypatch)
    normalize_all(archive)

    assert archive.data
    assert archive.data.jv_curve[0].voltage[0]
    assert abs(archive.data.jv_curve[2].efficiency -  0.37030243333333296) < 1e-6 
    


   

   

    
    
    
   
