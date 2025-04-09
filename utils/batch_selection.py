# --File contents--
#code for creating the batch selection widgets used in all three applications

import ipywidgets as widgets
from api_calls import get_batch_ids

# Function to handle search button click, filters the options based on search_field value
def on_search_enter(search, batch_selector, batch_ids_list):
    batch_selector.options = [d for d in batch_ids_list if search.value.strip().lower() in d]

def create_batch_selection(url, token, load_data_function):
    #give batch ids for visible batches of type "HySprint_Batch"
    batch_ids_list_tmp = list(get_batch_ids(url, token))
    batch_ids_list = []
    for b in batch_ids_list_tmp:
        if "_".join(b.split("_")[:-1]) in batch_ids_list_tmp: #skip id if the same name without the last word is also in the list
            continue
        batch_ids_list.append(b)
    batch_ids_selector = widgets.SelectMultiple(options=batch_ids_list,description='Batches',  layout=widgets.Layout(width='400px', height='300px'))
    
    search_field = widgets.Text(description="Search Batch")
    # Bind the 'Search' event
    search_field.observe(lambda b : on_search_enter(search_field, batch_ids_selector, batch_ids_list))

    status_output=widgets.Output()
    
    load_batch_button=widgets.Button(description="Load Data", button_style='primary')
    load_batch_button.on_click(lambda b:load_data_function(batch_ids_selector))
    
    return widgets.VBox([search_field, batch_ids_selector, load_batch_button])