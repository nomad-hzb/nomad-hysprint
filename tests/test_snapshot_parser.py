import json
import os
import shutil
import sys
from datetime import datetime, timezone

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
SNAPSHOT = 'test_process_snapshot_v0.2.yaml'
BATCH_NOTE = 'test_batch_note.yaml'  # parsed together with test_process_library.yaml
LIBRARY = 'test_process_library.yaml'


@pytest.fixture(params=[SNAPSHOT, BATCH_NOTE])
def parsed_archive(request, monkeypatch):
    """Sets up data for testing and cleans up after the test."""
    delete_json()
    yield get_archive(request.param, monkeypatch)
    delete_json()


def test_normalize_all(parsed_archive):
    normalize_all(parsed_archive)


def snapshot():
    return load_snapshot(os.path.join(DATA_DIR, SNAPSHOT))


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


def named(entries, name):
    return [d for d in entries.values() if getattr(d, 'name', None) == name]


def test_snapshot(monkeypatch):
    archive, entries = parse_upload(SNAPSHOT, monkeypatch)
    data = archive.data
    assert data.snapshot_format == 'hzb-process-snapshot/v0.2'
    assert (data.generator, data.source_commit, data.library_commit) == ('test', 'abc1234', '0123456')
    assert data.provenance['library_version'] == '1.1'  # provenance is kept completely
    # field names NOMAD does not know are kept in the file and reported
    assert data.unread_parameters == ['Nozzle distance [mm] (process contact_ag)']
    assert len(data.processed_archive) == len(entries)

    assert sorted(e.lab_id for e in entries['HZB_TEST_8'].entities) == [
        f'HZB_TEST_8_{group}_C-{n}' for group, n in ('A1', 'A2', 'B3', 'B4', 'C5')
    ]
    assert entries['HZB_TEST_8_B'].description == 'S: absorber 1 rotation speed 5000 rpm'
    assert entries['HZB_TEST_8_A_C-2'].architecture == 'single junction'

    spin_coatings = by_type(entries, 'HySprint_SpinCoating')
    # same slot, different step names, but a different recipe with identical values: never merged
    assert spin_coatings['spin coating HTL-A'] == [[1, 2, 3, 4], [5]]
    # parameter_changes on a step: a changed value is its own entry
    assert spin_coatings['spin coating Absorber-A'] == [[1, 2, 5], [3, 4]]
    speeds = sorted(
        d.recipe_steps[0].speed.to('rpm').magnitude for d in named(entries, 'spin coating Absorber-A')
    )
    assert speeds == [4000, 5000]
    # parameter_changes of one sample
    assert by_type(entries, 'HySprint_Evaporation') == {'evaporation Ag': [[1, 3, 4, 5], [2]]}
    thicknesses = sorted(
        d.inorganic_evaporation[0].thickness.to('nm').magnitude for d in named(entries, 'evaporation Ag')
    )
    assert thicknesses == [80, 100]
    assert by_type(entries, 'HySprint_Sputtering') == {'sputtering IZO': [[3, 4]]}


def parse_variant(change, tmp_path, monkeypatch):
    """Parse a changed copy of the test snapshot; return the created entries."""
    set_monkey_patch(monkeypatch)
    data = snapshot()
    change(data)
    mainfile = tmp_path / 'variant.snapshot.json'
    mainfile.write_text(json.dumps(data))
    parse(str(mainfile))
    return {
        name: parse(str(tmp_path / name))[0].data
        for name in sorted(os.listdir(tmp_path))
        if name.endswith('.archive.json')
    }


def test_run_label_splits_entries(tmp_path, monkeypatch):
    """Same slot, recipe and values, but a different run: separate entries."""

    def change(data):
        data['sub_batches'][1]['steps'][1]['run'] = 'second session'  # B's hole transport layer

    entries = parse_variant(change, tmp_path, monkeypatch)
    assert by_type(entries, 'HySprint_SpinCoating')['spin coating HTL-A'] == [[1, 2], [3, 4], [5]]


