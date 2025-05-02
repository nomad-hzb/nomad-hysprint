# How to use
## 1. Select the batches containing the data you want to analyze.
## 2. Dataset names
Enter names for the samples. These names will be part of the names used in the final plot. When creating an area or box plot curves with the same name will be grouped together.  
The available presets are:
* "sample name" use the lab id unless it contains a "&" character. In that case everything after the first "&" is used
* "batch" use the lab id with a suffix like "_something" removed
* "sample description" use the sample description from the NOMAD entry  

With "expand options" you can enter names for the individual curves of a sample. By default the individual names are two numbers, the first indicating the measurement entry and the second the curve within the measurement entry. The latter usually refers to which cell of the sample was being measured. The former is only relevant if multiple measurements exist for one sample.
You can select which curves will be considered in the plot with the checkboxes or the "show all/none" buttons

## 3 create plots
You can choose which of the names specified in the selection part will be used in the plot.  
When "group curves with same name" is selected all datasets with the same name will be displayed as a single area plot with a line representing the median or average and an area for the interquartile range or the 1σ interval.