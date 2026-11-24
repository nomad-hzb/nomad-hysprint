#!/usr/bin/env python3
"""Write the allowed field names per process type into the process snapshot contract.

The field names a snapshot may use are the ones of the Excel experiment file:

* every column the Excel template offers (utils/excel_creator, with all
  options switched on), and
* every column NOMAD's mapping code reads for that process type
  (baseclasses.helper.solar_cell_batch_mapping and the ink recycling
  mappers), which includes columns real Excel files use but the template
  does not offer.

Numbered fields (Solvent 1 name, Solvent 2 name ...) become patterns, shown
as 'Solvent {n} name'.

Usage, from the nomad-hysprint directory:
    python utils/snapshot_contract/update_contract_fields.py          # update the contracts
    python utils/snapshot_contract/update_contract_fields.py --check  # exit 1 if out of date

It updates every contract version in src/nomad_hysprint/parsers/contracts/.
The lists are documentation (x-known-field-names): other names are accepted,
reported as unread_parameters and not stored. Run it after changing the
Excel template or the mappers.
"""

import ast
import importlib
import inspect
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CONTRACT_DIR = os.path.join(REPO, 'src', 'nomad_hysprint', 'parsers', 'contracts')
EXCEL_CREATOR = os.path.join(REPO, 'utils', 'excel_creator')

MAPPER_MODULES = [
    'baseclasses.helper.solar_cell_batch_mapping',
    'nomad_hysprint.parsers.file_parser.ink_recycling_mappers',
]
EXPERIMENT_INFO = 'Experiment Info'
# process type (contract 'method') -> mapper function(s) the parser calls for it
MAPPERS = {
    'Cleaning': ['map_cleaning'],
    'Cleaning UV-Ozone': ['map_cleaning'],
    'Cleaning O2-Plasma': ['map_cleaning'],
    'Spin Coating': ['map_spin_coating'],
    'Slot Die Coating': ['map_sdc'],
    'Blade Coating': ['map_blade_coating'],
    'Inkjet Printing': ['map_inkjet_printing'],
    'Screen Printing': ['map_screen_printing'],
    'Evaporation': ['map_evaporation'],
    'Co-Evaporation': ['map_evaporation'],
    'Seq-Evaporation': ['map_evaporation'],
    'Sputtering': ['map_sputtering'],
    'ALD': ['map_atomic_layer_deposition'],
    'Annealing': ['map_annealing_class'],
    'Laser Scribing': ['map_laser_scribing'],
    'Ink Recycling': ['map_ink_recycling'],
    'Generic Process': ['map_generic'],
    EXPERIMENT_INFO: ['map_basic_sample', 'map_substrate'],
}
# Generic processes store every parameter they get (map_generic_parameters).
FREE_FORM = {'Generic Process'}
# The experiment table skips these processes when 'Material name' is empty.
MATERIAL_NAME_REQUIRED = {
    'Evaporation',
    'Co-Evaporation',
    'Seq-Evaporation',
    'Spin Coating',
    'Slot Die Coating',
    'Blade Coating',
    'Inkjet Printing',
    'Screen Printing',
    'Sputtering',
    'ALD',
}
# Experiment Info columns the parser fills from the snapshot's structure.
PARSER_OWNED = {
    'Date',
    'Project_Name',
    'Batch',
    'Subbatch',
    'Sample',
    'Nomad ID',
    'Parent ID',
    'Variation',
    'Architecture',
}
READERS = {'get_value', 'get_bool_value', 'get_datetime'}
# map_solutions derives these prefixes from columns like 'Solvent 1 name'
PREFIX_VARIABLES = {'solvent': 'Solvent {n}', 'solute': 'Solute {n}', 'additive': 'Additive {n}'}
TEMPLATE_COUNTS = dict(solvents=3, solutes=3, materials=3, precursors=3)
TEMPLATE_SWITCHES = ['antisolvent', 'gasquenching', 'vacuumquenching', 'gavd']


