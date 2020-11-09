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
from MISC import utils_1 as utils


# %% define class ESL

class ESL:

    def __init__(self, hazard_name: str):
        self.hazard_name = hazard_name
        self.consequence = {}
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
                    Loss_USD_Total = self.consequence[cons]["map_tract"]["Loss_USD"]
                    self.ESL_map = self.consequence[cons]["map_tract"]
                else:
                    Loss_USD_Total += self.consequence[cons]["map_tract"]["Loss_USD"]
        self.ESL_map['Loss_USD'] = Loss_USD_Total
        pass


#%% define class for SOV
#not hazard specific, so there's only one input

class SOV:

    def __init__(self, hazard_name, map_tract):
        self.hazard_name = hazard_name
        self.SOV_map = map_tract
        pass

#%% define class for RCA

class RCA:
#this assumes the input is the score at the tract level.
#the logis for the calculation can be built in later

    def __init__(self, hazard_name: str, map_tract):
        self.hazard_name = hazard_name
        self.RCA_map = map_tract
        pass

#%% define URI class
class URI:

    def __init__(self, hazard_name: str, ESL, SOV, RCA):
        self.hazard_name = hazard_name
        self.ESL = ESL
        self.SOV = SOV
        self.RCA = RCA
        pass

    def calc_URI(self):
        #calculate raw URI
        self.URI_map = self.ESL.ESL_map.copy()
        self.URI_map['URI_Score_Raw'] = self.ESL.ESL_map['Loss_USD']*self.SOV.SOV_map['Score'] / self.RCA.RCA_map['Score']
        # for i, idx in enumerate(self.URI_map.index):
        #     this_BCT = self.URI_map.at[idx, 'BCT_txt']
        #     this_ESL = self.URI_map.at[idx, 'Loss_USD']
        #     this_SOV = self.SOV.SOV_map.loc[self.SOV.SOV_map['BCT_txt']==this_BCT, 'Score']
        #     this_RCA = self.RCA.RCA_map.loc[self.RCA.RCA_map['BCT_txt']==this_BCT, 'Score']
        #     this_URI_raw = this_ESL * this_SOV / this_RCA
        #     self.URI_map.at[idx, 'URI_Score_Raw'] = this_URI_raw

        #calculate score 1-5
        self.URI_map = utils.calculate_kmeans(self.URI_map, data_column = 'URI_Score_Raw', score_column='URI_Score',
                                              n_cluster = 5)
        pass










