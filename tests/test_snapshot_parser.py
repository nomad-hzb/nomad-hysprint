import json
import os
import shutil
import sys

import pytest
from nomad.client import normalize_all, parse
from nomad.units import ureg

from nomad_hysprint.parsers import hysprint_process_snapshot_parser as entry_point
from nomad_hysprint.parsers.hysprint_snapshot_parser import (
    build_snapshot_dataframe,
    load_snapshot,
    supported_versions,
    unread_parameters,
    validate_snapshot,
)
from utils import delete_json, get_archive, set_monkey_patch

DATA_DIR = os.path.join('tests', 'data')
SNAPSHOT_V01 = 'test_process_snapshot_v0.1.yaml'
SNAPSHOT_V02 = 'test_process_snapshot_v0.2.yaml'
BATCH_NOTE = 'test_batch_note.yaml'  # parsed together with test_process_library.yaml
LIBRARY = 'test_process_library.yaml'


@pytest.fixture(params=[SNAPSHOT_V01, SNAPSHOT_V02, BATCH_NOTE])
def parsed_archive(request, monkeypatch):
    """Sets up data for testing and cleans up after the test."""
    delete_json()
    yield get_archive(request.param, monkeypatch)
    delete_json()


def test_normalize_all(parsed_archive):
    normalize_all(parsed_archive)


def snapshot(file=SNAPSHOT_V01):
    return load_snapshot(os.path.join(DATA_DIR, file))


def parse_upload(file, monkeypatch):
    """Parse a mainfile; return its archive and the created entries by file name."""
    set_monkey_patch(monkeypatch)
    delete_json()
    archive = parse(os.path.join(DATA_DIR, file))[0]
    entries = {}
    for name in sorted(os.listdir(DATA_DIR)):
        if name.endswith('.archive.json'):
            entries[name[: -len('.archive.json')]] = parse(os.path.join(DATA_DIR, name))[0].data
    delete_json()
    return archive, entries


def by_type(entries, class_name):
    """{entry name: sorted sample numbers} of the entries of one class."""
    result = {}
    for data in entries.values():
        if type(data).__name__ == class_name:
            numbers = sorted(int(s.lab_id.rsplit('-', 1)[1]) for s in data.samples)
            result.setdefault(data.name, []).append(numbers)
    return {name: sorted(groups) for name, groups in result.items()}


def test_snapshot_v01(monkeypatch):
    archive, entries = parse_upload(SNAPSHOT_V01, monkeypatch)
    data = archive.data
    assert data.snapshot_format == 'hzb-process-snapshot/v0.1'
    assert (data.generator, data.source_commit, data.library_commit) == ('test', 'abc1234', '0123456')
    assert data.provenance['source_note'] == 'experiments/test/TEST7_batch_note.yaml'
    assert not data.unread_parameters
    assert len(data.processed_archive) == len(entries)

    assert sorted(e.lab_id for e in entries['HZB_TEST_7'].entities) == [
        'HZB_TEST_7_A_C-1',
        'HZB_TEST_7_A_C-2',
        'HZB_TEST_7_B_C-3',
    ]
    assert entries['HZB_TEST_7_B'].description.endswith('test comment')
    assert entries['HZB_TEST_7_A_C-2'].architecture == 'single junction'
    assert by_type(entries, 'HySprint_SpinCoating') == {
        'spin coating HTL-A': [[1, 2]],
        'spin coating HTL-B': [[3]],
        'spin coating Absorber-A': [[1, 2, 3]],
    }
    assert by_type(entries, 'HySprint_Evaporation') == {'evaporation Ag': [[1, 2, 3]]}
    assert by_type(entries, 'HySprint_Sputtering') == {'sputtering IZO': [[3]]}


def test_snapshot_v02(monkeypatch):
    archive, entries = parse_upload(SNAPSHOT_V02, monkeypatch)
    data = archive.data
    assert data.snapshot_format == 'hzb-process-snapshot/v0.2'
    assert data.provenance['library_version'] == '1.1'  # provenance is kept completely
    # field names NOMAD does not know are kept in the file and reported
    assert data.unread_parameters == ['Nozzle distance [mm] (process contact_ag)']

    spin_coatings = by_type(entries, 'HySprint_SpinCoating')
    # same slot, but a different recipe with identical values: never merged
    assert spin_coatings['spin coating HTL-A'] == [[1, 2, 3, 4], [5]]
    # parameter_changes on a step: a changed value is its own entry
    assert spin_coatings['spin coating Absorber-A'] == [[1, 2, 5], [3, 4]]
    # parameter_changes of one sample
    assert by_type(entries, 'HySprint_Evaporation') == {'evaporation Ag': [[1, 3, 4, 5], [2]]}

    absorbers = [d for d in entries.values() if getattr(d, 'name', '') == 'spin coating Absorber-A']
    speeds = sorted(d.recipe_steps[0].speed.to('rpm').magnitude for d in absorbers)
    assert speeds == [4000, 5000]
    evaporations = [d for d in entries.values() if type(d).__name__ == 'HySprint_Evaporation']
    thicknesses = sorted(d.inorganic_evaporation[0].thickness.to('nm').magnitude for d in evaporations)
    assert thicknesses == [80, 100]


