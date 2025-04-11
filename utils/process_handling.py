# --file contents--
# classes and methods for handling, grouping and visualizing data about manufacturing steps 

import numpy as np
import json
import ipywidgets as widgets
import pandas as pd
import itertools
from IPython.display import display, HTML

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return str(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

#class to hold data about production steps and samples in a batch and provide visualization
class batch_process(widgets.GridBox):
    #constructur arguments:
    #process_list: list of process entries related to the samples in the relevant batch
    #efficiencies: dict containg key value pairs lab_id:efficiency
    #batch_name: name of the batch unused, was intended to be shown in the gui
    #detail_widget: should be an output widget, will be used to display tables with manufacturing parameters
    #parameter_widget: output widget used for the overview of selected parameters
    #exclude_constants, exclude_strings, abbreviate_keys: objects with a boolean .value attribute, selects which parameters are shown in the table 
    def __init__(self, 
                 process_list, 
                 efficiencies,
                 batch_name, 
                 detail_widget, 
                 parameter_widget,
                 exclude_constants, exclude_strings, abbreviate_keys):
        self.name=batch_name
        self.detail_widget=detail_widget
        self.parameter_widget=parameter_widget
        self.efficiencies = efficiencies
        
        self.exclude_constants=exclude_constants
        self.exclude_strings=exclude_strings
        self.abbreviate_keys=abbreviate_keys
        
        #procedure relies on steps being ordered by "position_in_experimental_plan"
        #result should be a list where the n-th entry is a list of all processes that were performed n-th in the production 
        steps = []
        plan_position_offset =process_list[0]["positon_in_experimental_plan"] #the number indicating the first manufacturing step, might be 0 or 1
        
        for step in process_list:
            if step["positon_in_experimental_plan"]-plan_position_offset >= len(steps):
                steps.append([step])
            else:
                steps[-1].append(step)
        
        self.steps=steps
        self.steps_merged=list(map(lambda x: merge_step_data(x),steps))
        
        #create overview widgets
        def create_step_description(i):
            if len(self.steps[i]) == 1:
                label=widgets.Label(value=f"{int(self.steps[i][0]['positon_in_experimental_plan'])} {self.steps[i][0]['name']}")
            elif len(self.steps_merged[i]) == 1:
                label=widgets.Label(value=f"{int(self.steps[i][0]['positon_in_experimental_plan'])} {self.steps[i][0]['name']}, {len(self.steps[i])} variations", style={"text_color":"blue"})
            else:
                label=widgets.Label(value= f"{int(self.steps[i][0]['positon_in_experimental_plan'])} {len(self.steps_merged[i])} different step types", style={"text_color":"red"})
            
            button=widgets.Button(description="details", layout={"width":"100px"})
            button.on_click(lambda b : self.show_process_details(i))
            
            return [label, button]
        super().__init__(list(itertools.chain.from_iterable(map(create_step_description, range(len(self.steps))))), layout=widgets.Layout(grid_template_columns="3fr 1fr", border="1px solid black"))
        
        #create the parameter selection widgets
        def param_selection_buttons(step_index):
            sample_ids_nested = self.samples_for_processes_in_step(step_index)
            return list(map(lambda process : list(map(lambda jsonpath_values_tuple: manufacturing_parameter(jsonpath_values_tuple[0],
                                                                                                            list(map(lambda idx:sample_ids_nested[idx], process["indices"])),
                                                                                                            jsonpath_values_tuple[1],
                                                                                                            self.refresh_selected_parameter_overview
                                                                                                           ),
                                                      flatten_layers(process["json"],[],False,False)
                                                     )),
                            self.steps_merged[step_index]
                           ))
        self.manufacturing_params = list(map(param_selection_buttons, range(len(self.steps_merged))))
    
    def show_process_details(self, step_index):
        self.detail_widget.clear_output()
        sample_lists = self.samples_for_processes_in_step(step_index)
        with self.detail_widget:
            for process_idx, process in enumerate(self.steps_merged[step_index]):
                display(HTML(make_table(process, 
                                        sample_lists,
                                        remove_constants=self.exclude_constants.value, 
                                        remove_string=self.exclude_strings.value, 
                                        abbreviate_keys=self.abbreviate_keys.value).to_html()))
                display(widgets.GridBox(self.manufacturing_params[step_index][process_idx], layout=widgets.Layout(grid_template_columns="repeat(10, 1fr)")))

    def samples_for_processes_in_step(self, step_index):
        return list(map(lambda process : list(map(lambda sample:sample.get("lab_id", "id not found"), process["samples"])), self.steps[step_index]))
        
    def refresh_selected_parameter_overview(self, triggering_button):
        with self.parameter_widget:
            self.parameter_widget.clear_output()
            display(widgets.GridBox(list(filter(lambda button: button.value,
                                                itertools.chain.from_iterable(itertools.chain.from_iterable(self.manufacturing_params))
                                               )),
                                    layout=widgets.Layout(grid_template_columns="repeat(10, 1fr)", border="1px solid black")
                                   ))
            
    def get_selected_manufacturing_parameters(self, only_samples_with_efficiencies=True, only_samples_with_all_values=True):
        datapoints_dict = {}
        parameter_name_list=[]
        for parameter_object in filter(lambda x:x.value, itertools.chain.from_iterable(itertools.chain.from_iterable(self.manufacturing_params))):
            parameter_name_list.append(str(parameter_object.keychain[-1]))
            for sample_id in filter(lambda x:bool(x in self.efficiencies or not only_samples_with_efficiencies),parameter_object.samples_values_dict):
                if sample_id not in datapoints_dict:
                    datapoints_dict[sample_id]={}
                datapoints_dict[sample_id][str(parameter_object.keychain[-1])] = parameter_object.samples_values_dict[sample_id]
        if only_samples_with_all_values:
            filtered_dict={}
            for sample_id in datapoints_dict:
                if list(datapoints_dict[sample_id].keys()) == parameter_name_list:
                    filtered_dict[sample_id]=datapoints_dict[sample_id]
            return filtered_dict
        else:
            return datapoints_dict
            

class manufacturing_parameter(widgets.ToggleButton):
    #sample_ids should be a list of lists where the ith list contains all sample ids for which the ith value was used
    def __init__(self, keychain, sample_ids_nested, values, update_callback):
        super().__init__(description=str(keychain[-1]))
        self.keychain=keychain
        self.value=False
        self.samples_values_dict = dict(itertools.chain.from_iterable(map(lambda idx:
                                                                          map(lambda sample_id: (sample_id, values[idx]),
                                                                              sample_ids_nested[idx]), 
                                                                          range(len(sample_ids_nested)))))
        self.observe(update_callback)

def merge_step_data(initial_process_list, exclude_non_numeric=False, blacklist = []):
    ignored_keys = ["samples", "positon_in_experimental_plan"]+blacklist
    process_list = [{key: unfiltered_process[key] for key in set(unfiltered_process) - set(ignored_keys)} for unfiltered_process in initial_process_list]
    return merge_process(process_list, exclude_non_numeric, 0)

def merge_process(process_list, exclude_non_numeric, recursion_depth):
    #object may be list of lists, a list of dicts (such as on top recursion level) or a list of str/float/int (final recursion layer)
    assert all(map(lambda x: bool(type(x)==type(process_list[0])), process_list)) #raise assertion error if not all processes have the same datatype
    if isinstance(process_list[0], dict) or isinstance(process_list[0], list):
        return_list = []
        is_list = isinstance(process_list[0], list)
        
        if is_list:
            all_key_structures = np.array(list(map(lambda x:list(range(len(x))), process_list)))
            key_structures, process_to_structure = np.unique(all_key_structures, return_inverse=True, axis=0)
        else:
            all_key_structures = np.array(list(map(lambda x:x.keys(), process_list)))
            key_structures, process_to_structure = np.unique(all_key_structures, return_inverse=True)
        
        for keyset_index, keyset in enumerate(key_structures):
            process_indices = np.nonzero(process_to_structure == keyset_index)[0]
            
            #central recursion on the data                
            key_results = dict(filter(lambda keyresulttuple : all(map(lambda data: len(data["json"]), keyresulttuple[1])), #drop keys for which there is no data
                                      map(lambda key: (key,
                                                       merge_process(list(map(lambda x:x[key], np.array(process_list)[process_indices])), #operate on the entries behind KEY for every process
                                                                     exclude_non_numeric, recursion_depth+1) #additional arguments for merge_process()
                                                      ),
                                          keyset)
                                     ))
            
            if not key_results:
                return_list = [{"indices":np.arange(len(process_list)), "json":[] if is_list else {}}]
                break

            #array works like substructure_map[key for subdata][j] = idx such that key_results[key][idx] gives the data corresponding to process_indices[j]
            substructure_map = np.array(list(map(lambda key: 
                                                 list(map(lambda i: 
                                                          np.argmax(list(map(lambda x: i in x["indices"], key_results[key]))),
                                                          range(len(process_indices))
                                                         )),
                                                 key_results)))
            
            # get unique combinations of datastructures, processes will be split as long as the structure differs for any key
            structure_combinations, process_to_combination = np.unique(substructure_map, axis=1, return_inverse=True)               
            if is_list:
                for unique_structure_index, unique_structure in enumerate(structure_combinations.T):
                    indices_for_current_struc = np.nonzero(process_to_combination == unique_structure_index)[0]
                    return_list.append({"indices":process_indices[indices_for_current_struc], 
                                        "json":list(map(lambda key : key_results[key][substructure_map[key][indices_for_current_struc[0]]]["json"],
                                                        key_results))})
            else:
                for unique_structure_index, unique_structure in enumerate(structure_combinations.T):                    
                    indices_for_current_struc = np.nonzero(process_to_combination == unique_structure_index)[0]
                    return_list.append({"indices":process_indices[indices_for_current_struc], 
                                        "json":dict(map(lambda i : (list(key_results)[i], key_results[list(key_results)[i]][substructure_map[i][indices_for_current_struc[0]]]["json"]),
                                                        range(len(key_results))))})
    else: #type is either string, float or some other non-nested-value
        if isinstance(process_list[0], str) and exclude_non_numeric:
            return_list = [{"indices":np.arange(len(process_list)), "json":{}}]
        else:
            return_list = [{"indices":np.arange(len(process_list)), "json":np.array(process_list)}]
    return return_list

def make_table(process, index_map, remove_constants=False, remove_string=False, abbreviate_keys=False):
    column_data = flatten_layers(process["json"],[], remove_constants, remove_string)
    if abbreviate_keys:
        return pd.DataFrame(dict(map(lambda x:(str(x[0][-1]),x[1]), column_data)), 
                            index=list(map(lambda idx:str(index_map[idx]), process["indices"])))
    else:
        return pd.DataFrame(dict(map(lambda x:(str(x[0]),x[1]), column_data)),
                            index=list(map(lambda idx:str(index_map[idx]), process["indices"])))

def flatten_layers(data, keychain, remove_constants, remove_string):
    if isinstance(data, np.ndarray):
        if remove_string and any(map(lambda x: isinstance(x, str), data)):
            return []
        elif remove_constants and all(data == data[0]):
            return []
        else:
            return [(keychain, data)]
    elif isinstance(data,list):
        return list(itertools.chain.from_iterable(map(lambda idx_entry : flatten_layers(idx_entry[1], keychain+[str(idx_entry[0])], remove_constants, remove_string), enumerate(data))))
    elif isinstance(data,dict):
        return list(itertools.chain.from_iterable(map(lambda key : flatten_layers(data[key], keychain + [key], remove_constants, remove_string), data)))