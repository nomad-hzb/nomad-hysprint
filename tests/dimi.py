import os 
from nomad.client import parse

# mainfile_path = "nomad-hysprint/tests/data/hzb_TestP_AA_2_c-5.mppt.txt"
# print(f"Mainfile path {mainfile_path}")
# mainfile = os.path.basename(mainfile_path)
# print(f"Mainfile {mainfile}")
# print(os.path.abspath(mainfile_path))
# directory = os.path.dirname(mainfile_path)
# print(directory)
# print(os.listdir(os.path.join('tests/data')))
# print(os.path.join('tests', 'data', mainfile))
# #parse(mainfile_path)




# def parser():
#     entry_archive = EntryArchive(m_context=ParserContext(directory))
#     entry_archive.metadata = EntryMetadata()
#     entry_archive.metadata.mainfile = mainfile_path
#     entry_archives = [entry_archive]
#     return entry_archives

import os

import pytest
from nomad.client import normalize_all, parse


def set_monkey_patch(monkeypatch):
    def mockreturn_search(*args):
        return None

    monkeypatch.setattr(
        'nomad_hysprint.parsers.hysprint_measurement_parser.set_sample_reference',
        mockreturn_search,
    )

    monkeypatch.setattr(
        'nomad_hysprint.schema_packages.hysprint_package.set_sample_reference',
        mockreturn_search,
    )


def delete_json():
    for file in os.listdir(os.path.join('tests/data')):
        if not file.endswith('archive.json'):
            continue
        os.remove(os.path.join('tests', 'data', file))


def get_archive(file_base, monkeypatch):
    set_monkey_patch(monkeypatch)
    mainfile_path = os.path.join('tests', 'data', file_base)
    file_archive = parse(mainfile_path)[0] # parse() -> [EntryArchive(data, metadata)]
    assert file_archive.data # -> RawFileHZB(processed_archive)
    assert file_archive.metadata # -> EntryMetadata(entry_name, mainfile, domain)

    for file in os.listdir(os.path.join('tests/data')):
        if 'archive.json' not in file:
            continue
        measurement_path = os.path.join('tests', 'data', file)
        measurement_archive = parse(measurement_path)[0]

    return measurement_archive


@pytest.fixture(
    params=[
        'hzb_TestP_AA_2_c-5.mppt.txt',
    ]
)
def parsed_archive(request, monkeypatch):
    """
    Sets up data for testing and cleans up after the test.
    """
    yield get_archive(request.param, monkeypatch)


def test_normalize_all(parsed_archive):
    normalize_all(parsed_archive)
    delete_json()


def test_mppt_simple_parser(monkeypatch):
    file = 'hzb_TestP_AA_2_c-5.mppt.txt'
    archive = get_archive(file, monkeypatch)
    normalize_all(archive) #what does normalizer do, how does it run and why do we need it here since it returns nothing?
    assert archive.data
    assert archive.metadata
    #print(dir(archive))
    #print(archive.data) # -> hzb_TestP_AA_2_c-5 :HySprint_SimpleMPPTracking(name, datetime, description, data_file, steps, samples, instruments, results, atmosphere)
    #print(dir(archive.data))
    #print(archive.metadata) # -> EntryMetadata(entry_name, mainfile, section_defs, entry_references, search_quantities)
    delete_json()