def test_batch_note_with_library(monkeypatch):
    archive, entries = parse_upload(BATCH_NOTE, monkeypatch)
    data = archive.data
    assert data.snapshot_format == 'hzb-process-snapshot/v0.2'
    assert data.provenance['generator'] == 'nomad-hysprint batch note conversion'
    assert data.provenance['library'] == LIBRARY
    assert len(data.provenance['library_sha256']) == 64

    assert sorted(e.lab_id for e in entries['HZB_TEST_9'].entities) == [
        f'HZB_TEST_9_{group}_C-{n}' for group, n in ('A1', 'A2', 'B3', 'B4', 'C5', 'D6', 'D7')
    ]
    assert (
        entries['HZB_TEST_9_C'].description
        == 'single junction; transport layer 1: none; no hole transport layer'
    )
    assert by_type(entries, 'HySprint_SpinCoating') == {
        'spin coating HTL-A': [[1, 2, 6, 7]],
        'spin coating HTL-B': [[3, 4]],
        'spin coating Absorber-A': [[1, 2, 3, 4, 5, 6, 7]],
    }
    assert by_type(entries, 'HySprint_Evaporation') == {
        'evaporation Ag': [[1, 2, 3, 4, 5]],
        'evaporation Cu': [[6, 7]],
    }
    # library formula '=8*10^-7' becomes a number
    copper = next(d for d in entries.values() if getattr(d, 'name', '') == 'evaporation Cu')
    assert copper.inorganic_evaporation[0].pressure.to('bar').magnitude == pytest.approx(8e-7)


def test_batch_note_without_library(tmp_path, monkeypatch):
    set_monkey_patch(monkeypatch)
    shutil.copy(os.path.join(DATA_DIR, BATCH_NOTE), tmp_path)
    with pytest.raises(ValueError, match='No process library'):
        parse(str(tmp_path / BATCH_NOTE))


def test_batch_note_unknown_process(tmp_path, monkeypatch):
    set_monkey_patch(monkeypatch)
    shutil.copy(os.path.join(DATA_DIR, LIBRARY), tmp_path)
    note = tmp_path / BATCH_NOTE
    text = open(os.path.join(DATA_DIR, BATCH_NOTE)).read().replace('htl_b', 'htl_bb')
    note.write_text(text)
    with pytest.raises(ValueError, match=r'Process "htl_bb" \(group B, step "transport layer 1"\).*"htl_b"'):
        parse(str(note))


@pytest.mark.parametrize(
    'change, message',
    [
        (lambda s: s.update(format='hzb-process-snapshot/v9'), 'Unsupported snapshot format'),
        (lambda s: s['experiment'].update(project='MY_PROJECT'), 'experiment/project'),
        (
            lambda s: s['processes']['contact_ag']['parameters'].update({'Base pressure [bar]': '=8*10^-7'}),
            'processes/contact_ag/parameters/Base pressure [bar]',
        ),
        (lambda s: s['processes']['izo'].update(method='Sputter'), 'processes/izo/method'),
        (
            lambda s: s['processes']['absorber']['parameters'].update({'Rotaton speed [rpm]': 4000}),
            'processes/absorber/parameters: unknown field "Rotaton speed [rpm]". '
            'Did you mean "Rotation speed [rpm]"?',
        ),
        (lambda s: s['processes']['izo']['parameters'].pop('Material name'), "'Material name' is a required"),
        (
            lambda s: s['sub_batches'][1]['steps'][3].update(process='izo_typo'),
            'refers to process "izo_typo"',
        ),
        (lambda s: s['sub_batches'][1]['samples'].append({'number': 2}), 'sample number 2 is also used'),
        (
            lambda s: s['sub_batches'][0]['samples'][0].update(nomad_id='HZB_TEST_7_B_C-1'),
            'should be "HZB_TEST_7_A_C-1"',
        ),
        (lambda s: s['sub_batches'][0]['steps'][1].update(position=1), 'step positions are not unique'),
    ],
)
def test_validation_errors_v01(change, message):
    data = snapshot()
    change(data)
    with pytest.raises(ValueError) as error:
        validate_snapshot(data)
    assert message in str(error.value)


