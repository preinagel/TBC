# Temporal Barcode Project Capsule
Started by Pamela Reingael, July 10, 2025, San Diego California

This repo constitutes a capsule for the Temporal Barcode project of the Allen Institute's OpenScope project. This project recorded extracellular potentials from neurons using Neuropixels probes, throughout the brains of awake mice during passive exposure to visual stimuli that were temporally modulated with broad-band white noise (either spatially uniform or spatially static).

This code is directly associated with the open dataset available here:

       https://dandiarchive.org/dandiset/000563/0.250311.2145

or here:

       https://doi.org/10.48324/dandi.000563/0.250311.2145

A demonstration notebook introducing the Temporal Barcode experiment and dataset can be found within the OpenScope Databook here:

       https://alleninstitute.github.io/openscope_databook/projects/barcoding.html

# Overview of this repository  
## The TBC Module
A set of Python packages containing utility functions developed for working with this dataset, some of which are quite specific to these data files or scientific questions, and others of which may be of broader utility.

### Packages
#### tbc_utils.py         
   dataset-specific utilities for extracting data from raw (NWB standard) data files, based on details of this experiment's design
#### raster_utils.py      
   general purpose functions for manipulating and analysis of spike rasters (spike times from multiple trials aligned to an event trigger)
#### tbc_computation.py   
   computational functions that operate on data to generate numerical results specifically relating to temporal barcode analysis
#### tbc_visualization.py 
   functions for conveniently visualizing output of computations (a direct companion of tbc_computation.py)
### Docs
Documentation of the above packages, automatically updated from docstrings using Sphinx
### Demos
A folder containing Jupyter notebooks that demonstrate how to use the functions in the other packages, or that demonstrate the validity of implementations and approximations in those functions, along with very small toy datasets used by those demos.


## TBC analysis
### Pilot analysis
Data analysis pipelines validated using pilot datasets *prior to viewing any production data file* (to render transparent which analysis decisions were data-independent vs. data-dependent with resect to the production dataset)
### Production analysis
Data analysis pipelines that go from the raw data files all the way to final numerical outputs and figures to be included in publications, including supplementary materials of those publications