def test_slot_groups_across_step_names(tmp_path, monkeypatch):
    """Different step name, same slot and recipe: one entry."""

    def change(data):
        data['sub_batches'][2]['steps'][1]['process'] = 'htl_a'  # C: 'hole transport layer', slot '2'

    entries = parse_variant(change, tmp_path, monkeypatch)
    assert by_type(entries, 'HySprint_SpinCoating')['spin coating HTL-A'] == [[1, 2, 3, 4, 5]]


def test_snapshot_parent_id(monkeypatch):
    _, entries = parse_upload(SNAPSHOT, monkeypatch)
    assert entries['HZB_TEST_8_C_C-5'].parent.lab_id == 'HZB_TEST_8_A_C-1'
    assert entries['HZB_TEST_8_A_C-1'].parent is None


def test_snapshot_datetimes(monkeypatch):
    _, entries = parse_upload(SNAPSHOT, monkeypatch)
    # experiment date on samples and substrates
    assert entries['HZB_TEST_8_A_C-1'].datetime == datetime(2026, 3, 5, tzinfo=timezone.utc)
    substrates = [d for d in entries.values() if type(d).__name__ == 'HySprint_Substrate']
    assert {d.datetime for d in substrates} == {datetime(2026, 3, 5, tzinfo=timezone.utc)}
    # process Datetime '2026-03-05T10:30:00+01:00' is stored as 09:30 UTC
    absorbers = named(entries, 'spin coating Absorber-A')
    assert {d.datetime for d in absorbers} == {datetime(2026, 3, 5, 9, 30, tzinfo=timezone.utc)}


def test_spin_delay_stored(monkeypatch):
    _, entries = parse_upload(SNAPSHOT, monkeypatch)
    absorbers = named(entries, 'spin coating Absorber-A')
    assert all(d.recipe_steps[0].spin_delay == 0.5 * ureg('s') for d in absorbers)


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
    assert entries['HZB_TEST_9_D_C-6'].parent.lab_id == 'HZB_TEST_9_A_C-1'
    assert entries['HZB_TEST_9_A_C-1'].datetime == datetime(2026, 3, 4, tzinfo=timezone.utc)
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
    copper = named(entries, 'evaporation Cu')[0]
    assert copper.inorganic_evaporation[0].pressure.to('bar').magnitude == pytest.approx(8e-7)


def test_batch_note_without_library(tmp_path, monkeypatch):
    set_monkey_patch(monkeypatch)
    shutil.copy(os.path.join(DATA_DIR, BATCH_NOTE), tmp_path)
    with pytest.raises(ValueError, match='No process library'):
        parse(str(tmp_path / BATCH_NOTE))


@pytest.mark.parametrize(
    'old, new, message',
    [
        ('htl_b', 'htl_bb', r'Process "htl_bb" \(group B, step "transport layer 1"\).*Did you mean "htl_b"'),
        ('sample_type: S\n', 'sample_type: XYZ\n', r'Sample type "XYZ" \(group A\)'),
        ('{6: HZB_TEST_9_A_C-1}', '{8: HZB_TEST_9_A_C-1}', r'Group D: parent_ids for samples \[8\]'),
    ],
)
def test_batch_note_errors(old, new, message, tmp_path, monkeypatch):
    set_monkey_patch(monkeypatch)
    shutil.copy(os.path.join(DATA_DIR, LIBRARY), tmp_path)
    with open(os.path.join(DATA_DIR, BATCH_NOTE), encoding='utf-8') as f:
        (tmp_path / BATCH_NOTE).write_text(f.read().replace(old, new, 1))
    with pytest.raises(ValueError, match=message):
        parse(str(tmp_path / BATCH_NOTE))


