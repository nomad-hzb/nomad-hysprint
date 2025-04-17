import ipywidgets as widgets
from IPython.display import display, Markdown, HTML

#define functions to get names
def sample_and_curve_name (sample_name, curve_name):
    return sample_name + " " + curve_name
def only_sample_name (sample_name, curve_name):
    return sample_name
def only_curve_name (sample_name, curve_name):
    return curve_name

#class for size and name widgets.
class plot_options(widgets.widget_box.VBox):
    def __init__(self, default_name=0):
        self.width = widgets.BoundedIntText(
            value=1200,
            min=100,
            max=2000,
            step=1,
            description='width in px:')

        self.height = widgets.BoundedIntText(
            value=500,
            min=100,
            max=2000,
            step=1,
            description='height in px:')
        
        self.name = widgets.ToggleButtons(options=[("sample + curve name",sample_and_curve_name), 
                                                   ("only sample name",only_sample_name), 
                                                   ("only individual name",only_curve_name)], 
                                          index=default_name,
                                          description="select how the datasets will be named")
        super().__init__([self.name, self.width, self.height])

#function to create a manual display area
def create_manual(filename):
    toggle_manual = widgets.ToggleButton(description="Manual")
    manual_out = widgets.Output()
    def update_manual(change):
        manual_out.clear_output()
        if change["new"]:
            with manual_out, open(filename, "r", encoding="utf-8") as file:
                display(Markdown(file.read()))
    toggle_manual.observe(update_manual, names="value")
    return widgets.VBox([toggle_manual, manual_out])