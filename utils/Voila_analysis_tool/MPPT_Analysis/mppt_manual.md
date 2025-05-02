# How to use
## 1. Select the batches containing the data you want to analyze.
## 2. Dataset Names
Enter names for the samples. These names will be part of the names used in the final plot. When creating an area or box plot curves with the same name will be grouped together.  
The available presets are:
* "sample name" use the lab id unless it contains a "&" character. In that case everything after the first "&" is used
* "batch" use the lab id with a suffix like "_something" removed
* "sample description" use the sample description from the NOMAD entry  

With "expand options" you can enter names for the individual curves of a sample. By default this is a number that simply enumerates all mppt measurements that exist for a single sample.

## 3. model fitting
The interval slider can be used to constrict the time interval that will be used for model fitting. You may use this to exclude an initial burn in period from the fitting process. Next select which fitting models should be used. If you want to implement your own models you can find a guide in the comments of third cell of this notebook and the fitting_tools.py file. Only the power density will be subjected to fitting, the voltage and current values are ignored.
## 4. create plots
You can choose which of the names specified in the selection part will be used in the plot.
You can also select which fitted function will be plotted in addition to the data. If you want to plot the voltage or current values "None" must be selected for the models.

For the 