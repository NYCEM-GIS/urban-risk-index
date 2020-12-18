# %% import packages
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import matplotlib.pyplot as plt
from MISC import utils_1 as utils
from MISC import params_1 as params

"""
Define class ESL that contains information about estimated loss.
Note the class does not include functions for preprocessing
specific hazard information. 
"""

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
        self.consequence[consequence_name]["map_tract"] = map_tract.copy(deep=True)
        self.list_consequences.append(consequence_name)
        if len(self.list_consequences) == 1:
            self.ESL_map = map_tract
        elif len(self.list_consequences) > 1:
            self.ESL_map['Loss_USD'] = self.ESL_map['Loss_USD'].values + map_tract['Loss_USD'].values
        pass

    # calculate total ESL based on all consequences
    # def calc_ESL_total(self):
    #     print("FIXED11!")
    #     # if no consequences, total ESL is zero
    #     if len(self.list_consequences) == 0:
    #         #ESL_total = 0
    #         Loss_USD_Total = 0
    #     else:
    #         # loop and add each consequence
    #         for i, cons in enumerate(self.list_consequences):
    #             print(cons)
    #             if i == 0:
    #                 Loss_USD_Total = self.consequence[cons]["map_tract"]["Loss_USD"].values
    #                 self.ESL_map = self.consequence[cons]["map_tract"].copy(deep=True)
    #                 print(self.ESL_map.sum())
    #             else:
    #                 Loss_USD_Total = Loss_USD_Total + self.consequence[cons]["map_tract"]["Loss_USD"].values
    #                 self.ESL_map['Loss_USD'] = Loss_USD_Total
    #             print("HERE! {}".format(i))
    #             print(self.ESL_map.sum())
    #     pass


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
        self.URI_map['URI_Raw'] = self.ESL.ESL_map['Loss_USD']*self.SOV.SOV_map['SOV'] / self.RCA.RCA_map['RCA']

        #calculate score 1-5
        self.URI_map = utils.calculate_kmeans(self.URI_map, data_column = 'URI_Raw', score_column='URI',
                                              n_cluster = 5)
        pass

    def save_URI_FULL(self):
        URI_full_map = self.URI_map[['BCT_txt', 'URI_Raw', 'URI', 'Loss_USD', 'geometry']].copy()
        URI_full_map = URI_full_map.merge(self.RCA.RCA_map[['BCT_txt', 'RCA']], on='BCT_txt', how='left')
        URI_full_map = URI_full_map.merge(self.SOV.SOV_map[['BCT_txt', 'SOV']], on='BCT_txt', how='left')
        URI_full_map.rename(columns={'Loss_USD': 'ESL'}, inplace=True)
        # add all consequences
        for con in self.ESL.list_consequences:
            con_label = 'ESL_' + con.replace(" ", "_")
            con_map = self.ESL.consequence[con]["map_tract"]
            con_map.rename(columns={'Loss_USD': con_label}, inplace=True)
            URI_full_map = URI_full_map.merge(con_map[['BCT_txt', con_label]], on='BCT_txt', how='left')
        # add normalization factors: population, area, buildings
        path_norm = params.PATHNAMES.at['OTH_normalize_values', 'Value']
        gdf_norm = gpd.read_file(path_norm)
        URI_full_map = URI_full_map.merge(gdf_norm[['BCT_txt', 'Sq_miles', 'Building_C', 'pop_2010']], on='BCT_txt',
                                          how='left')
        path_save = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
            self.hazard_name, self.hazard_name)
        URI_full_map.to_file(path_save)









