"""Minimal NOMAD API helpers needed by the JV viewer."""

import requests


def _post_archive_query(url, token, query):
    response = requests.post(
        f'{url}/entries/archive/query',
        headers={'Authorization': f'Bearer {token}'},
        json=query,
    )
    response.raise_for_status()
    return response.json()['data']


def _post_entries_query(url, token, query):
    response = requests.post(
        f'{url}/entries/query',
        headers={'Authorization': f'Bearer {token}'},
        json=query,
    )
    response.raise_for_status()
    return response.json()['data']


def verify_token(url, token, timeout=10):
    """Return the user info dict for the given token, or raise."""
    response = requests.get(
        f'{url}/users/me',
        headers={'Authorization': f'Bearer {token}'},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def get_batch_ids(url, token, batch_type='HySprint_Batch'):
    """List all batch lab_ids visible to the user."""
    data = _post_archive_query(
        url,
        token,
        {
            'required': {'data': '*'},
            'owner': 'visible',
            'query': {'entry_type': batch_type},
            'pagination': {'page_size': 10000},
        },
    )
    return [d['archive']['data']['lab_id'] for d in data if 'lab_id' in d['archive']['data']]


def get_ids_in_batch(url, token, batch_ids, batch_type='HySprint_Batch'):
    """Given a list of batch lab_ids, return all sample lab_ids contained in them."""
    data = _post_archive_query(
        url,
        token,
        {
            'required': {'data': '*'},
            'owner': 'visible',
            'query': {'results.eln.lab_ids:any': batch_ids, 'entry_type': batch_type},
            'pagination': {'page_size': 1000},
        },
    )
    sample_ids = []
    for d in data:
        dd = d['archive']['data']
        if 'entities' in dd:
            sample_ids.extend([s['lab_id'] for s in dd['entities']])
    return sample_ids


def get_sample_description(url, token, sample_ids):
    """Return {lab_id: description} for every sample that has a non-empty description."""
    entries = _post_entries_query(
        url,
        token,
        {
            'required': {'data': '*'},
            'owner': 'visible',
            'query': {'results.eln.lab_ids:any': sample_ids},
            'pagination': {'page_size': 10000},
        },
    )
    res = {}
    for entry in entries:
        data = entry.get('data') or {}
        desc = data.get('description')
        if desc and desc.strip():
            res[data['lab_id']] = desc
    return res


def get_all_jv(url, token, sample_ids, jv_type='HySprint_JVmeasurement'):
    """Return {lab_id: [jv_archive_data, ...]} for the given samples."""
    entries = _post_entries_query(
        url,
        token,
        {
            'required': {'metadata': '*'},
            'owner': 'visible',
            'query': {'results.eln.lab_ids:any': sample_ids},
            'pagination': {'page_size': 10000},
        },
    )
    entry_ids = [e['entry_id'] for e in entries]
    if not entry_ids:
        return {}

    linked = _post_archive_query(
        url,
        token,
        {
            'required': {'data': '*', 'metadata': '*'},
            'owner': 'visible',
            'query': {
                'entry_references.target_entry_id:any': entry_ids,
                'entry_type': jv_type,
            },
            'pagination': {'page_size': 10000},
        },
    )
    res = {}
    for ldata in linked:
        d = ldata['archive']['data']
        if not d.get('samples'):
            continue
        lab_id = d['samples'][0]['lab_id']
        res.setdefault(lab_id, []).append(d)
    return res
