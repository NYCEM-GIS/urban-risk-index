# NYCEM_URI
These scripts perform the calculations for the New York City Emergency Management (NYCEM) Urban Risk Index (URI) project. The URI scores the relative risk in each NYC census tract for 6 different hazards:  
- Coastal erosion (CER)
- Coastal storm flooding (CSF)
- Coastal storm winds (CSW)
- Earthquake (ERQ)
- Extreme heat (EXH)
- Winter weather (WIW)

The URI score for each hazard takes into account three factors:  hazard impacts (based on estimated annualized loss (ESL)), social vulnerability (SOV), and resilience capacity (RCA).  The repository contents are described below.  Note this repository is under development.  Code and comments are regularly modified and added.

## DATA_DOWNLOAD
Contains scripts that are used to generate raw inputs which are then in turn used in scripts in the PRE_PROCESSING folder.

## PRE_PROCESSING
Contains scripts that process raw data into tract-level inputs to the URI model.  The raw data inputs are stored outside of the repository in ../1_RAW_INPUTS. In general, the raw data files were provided by NYCEM or downloaded from public web sites. The processing includes projection, null-data handling, resampling to census tracts, and conversion of consequences to estimated losses.  The outputs produced by the script are saved in ../2_PROCESSED_INPUTS.

Naming convention: The first three letters of each script reference the relevant URI component (ESL, SOV, or RCA).  For scripts used to calculate ESL, the next three letters indicate the relevant hazard (see list above).  For scripts used to calculate RCA, the next two letters indicate the relevant subcomponent of RCA (CC - Community Capital, ML- Mitigation Landscape, RC - Response Capacity, RR - Recovery Resources).  The last two or three letters abbreviate the relevant resilience factor, which is described in the methods document.  

## MODEL 
Contains scripts that takes tract-level outputs from the PRE_PROCESSING folder (stored in the 2_PROCESSED_INPUTS directory), generates the relevant components of the URI, and stores results in the 3_OUTPUTS folder.

## POST_PROCESSING
Contains scripts used to combine URI outputs into a single file and export to a geodatabase with aliases and domains for use in the ESRI dashboard.

## PARAMS
Contains non-geospatial variables used through the URI, such as paths to relevant raw input files, hard-coded parameters, settings, and other parameters that drive URI calculations (such as the value of a statistical life or the average duration of displacement). 

## UTILITY
Miscellaneous scripts used throughout all stages of the URI, such as plotting and projecting 
