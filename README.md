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

## DATA_PROCESSING
This folder contains python scripts that process raw data into processed data.  In general, the raw data area data files provided by NYCEM or downloaded from public web sites. The processing includes projection, null-data handling, resampling to census tracts, and converstion of consequences to estimated losses.

Naming convention: The first three letters of each script refernce the relevant subcomponent (ESL, SOV, or RCA).  For scripts used to calcualte ESL, the next three letters indicate the relevant hazard (see list above).  For scripts used to calculate RCA, the next two letters indicate the relevant sub-component of RCA (CC - Community Capital, ML- Mitigation Landscape, RC - Response Capacity, RR - Recovery Resources).  The last two or three letters abbreviate the relevant resilience factor.  

