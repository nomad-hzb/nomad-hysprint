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
"""Turn a batch note and its process library into a process snapshot.

Instead of a generated snapshot, a batch can be uploaded as two YAML files:

* a process library: the default layer stack of every cell type
  (``cell_types``) and the parameters of every process (``components``), and
* a batch note: the sample groups of one batch (``samples``), their cell type
  and the steps in which they deviate from the library.

The batch note is the mainfile; the library is looked up in the same upload.
Both are merged into a snapshot of the latest contract version, which is then
validated and parsed like an uploaded snapshot.
"""

import datetime
import difflib
import hashlib
import os
import re

import yaml

SNAPSHOT_VERSION = 'hzb-process-snapshot/v0.2'
REMOVED_STEP = 'none'
DEFAULT_LAB = 'HZB'
# Experiment Info columns that the snapshot states in its own fields
STRUCTURE_COLUMNS = ('Date', 'Project_Name', 'Batch', 'Subbatch', 'Sample', 'Nomad ID')
_formula_re = re.compile(r'^[\d\s.eE+\-*/()^]+$')


def is_batch_note(data):
    """A batch note maps sample groups to their sample numbers and cell type."""
    groups = data.get('samples') if isinstance(data, dict) else None
    return (
        isinstance(groups, dict)
        and bool(groups)
        and all(isinstance(g, dict) and 'sample_type' in g and 'sample_numbers' in g for g in groups.values())
    )


def is_process_library(data):
    return isinstance(data, dict) and isinstance(data.get('cell_types'), dict) and 'components' in data


def parse_sample_numbers(spec):
    """Expand '1-2', '1,3,5-7' or 4 into a list of sample numbers."""
    if isinstance(spec, int):
        return [spec]
    numbers = []
    for raw_part in str(spec).split(','):
        part = raw_part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = (int(x) for x in part.split('-', 1))
            numbers.extend(range(start, end + 1))
        else:
            numbers.append(int(part))
    return numbers


def to_value(value):
    """Library values as the snapshot expects them: formulas such as '=8*10^-7' become numbers."""
    if isinstance(value, str) and value.startswith('='):
        expression = value[1:]
        if _formula_re.match(expression):
            try:
                return float(eval(expression.replace('^', '**'), {'__builtins__': {}}, {}))
            except Exception:
                pass
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def not_found_message(kind, name, where, known, list_known=False):
    message = f'{kind} "{name}" ({where}) not found in the process library.'
    known = sorted(str(k) for k in known)
    close = difflib.get_close_matches(str(name), known, n=1, cutoff=0.6)
    if close:
        message += f' Did you mean "{close[0]}"?'
    elif list_known and known:
        message += f' Known: {", ".join(known)}.'
    return message


def section_number(section):
    match = re.match(r'^\s*(\d+)\s*:', str(section or ''))
    return int(match.group(1)) if match else None


def resolve_steps(library, cell_type, overrides, components, group_id, logger=None):
    """Ordered (step name, process, default process) of one sample group, and the removed steps.

    The library's common steps come first, then the cell type's steps. The
    batch note replaces the process of a step by its step name; 'none' removes
    the step.
    """
    defaults = dict(library.get('common_steps') or {})
    defaults.update(cell_type.get('steps') or {})
    steps = dict(defaults)
    for step_name, process in overrides.items():
        if str(process).strip().lower() != REMOVED_STEP and process not in components:
            raise ValueError(
                not_found_message('Process', process, f'group {group_id}, step "{step_name}"', components)
            )
        if step_name not in defaults and logger:
            logger.warning(
                'batch note step not in the cell type, added at the end', step=step_name, group=group_id
            )
        steps[step_name] = process
    for step_name, process in defaults.items():
        if step_name not in overrides and process not in components:
            raise ValueError(
                not_found_message(
                    'Process',
                    process,
                    f'default of cell type "{cell_type.get("alias")}", step "{step_name}"',
                    components,
                )
            )
    kept = [
        (name, process, defaults.get(name))
        for name, process in steps.items()
        if process is not None and str(process).strip().lower() != REMOVED_STEP
    ]
    removed = [name for name, process in steps.items() if str(process).strip().lower() == REMOVED_STEP]
    return kept, removed


def assign_slots(steps, components, library_sections):
    """Slot label of every step: the same layer position of the batch gets the same slot.

    The slot is the number of the library 'section' of the step's default
    process, so a varied step stays in the slot of the step it replaces. Steps
    without a section are placed in the gap between their neighbours, e.g.
    between section 17 and 19 a sputtering step gets slot '18'.
    """
    numbers = [
        section_number(components[default if default is not None else process].get('section'))
        for _, process, default in steps
    ]
    slots = []
    for index, section in enumerate(numbers):
        slot = section
        if slot is None:
            previous = max([n for n in numbers[:index] if n is not None], default=0)
            following = min([n for n in numbers[index + 1 :] if n is not None], default=None)
            candidate = previous + 1
            fits = (following is None or candidate < following) and candidate not in library_sections
            slot = candidate if fits else previous + 0.5
        slots.append(f'{slot:g}')
    return slots


