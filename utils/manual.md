# Feature Overview
## EQE Plotting
* creating plots of eqe curves
* creating boxplots for parameters derived from eqe curves (such as the bandgap)
* create area plots for groups of eqe curves
## MPPT Plotting
* create plots of MPPT Measurements
* fit model functions to MPPT Curves
* create area plots for groups of MPPT Curves
## Manufacturing Parameters

# How to run the tools
You can either run the programm through the [NOMAD remote tools hub](https://nomad-hzb-se.de/nomad-oasis/gui/analyze/north/ "go to the website") or on your computer.  
For the Former (the simpler option) the code needs to be in a Nomad upload you have access to.  
For the Latter you need jupyter with voilà and the following python packages:  
* numpy
* pandas
* requests
* plotly
* lmfit
* ipywidgets