@pytest.mark.parametrize(
    'change, message',
    [
        (lambda s: s['sub_batches'][0]['steps'][0].pop('slot'), "'slot' is a required property"),
        (
            lambda s: s['sub_batches'][0]['samples'][1]['parameter_changes'].update(
                {'no such step': {'x': 1}}
            ),
            'refer to step "no such step", which is not a step of this sub-batch',
        ),
        (
            lambda s: s['sub_batches'][1]['steps'][2].update(parameter_changes={}),
            'sub_batches/1/steps/2/parameter_changes',
        ),
    ],
)
def test_validation_errors_v02(change, message):
    data = snapshot(SNAPSHOT_V02)
    change(data)
    with pytest.raises(ValueError) as error:
        validate_snapshot(data)
    assert message in str(error.value)


def test_unknown_field_names_v02_accepted():
    data = snapshot(SNAPSHOT_V02)
    data['processes']['htl_a']['parameters']['Rotaton speed [rpm]'] = 1
    assert validate_snapshot(data) == 'v0.2'
    assert unread_parameters(data)['Rotaton speed [rpm]'] == ['process htl_a']


def process_headers(df):
    return [h for h in dict.fromkeys(df.columns.get_level_values(0)) if h != 'Experiment Info']


def test_ordering_v01():
    data = snapshot()
    assert process_headers(build_snapshot_dataframe(data)) == [
        '1: Cleaning UV-Ozone',
        '2: Spin Coating',
        '3: Spin Coating',
        '4: Sputtering',
        '5: Evaporation',
    ]
    for sub_batch in data['sub_batches']:  # without excel_section: by step order and name
        for step in sub_batch['steps']:
            del step['excel_section']
    assert len(process_headers(build_snapshot_dataframe(data))) == 5
    data['sub_batches'][1]['steps'][2]['run'] = 'second session'  # a run label splits
    assert len(process_headers(build_snapshot_dataframe(data))) == 6


def test_ordering_v02():
    assert process_headers(build_snapshot_dataframe(snapshot(SNAPSHOT_V02))) == [
        '1: Cleaning UV-Ozone',
        '2: Spin Coating',
        '3: Spin Coating',
        '4: Sputtering',
        '5: Evaporation',
    ]


def test_is_mainfile(tmp_path):
    parser = entry_point.load()
    json_file = tmp_path / 'snapshot.json'
    json_file.write_text(json.dumps(snapshot(SNAPSHOT_V02)))
    contract = supported_versions()['v0.2']
    cases = [
        (os.path.join(DATA_DIR, SNAPSHOT_V01), True),
        (os.path.join(DATA_DIR, SNAPSHOT_V02), True),
        (str(json_file), True),
        (os.path.join(DATA_DIR, BATCH_NOTE), True),
        (os.path.join(DATA_DIR, LIBRARY), False),
        (contract, False),
    ]
    for path, expected in cases:
        with open(path, 'rb') as f:
            buffer = f.read()
        assert parser.is_mainfile(os.path.abspath(path), 'text/plain', buffer, buffer.decode()) is expected, (
            path
        )


def test_contracts_list_excel_template_names():
    """Every column of the Excel template is a known field name in every contract version.

    (The names read by the mappers are added by the same generator; they live in
    nomad-baseclasses, so they are not checked here.)
    """
    sys.path.insert(0, os.path.join('utils', 'snapshot_contract'))
    from update_contract_fields import (
        EXPERIMENT_INFO,
        MAPPERS,
        PARSER_OWNED,
        normalize,
        slug,
        template_fields,
    )

    for version, path in supported_versions().items():
        with open(path, encoding='utf-8') as f:
            definitions = json.load(f)['$defs']
        for method in MAPPERS:
            definition = definitions[slug(method)]
            known = definition.get('propertyNames') or definition.get('x-known-field-names')
            if known is None:  # free-form (Generic Process)
                continue
            listed = set(known['anyOf'][0]['enum']) | {o['title'] for o in known['anyOf'][1:]}
            names = {normalize(n) for n in template_fields(method)}
            if method == EXPERIMENT_INFO:
                names -= PARSER_OWNED
            assert names <= listed, (version, method, sorted(names - listed))


def test_spin_delay_stored(monkeypatch):
    _, entries = parse_upload(SNAPSHOT_V02, monkeypatch)
    absorbers = [d for d in entries.values() if getattr(d, 'name', '') == 'spin coating Absorber-A']
    assert all(d.recipe_steps[0].spin_delay == 0.5 * ureg('s') for d in absorbers)