@pytest.mark.parametrize(
    'change, message',
    [
        (lambda s: s.update(format='hzb-process-snapshot/v0.1'), 'Unsupported snapshot format'),
        (lambda s: s['experiment'].update(project='MY_PROJECT'), 'experiment/project'),
        (lambda s: s['experiment'].update(date='04.03.2025'), 'experiment/date'),
        (
            lambda s: s['processes']['contact_ag']['parameters'].update({'Base pressure [bar]': '=8*10^-7'}),
            'processes/contact_ag/parameters/Base pressure [bar]',
        ),
        (lambda s: s['processes']['izo'].update(method='Sputter'), 'processes/izo/method'),
        (lambda s: s['processes']['izo']['parameters'].pop('Material name'), "'Material name' is a required"),
        (lambda s: s['sub_batches'][0]['steps'][0].pop('slot'), "'slot' is a required property"),
        (
            lambda s: s['sub_batches'][1]['steps'][3].update(process='izo_typo'),
            'refers to process "izo_typo"',
        ),
        (lambda s: s['sub_batches'][1]['samples'].append({'number': 2}), 'sample number 2 is also used'),
        (
            lambda s: s['sub_batches'][0]['samples'][0].update(nomad_id='HZB_TEST_8_B_C-1'),
            'should be "HZB_TEST_8_A_C-1"',
        ),
        (lambda s: s['sub_batches'][0]['steps'][1].update(position=1), 'step positions are not unique'),
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
        (
            lambda s: s['processes']['absorber']['parameters'].update(Datetime='05.03.2026 10:30'),
            'processes/absorber/parameters/Datetime: "05.03.2026 10:30" is not an ISO 8601 date',
        ),
        (
            lambda s: s['sub_batches'][1]['steps'][2]['parameter_changes'].update(Datetime='yesterday'),
            'sub_batches/1/steps/2/parameter_changes/Datetime: "yesterday" is not an ISO 8601 date',
        ),
        (lambda s: s['provenance'].update(generated_at='today'), 'provenance/generated_at: "today"'),
    ],
)
def test_validation_errors(change, message):
    data = snapshot()
    change(data)
    with pytest.raises(ValueError) as error:
        validate_snapshot(data)
    assert message in str(error.value)


@pytest.mark.parametrize(
    'value, stored',
    [
        ('2026-03-05', '2026-03-05'),
        ('2026-03-05 10:30', '2026-03-05 10:30:00'),
        ('2026-03-05T10:30:15', '2026-03-05 10:30:15'),
        ('2026-03-05T10:30:00+01:00', '2026-03-05 09:30:00'),
        ('2026-03-05T10:30:00Z', '2026-03-05 10:30:00'),
    ],
)
def test_datetimes_normalized(value, stored):
    data = snapshot()
    data['processes']['absorber']['parameters']['Datetime'] = value
    validate_snapshot(data)
    assert data['processes']['absorber']['parameters']['Datetime'] == stored


def test_unknown_field_names_accepted():
    data = snapshot()
    data['processes']['htl_a']['parameters']['Rotaton speed [rpm]'] = 1
    assert validate_snapshot(data) == 'v0.2'
    assert unread_parameters(data)['Rotaton speed [rpm]'] == ['process htl_a']


def test_entry_order():
    df = build_snapshot_dataframe(snapshot())
    headers = [h for h in dict.fromkeys(df.columns.get_level_values(0)) if h != 'Experiment Info']
    assert headers == [
        '1: Cleaning UV-Ozone',
        '2: Spin Coating',
        '3: Spin Coating',
        '4: Sputtering',
        '5: Evaporation',
    ]


def test_is_mainfile(tmp_path):
    parser = entry_point.load()
    json_file = tmp_path / 'snapshot.json'
    json_file.write_text(json.dumps(snapshot()))
    cases = [
        (os.path.join(DATA_DIR, SNAPSHOT), True),
        (str(json_file), True),
        (os.path.join(DATA_DIR, BATCH_NOTE), True),
        (os.path.join(DATA_DIR, LIBRARY), False),
        (supported_versions()['v0.2'], False),
    ]
    for path, expected in cases:
        with open(path, 'rb') as f:
            buffer = f.read()
        assert parser.is_mainfile(os.path.abspath(path), 'text/plain', buffer, buffer.decode()) is expected, (
            path
        )


def test_contract_lists_excel_template_names():
    """Every column of the Excel template is a known field name in the contract.

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
            known = definitions[slug(method)].get('x-known-field-names')
            if known is None:  # free-form (Generic Process)
                continue
            listed = set(known['anyOf'][0]['enum']) | {o['title'] for o in known['anyOf'][1:]}
            names = {normalize(n) for n in template_fields(method)}
            if method == EXPERIMENT_INFO:
                names -= PARSER_OWNED
            assert names <= listed, (version, method, sorted(names - listed))