def normalize(name):
    """'Rotation speed {n}[rpm]' -> 'Rotation speed {n} [rpm]'."""
    name = re.sub(r'\s*\{n\}\s*', ' {n} ', name).strip()
    return re.sub(r'\s+', ' ', name)


def to_pattern(name):
    """Regex for a numbered field. A number after a space may be left out, as the
    mappers also read the unnumbered form ('Rotation speed [rpm]')."""
    regex = re.escape(name).replace(re.escape(' {n}'), r'(?: \d+)?').replace(re.escape('{n}'), r'\d+')
    return f'^{regex}$'


def number_template_name(name):
    """'Solvent 2 name' -> 'Solvent {n} name' (numbers that count repeated fields)."""
    return re.sub(r'(?<=[A-Za-z] )\d+(?=( |$))', '{n}', name)


def template_fields(method):
    sys.path.insert(0, EXCEL_CREATOR)
    import openpyxl
    from sheet_experiment import add_experiment_sheet

    names = {}
    for spinsteps in (0, 1, 3):
        for switches in itertools.product((False, True), repeat=len(TEMPLATE_SWITCHES)):
            config = dict(TEMPLATE_COUNTS, spinsteps=spinsteps, **dict(zip(TEMPLATE_SWITCHES, switches)))
            sequence = [{'process': EXPERIMENT_INFO}]
            if method != EXPERIMENT_INFO:
                sequence.append({'process': method, 'config': config})
            workbook = openpyxl.Workbook()
            add_experiment_sheet(workbook, sequence, is_testing=True)
            sheet = workbook.active
            group = None
            for column in range(1, sheet.max_column + 1):
                group = sheet.cell(row=1, column=column).value or group
                name = sheet.cell(row=2, column=column).value
                if not name or (group == EXPERIMENT_INFO) != (method == EXPERIMENT_INFO):
                    continue
                if name == 'Undefined Process':  # the template does not know this process type
                    continue
                names[number_template_name(name)] = None
            if method == EXPERIMENT_INFO:
                return list(names)
    return list(names)


def mapper_functions():
    functions = {}
    for module_name in MAPPER_MODULES:
        tree = ast.parse(inspect.getsource(importlib.import_module(module_name)))
        functions.update({node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)})
    return functions


def mapper_fields(entry_points, functions):
    """Field names read by the given mapper functions and the helpers they call."""

    def render(node, env):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return [node.value]
        if isinstance(node, ast.List | ast.Tuple):
            return [name for element in node.elts for name in render(element, env) or []]
        if isinstance(node, ast.JoinedStr):
            text = ''
            for part in node.values:
                if isinstance(part, ast.Constant):
                    text += part.value
                else:
                    variable = ast.unparse(part.value)
                    text += env.get(variable, PREFIX_VARIABLES.get(variable, '{n}'))
            return [text]
        return None

    names, seen, unresolved = set(), set(), []

    def collect(function_name, env):
        key = (function_name, tuple(sorted(env.items())))
        if key in seen or function_name not in functions:
            return
        seen.add(key)
        for node in ast.walk(functions[function_name]):
            if isinstance(node, ast.Subscript) and ast.unparse(node.value) == 'data':
                names.update(render(node.slice, env) or [])
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            callee = func.id if isinstance(func, ast.Name) else getattr(func, 'attr', None)
            if callee == 'create_product_info' and len(node.args) > 1:
                for prefix in render(node.args[1], env) or ['{n}']:
                    collect('create_product_info', {'prefix': prefix})
            elif callee in READERS and len(node.args) > 1:
                rendered = render(node.args[1], env)
                if rendered is None:
                    unresolved.append(f'{function_name}: {ast.unparse(node.args[1])}')
                names.update(rendered or [])
            elif callee == 'get' and isinstance(func, ast.Attribute) and ast.unparse(func.value) == 'data':
                names.update(render(node.args[0], env) or [])
            elif callee in functions:
                collect(callee, {})

    for entry_point in entry_points:
        collect(entry_point, {})
    if unresolved:
        raise RuntimeError(f'Field names the generator cannot resolve: {unresolved}')
    return names