def batch_note_to_snapshot(note, library, provenance, logger=None):
    """Merge a batch note and its process library into a snapshot (latest contract version)."""
    components = library.get('components') or {}
    cell_types = {}
    for key, cell_type in (library.get('cell_types') or {}).items():
        cell_types[key] = dict(cell_type, id=key)
        if cell_type.get('alias'):
            cell_types[cell_type['alias']] = cell_types[key]
    library_sections = {
        n for n in (section_number(c.get('section')) for c in components.values()) if n is not None
    }

    defaults = {k: to_value(v) for k, v in (library.get('experiment_defaults') or {}).items()}
    template = str(library.get('nomad_id_template', ''))
    lab = template.split('_', 1)[0] if template and '{' not in template.split('_', 1)[0] else DEFAULT_LAB
    experiment = {
        'lab': lab,
        'project': str(note.get('project', defaults.get('Project_Name', ''))),
        'batch': str(note.get('batch', defaults.get('Batch', ''))),
        'properties': {k: v for k, v in defaults.items() if k not in STRUCTURE_COLUMNS},
    }
    date = to_value(note.get('date', defaults.get('Date')))
    if date:
        experiment['date'] = str(date)

    sub_batches, used = [], {}
    for group_id, group in note['samples'].items():
        type_key = group.get('sample_type')
        if type_key not in cell_types:
            raise ValueError(
                not_found_message('Sample type', type_key, f'group {group_id}', cell_types, list_known=True)
            )
        cell_type = cell_types[type_key]
        overrides = group.get('steps') or {}
        steps, removed = resolve_steps(library, cell_type, overrides, components, group_id, logger)
        slots = assign_slots(steps, components, library_sections)

        display_name = cell_type.get('display_name') or type_key
        variation = [display_name] + [
            f'{step}: {components.get(p, {}).get("display_name", p)}' for step, p in overrides.items()
        ]
        sub_batch = {
            'id': str(group_id),
            'cell_type': {
                'id': cell_type['id'],
                'alias': cell_type.get('alias'),
                'display_name': display_name,
            },
            'variation': '; '.join(str(v) for v in variation),
            'sample_properties': {
                k: to_value(v) for k, v in (cell_type.get('sample_properties') or {}).items()
            },
            'samples': [{'number': n} for n in parse_sample_numbers(group.get('sample_numbers'))],
            'steps': [],
        }
        for key in ('lab_comment', 'notes'):
            if group.get(key):
                sub_batch[key] = str(group[key])
        if removed:
            sub_batch['omitted_steps'] = removed
        for position, ((name, process, default), slot) in enumerate(zip(steps, slots), start=1):
            step = {'position': position, 'name': name, 'process': process, 'slot': slot}
            if default is not None and process != default:
                step['varied_from'] = default
                used[default] = components[default]
            sub_batch['steps'].append(step)
            used[process] = components[process]
        sub_batches.append(sub_batch)

    processes = {
        key: {
            'display_name': component.get('display_name') or key,
            'method': component.get('method') or 'Generic Process',
            'parameters': {k: to_value(v) for k, v in (component.get('values') or {}).items()},
        }
        for key, component in used.items()
    }
    return {
        'format': SNAPSHOT_VERSION,
        'provenance': provenance,
        'experiment': experiment,
        'sub_batches': sub_batches,
        'processes': processes,
    }


def upload_raw_root(mainfile, archive):
    """The upload's raw directory (from the archive's context), else the mainfile's directory."""
    mainfile_dir = os.path.dirname(os.path.abspath(mainfile))
    context = getattr(archive, 'm_context', None)
    roots = []
    try:
        roots.append(context.raw_path())
    except Exception:
        pass
    roots.append(getattr(context, 'local_dir', None))
    for candidate in roots:
        if not candidate:
            continue
        root = os.path.abspath(candidate)
        if root != os.sep and os.path.commonpath([root, mainfile_dir]) == root:
            return root
    return mainfile_dir


def find_process_library(mainfile, archive, note, logger=None):
    """The process library for a batch note: its 'library' path, else a library in the upload."""
    reference = note.get('library')
    if reference:
        path = os.path.normpath(os.path.join(os.path.dirname(mainfile), str(reference)))
        if os.path.isfile(path):
            return path
    candidates = []
    for directory, _, files in os.walk(upload_raw_root(mainfile, archive)):
        for file_name in sorted(files):
            path = os.path.join(directory, file_name)
            if path == mainfile or not file_name.lower().endswith(('.yaml', '.yml')):
                continue
            try:
                with open(path, encoding='utf-8') as f:
                    if is_process_library(yaml.safe_load(f)):
                        candidates.append(path)
            except Exception:
                continue
    if not candidates:
        raise ValueError(
            'No process library (a YAML file with cell_types and components) found in the upload. '
            'Upload it together with the batch note.'
        )
    if reference:
        same_name = [
            p for p in candidates if os.path.basename(p).lower() == os.path.basename(reference).lower()
        ]
        candidates = same_name + [p for p in candidates if p not in same_name]
    if len(candidates) > 1 and logger:
        logger.warning('several process libraries in the upload', used=candidates[0], found=candidates)
    return candidates[0]


def load_batch_note_snapshot(mainfile, archive, note, logger=None):
    """The snapshot for a batch note mainfile, with the files it came from as provenance."""
    library_path = find_process_library(mainfile, archive, note, logger)
    with open(library_path, 'rb') as f:
        library_bytes = f.read()
    library = yaml.safe_load(library_bytes)
    root = upload_raw_root(mainfile, archive)
    provenance = {
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'generator': 'nomad-hysprint batch note conversion',
        'source_note': os.path.relpath(mainfile, root),
        'library': os.path.relpath(library_path, root),
        'library_sha256': hashlib.sha256(library_bytes).hexdigest(),
    }
    for key, value in (('source_note_format', note.get('format')), ('library_format', library.get('format'))):
        if value:
            provenance[key] = str(value)
    return batch_note_to_snapshot(note, library, provenance, logger)
