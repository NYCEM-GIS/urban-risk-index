"""
Define class ESL that contains information about estimated loss.
Note the class does not include functions for preprocessing
specific hazard information. This is done by scripts.
ESL class variables:
- hazard name
- tract dictionary with item for each consequence:
-- receptor string
-- value (tract level cost shapefile)
- total dictionary with total
-- value
- similar dictionaries for neighborhood, community, borough
- inputs dictionary - other inputs such as liklihood
ESL class functions
-- add consequence (specifying resolution, receptor, cost)
--
"""

# %% import packages
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import matplotlib.pyplot as plt


# %% define class ESL

class ESL:

    def __init__(self, hazard_name: str):
        self.hazard_name = hazard_name
        self.consequence = {}
        self.ESL_total = 0
        self.list_consequences = []
        pass

    # add consequence. map_tract should be GeoDataFrame
    def add_consequence(self, consequence_name: str, receptor_name: str, map_tract):
        self.consequence[consequence_name] = {}
        self.consequence[consequence_name]["receptor"] = receptor_name
        self.consequence[consequence_name]["map_tract"] = map_tract
        self.list_consequences.append(consequence_name)
        pass

    # calculate total ESL based on all consequences
    def calc_ESL_total(self):
        # if no consequences, total ESL is zero
        if len(self.list_consequences) == 0:
            ESL_total = 0
        else:
            # loop and add each consequence
            for i, cons in enumerate(self.list_consequences):
                if i == 0:
                    ESL_total = self.consequence[cons]["map_tract"]["Loss_USD"]
                else:
                    ESL_total += self.consequence[cons]["map_tract"]["Loss_USD"]
        self.ESL_total = ESL_total
        pass


#%% define class for SOV
#not hazard specific, so there's only one input

class SOV:

    def __init__(self, map_tract):
        self.SOV_total = map_tract
        pass

#%% define class for RCA

class RCA:
#this assumes the input is the score at the tract level.
#the logis for the calculation can be built in later

    def __init__(self, hazard_name: str, map_tract):
        self.hazard_name = hazard_name
        self.RCA_total = map_tract
        pass








