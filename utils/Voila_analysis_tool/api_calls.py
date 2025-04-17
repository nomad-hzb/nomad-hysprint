# --file contents--
# mthods to access the nomad api

import requests
import getpass

def init_cache():
    import requests_cache
    requests_cache.install_cache("my_local_cache", allowable_methods=('GET', 'POST'), ignored_parameters=['Authorization'])

#retreive information about all uploads of current user
def get_all_uploads(url, token, number_of_uploads=20):
    response = requests.get(f'{url}/uploads',
                             headers={'Authorization': f'Bearer {token}'},params=dict(page_size=number_of_uploads,order_by='upload_create_time', order="desc"))
    response.raise_for_status()
    return response.json()["data"]


def get_template(url, token, upload_name, method):
    query = {
        'required': {
            'data': '*',
        },
        'owner': 'visible',
        'query': {"upload_name": upload_name, "entry_type":method},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    return response.json()["data"]

def get_token(url, name=None):
    user = name if name is not None else input("Username")
    print("Passwort: \n")
    password = getpass.getpass()
    
    # Get a token from the api, login
    response = requests.get(
        f'{url}/auth/token', params=dict(username=user, password=password))  
    response.raise_for_status()  
    return response.json()['access_token']

def get_batch_ids(url, token, batch_type="HySprint_Batch"):
    query = {
        'required': {
            'data': '*'
        },
        'owner': 'visible',
        'query': {'entry_type':batch_type},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/archive/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    data = response.json()["data"]
    return [d["archive"]["data"]["lab_id"] for d in data if "lab_id" in d["archive"]["data"]]

def get_ids_in_batch(url, token,batch_ids, batch_type="HySprint_Batch"):
    query = {
        'required': {
            'data': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': batch_ids, 'entry_type':batch_type},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(
        f'{url}/entries/archive/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    data = response.json()["data"]
    assert len(data) == len(batch_ids)
    sample_ids = []
    for d in data:
        dd = d["archive"]["data"]
        if "entities" in dd:
            sample_ids.extend([s["lab_id"] for s in dd["entities"]])
    return sample_ids

def get_entry_data(url, token, entry_id):

    row = {"entry_id": entry_id}
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    assert len(response.json()["data"]) ==1, "Entry not found"
    return response.json()["data"][0]["archive"]["data"]

def get_sample_description(url, token, sample_ids):
    query = {
        'required': {
            'data': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    entries = response.json()["data"]
    res = {}
    for entry in entries:
        data = entry["data"]
        if "description" in data and  data["description"] and data["description"].strip():
            res.update({data["lab_id"]:data["description"]})
    return res
        

def get_entryid(url, token, sample_id):  # give it a batch id
    # get al entries related to this batch id
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids': sample_id},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    data = response.json()["data"]
    assert len(data) == 1
    return data[0]["entry_id"]

def get_nomad_ids_of_entry(url, token, sample_id):  # give it a batch id
    # get al entries related to this batch id
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids': sample_id},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    data = response.json()["data"]
    assert len(data) == 1
    return data[0]["entry_id"], data[0]["upload_id"]

def get_entry_meta_data(url, token, entry_id):

    row = {"entry_id": entry_id}
    query = {
        'required': {
            'metadata': '*',
        },
        'owner': 'visible',
        'query': row,
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(f'{url}/entries/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    assert len(response.json()["data"]) ==1, "Entry not found"
    return response.json()["data"][0]



def get_information(url, token, entry_id, path):
    mdata = get_entry_meta_data(url, token, entry_id)
    res = []
    for ref in mdata.get("entry_references"):
        if path != ref.get("source_path"):
            continue
        res.append(get_entry_data(url, token, ref.get("target_entry_id")))
        
    return res


def get_setup(url, token, entry_id):
    data = get_information(url, token, entry_id, "data.setup")
    assert data and len(data) == 1, "No Setup found"
    return data[0]

def get_environment(url, token, entry_id):
    data = get_information(url, token, entry_id, "data.environment")
    assert data and len(data) == 1, "No Environment found"
    return data[0]
    
def get_samples(url, token, entry_id):
    data = get_information(url, token, entry_id, "data.samples.reference")
    assert data and len(data) > 0, "No Samples found"
    return data



def get_specific_data_of_sample(url, token, sample_id, entry_type, with_meta=False):
    # collect the results of the sample, in this case it are all the annealing temperatures
    entry_id = get_entryid(url, token, sample_id)
    
    query = {
        'required': {
            'metadata': '*',
            'data': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id': entry_id},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = []
    for ldata in linked_data:
        if "entry_type" not in ldata["archive"]["metadata"] or entry_type not in ldata["archive"]["metadata"]["entry_type"]:
            continue
        if with_meta:
            res.append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
        else:
            res.append(ldata["archive"]["data"])
    return res

def get_all_JV(url, token, sample_ids, jv_type="HySprint_JVmeasurement"):
    # collect the results of the sample, in this case it are all the annealing temperatures
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
            'metadata': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'entry_type':jv_type},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = {}
    for ldata in linked_data:
        lab_id = ldata["archive"]["data"]["samples"][0]["lab_id"]
        if lab_id not in res:
            res[lab_id] = []
        res[lab_id].append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
    return res

def get_all_measurements_except_JV(url, token, sample_ids):
    # collect the results of the sample, in this case it are all the annealing temperatures
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
            'metadata': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'section_defs.definition_qualified_name': 'baseclasses.BaseMeasurement'},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = {}
    for ldata in linked_data:
        if "entry_type" not in ldata["archive"]["metadata"] or "JV" in ldata["archive"]["metadata"]["entry_type"]:
            continue
        lab_id = ldata["archive"]["data"]["samples"][0]["lab_id"]
        if lab_id not in res:
            res[lab_id] = []
        res[lab_id].append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
    return res

def get_all_measurements_except_JV(url, token, sample_ids):
    # collect the results of the sample, in this case it are all the annealing temperatures
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
            'metadata': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'section_defs.definition_qualified_name': 'baseclasses.BaseMeasurement'},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = {}
    for ldata in linked_data:
        if "entry_type" not in ldata["archive"]["metadata"] or "JV" in ldata["archive"]["metadata"]["entry_type"]:
            continue
        lab_id = ldata["archive"]["data"]["samples"][0]["lab_id"]
        if lab_id not in res:
            res[lab_id] = []
        res[lab_id].append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
    return res

def get_all_eqe(url, token, sample_ids, eqe_type="HySprint_EQEmeasurement"):
    #
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
            'metadata': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'entry_type':eqe_type},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = {}
    for ldata in linked_data:
        lab_id = ldata["archive"]["data"]["samples"][0]["lab_id"]
        if lab_id not in res:
            res[lab_id] = []
        res[lab_id].append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
    return res

def get_all_mppt(url, token, sample_ids, mppt_type="HySprint_SimpleMPPTracking"):
    #
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
            'metadata': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'entry_type':mppt_type},
        'pagination': {
            'page_size': 100
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    linked_data = response.json()["data"]
    res = {}
    for ldata in linked_data:
        lab_id = ldata["archive"]["data"]["samples"][0]["lab_id"]
        if lab_id not in res:
            res[lab_id] = []
        res[lab_id].append((ldata["archive"]["data"],ldata["archive"]["metadata"]))
    return res

def get_processing_steps(url, token, sample_ids, process_type="baseclasses.BaseProcess"):
    # collect the entry ids of the samples
    query = {
        'required': {
            'metadata': '*'
        },
        'owner': 'visible',
        'query': {'results.eln.lab_ids:any': sample_ids},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(
        f'{url}/entries/query', headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    
    entry_ids = [entry["entry_id"] for entry in response.json()["data"]]
    
    query = {
        'required': {
            'data': '*',
        },
        'owner': 'visible',
        'query': {'entry_references.target_entry_id:any': entry_ids,
                 'section_defs.definition_qualified_name': process_type},
        'pagination': {
            'page_size': 10000
        }
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    data = list(map(lambda process : process["archive"]["data"], response.json()["data"]))
    # delete entries for which "position_in_experimental_plan" is not defined, these are likely not proper processing steps
    data = [step for step in data if "positon_in_experimental_plan" in step]
    data.sort(key=lambda process : process["positon_in_experimental_plan"])
    return data

def get_efficiencies(url, token, sample_ids):
    query = {
        "required": {"results":{"properties":{"optoelectronic":{"solar_cell":{"efficiency":"*"}}}, "eln":{"lab_ids":"*"}}},
        'query': {'results.eln.lab_ids:any': sample_ids, "results.properties.optoelectronic.solar_cell.efficiency:gt":"0"},
        'owner': 'visible'
    }
    response = requests.post(f'{url}/entries/archive/query',
                             headers={'Authorization': f'Bearer {token}'}, json=query)
    response.raise_for_status()
    #return dict with entries lab_id:efficiency
    return dict(map(lambda x:(x["archive"]["results"]["eln"]["lab_ids"][0],
                              x["archive"]["results"]["properties"]["optoelectronic"]["solar_cell"]["efficiency"]),
                    response.json()["data"]
                   ))