def slug(method):
    return 'parameters_' + re.sub(r'[^a-z0-9]+', '_', method.lower()).strip('_')


def field_list_schema(method, names):
    exact = sorted({n for n in names if '{n}' not in n})
    numbered = sorted({n for n in names if '{n}' in n})
    known = {'anyOf': [{'enum': exact}] + [{'title': n, 'pattern': to_pattern(n)} for n in numbered]}
    schema = {
        'description': (
            f'Field names for {method}: the Excel experiment file columns. '
            "Numbered fields are shown with {n}, e.g. 'Solvent {n} name' accepts 'Solvent 1 name'. "
            'Generated by utils/snapshot_contract/update_contract_fields.py, do not edit by hand. '
            'The names NOMAD reads are listed in x-known-field-names (documentation, not a rule): '
            'other names are accepted, reported as unread_parameters, and their values are not stored.'
        ),
        'type': 'object',
        'additionalProperties': {'$ref': '#/$defs/scalar'},
    }
    if method in MATERIAL_NAME_REQUIRED:
        schema['required'] = ['Material name']
    schema['x-known-field-names'] = known
    return schema


def field_names():
    """Field names per process type (and Experiment Info): template plus mappers."""
    functions = mapper_functions()
    result = {}
    for method, entry_points in MAPPERS.items():
        names = {normalize(n) for n in template_fields(method)}
        names |= {normalize(n) for n in mapper_fields(entry_points, functions)}
        if method == EXPERIMENT_INFO:
            names -= PARSER_OWNED
        result[method] = names
    return result


def generated_definitions(names_per_method):
    definitions = {}
    for method, names in names_per_method.items():
        if method in FREE_FORM:
            definitions[slug(method)] = {
                'description': (
                    f'{method}: any field name; every parameter is stored. '
                    'Generated by utils/snapshot_contract/update_contract_fields.py.'
                ),
                '$ref': '#/$defs/fieldValues',
            }
        else:
            definitions[slug(method)] = field_list_schema(method, names)
    return definitions


def contract_files():
    """{version: path} of all contract versions."""
    files = {}
    for file_name in sorted(os.listdir(CONTRACT_DIR)):
        match = re.match(r'^hzb-process-snapshot\.(v[\w.]+)\.schema\.json$', file_name)
        if match:
            files[match.group(1)] = os.path.join(CONTRACT_DIR, file_name)
    return files


def updated_contract(contract, names_per_method):
    contract = json.loads(json.dumps(contract))  # copy
    definitions = contract['$defs']
    for key in [k for k in definitions if k.startswith('parameters_')]:
        del definitions[key]
    definitions.update(generated_definitions(names_per_method))
    methods = [m for m in MAPPERS if m != EXPERIMENT_INFO]
    definitions['process']['properties']['method']['enum'] = methods
    definitions['process']['allOf'] = [
        {
            'if': {'properties': {'method': {'const': method}}, 'required': ['method']},
            'then': {'properties': {'parameters': {'$ref': f'#/$defs/{slug(method)}'}}},
        }
        for method in methods
    ]
    info = f'#/$defs/{slug(EXPERIMENT_INFO)}'
    contract['properties']['experiment']['properties']['properties']['$ref'] = info
    definitions['subBatch']['properties']['sample_properties']['$ref'] = info
    return contract


def dumps(contract):
    return json.dumps(contract, indent=2, ensure_ascii=False) + '\n'


def main():
    names_per_method = field_names()
    outdated = []
    for path in contract_files().values():
        with open(path, encoding='utf-8') as f:
            current = f.read()
        updated = dumps(updated_contract(json.loads(current), names_per_method))
        if updated == current:
            continue
        outdated.append(path)
        if '--check' not in sys.argv:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f'updated {os.path.relpath(path, REPO)}')
    if '--check' in sys.argv:
        if outdated:
            print(f'out of date: {outdated}; run {os.path.relpath(__file__, REPO)}')
            sys.exit(1)
        print('contract field names are up to date')


if __name__ == '__main__':
    main()
