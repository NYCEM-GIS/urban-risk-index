# NYCEM_URI
These scripts perform the calculations for the New York City Emergency Management (NYCEM) Urban Risk Index (URI) project. The URI scores the relative risk in each NYC census tract for 11 different hazards:  
- Coastal erosion (CER)
- Chemical, biological, radiation, and nuclear threats (CBRN)
- Coastal storms (CST)
- Cyber threats (CYB)
- Emerging diseases epidemic (EMG)
- Earthquake (ERQ)
- Extreme heat (EXH)
- Flooding (FLD)
- High winds (HIW)
- Respiratory disease pandemic (RES)
- Winter weather (WIW)
The URI score for each hazard take into account three factors:  estimated annualized loss (ESL), social vulnerability (SOV), and resilience capacity (RCA).  The repository contents are described below.  


## CALCS
This folder is not currently used.

## CLASSES
This folder contains the class_EL_SV_CR python script that defines the object constructor for the EL, SV, CR, and URI objects.  The python notebooks use the EL, SV, CR, and URI objects to store data about each subcomponent for each hazard, to perform simple operations on that data such as plot.

## DATA_PROCESSING
This folder contains python scripts that process raw data into processed data.  The raw data inputs are stored outside of the repository in ../1_RAW_INPUTS.  In general, the raw data files were provided by NYCEM or downloaded from public web sites. The processing includes projection, null-data handling, resampling to census tracts, and converstion of consequences to estimated losses.  The outputs produced by the script are saved in ../2_PROCESSED_INPUTS.

Naming convention: The first three letters of each script reference the relevant URI subcomponent (ESL, SOV, or RCA).  For scripts used to calcualte ESL, the next three letters indicate the relevant hazard (see list above).  For scripts used to calculate RCA, the next two letters indicate the relevant subsubcomponent of RCA (CC - Community Capital, ML- Mitigation Landscape, RC - Response Capacity, RR - Recovery Resources).  The last two or three letters abbreviate the relevant resilience factor, which is described in the methods document.  

## MISC
This folder contains miscellaneous scripts used in the URI calculation.  Here is a brief description the each:
- utils_1.py: defines utility functions that are used by the scripts in the DATA_PROCESSING folder.  The utility perform commonly-needed functions such as loading and projecting the ensus tract shapefile, putting an input into the correct projection, or performing a dasymetric transformation between tract, neighborhood, and community levels.  
- params_1.py: loads the parameters for the URI calculation from an excel spreadsheet.  The spreadsheet is saved outside the repository in ../5_PARAMES/.
- folder_setup_1.py: creates the folder structure to store outputs from the URI calculation.
- plotting_1.py: creates plots and maps of the URI calculation results.
- read_nri_1.py: reads and plots data downloaded from the National Risk Index (NRI) for comparative anaysis.  This data was not used in the NRI calculation.

## NOTEBOOKS
This folder contains jupyter notebooks that perform the URI calculations for specific hazards.  The hazard acronym is in the notebook title.  

For more infommation, contact Dano Wilusz at dwilusz@dewberry.com.



