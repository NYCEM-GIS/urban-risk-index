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
            #rename loss on incoming tract
            map_tract.rename(columns={'Loss_USD':"Loss_USD_2"}, inplace=True)
            #addd to ESL_map
            self.ESL_map = self.ESL_map.merge(map_tract[['BCT_txt', 'Loss_USD_2']], on='BCT_txt', how='left')
            self.ESL_map['Loss_USD'] = self.ESL_map['Loss_USD'] + self.ESL_map['Loss_USD_2']
            #remove
            self.ESL_map.drop(columns=['Loss_USD_2'], inplace=True)
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
        self.URI_map = self.URI_map.merge(self.RCA.RCA_map[['BCT_txt', 'RCA']], on='BCT_txt', how='left')
        self.URI_map = self.URI_map.merge(self.SOV.SOV_map[['BCT_txt', 'SOV']], on='BCT_txt', how='left')
        self.URI_map['URI_Raw'] = self.URI_map['Loss_USD']*self.URI_map['SOV'] / self.URI_map['RCA']

        #calculate score 1-5
        self.URI_map = utils.calculate_kmeans(self.URI_map, data_column = 'URI_Raw', score_column='URI',
                                              n_cluster = 5)
        self.URI_map = utils.calculate_quantile(self.URI_map, data_column = 'URI_Raw', score_column='URI_QT',
                                              n_cluster = 5)
        self.URI_map = utils.calculate_equal_interval(self.URI_map, data_column = 'URI_Raw', score_column='URI_EI',
                                              n_cluster = 5)
        pass

    def save_URI_FULL(self):
        URI_full_map = self.URI_map[['BCT_txt', 'URI_Raw', 'URI', 'URI_QT', 'URI_EI',  'Loss_USD', 'SOV', 'RCA', 'geometry']].copy()
        # URI_full_map = URI_full_map.merge(self.RCA.RCA_map[['BCT_txt', 'RCA']], on='BCT_txt', how='left')
        # URI_full_map = URI_full_map.merge(self.SOV.SOV_map[['BCT_txt', 'SOV']], on='BCT_txt', how='left')
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
        URI_full_map = URI_full_map.merge(gdf_norm[['BCT_txt', 'Sq_miles', 'Building_C', 'Floor_sqft', 'pop_2010']], on='BCT_txt',
                                          how='left')
        #add neighborhoods, PUMAs, boroughs
        # merge with tracts
        gdf_tract = utils.get_blank_tract()
        gdf_URI = URI_full_map.merge(gdf_tract[['BOROCODE', 'NEIGHBORHO', 'PUMA', 'BCT_txt']], on='BCT_txt', how='left')
        def weight_ave(x, weights):
            if weights.sum() != 0:
                result = np.average(x, weights=weights)
            else:
                result = 3
            return result
        wm = lambda x: weight_ave(x, weights=gdf_URI.loc[x.index, "pop_2010"])
        #run for neighborhoods
        df_NEIGHBORHO = gdf_URI.groupby(["NEIGHBORHO"]).agg(N_SOV=("SOV", wm),
                                                            N_RCA=("RCA", wm),
                                                            N_ESL=("ESL", sum)
                                                            )
        df_NEIGHBORHO['N_URI_Raw'] = df_NEIGHBORHO['N_ESL'] * df_NEIGHBORHO['N_SOV'] / df_NEIGHBORHO['N_RCA']
        df_NEIGHBORHO.index.name = 'index'
        df_NEIGHBORHO['NEIGHBORHO'] = df_NEIGHBORHO.index
        df_NEIGHBORHO = utils.calculate_kmeans(df_NEIGHBORHO, data_column='N_URI_Raw', score_column='N_URI',
                                               n_cluster=5)
        df_NEIGHBORHO = utils.calculate_quantile(df_NEIGHBORHO, data_column='N_URI_Raw', score_column='N_URI_QT',
                                               n_cluster=5)
        df_NEIGHBORHO = utils.calculate_equal_interval(df_NEIGHBORHO, data_column='N_URI_Raw', score_column='N_URI_EI',
                                               n_cluster=5)
        gdf_URI = gdf_URI.merge(df_NEIGHBORHO[['N_ESL', 'N_SOV', 'N_RCA', 'N_URI_Raw', 'N_URI', 'N_URI_QT', 'N_URI_EI',"NEIGHBORHO"]],
                                left_on='NEIGHBORHO', right_on='NEIGHBORHO', how='left')
        #run for PUMA
        df_PUMA = gdf_URI.groupby(["PUMA"]).agg(P_SOV=("SOV", wm),
                                                P_RCA=("RCA", wm),
                                                P_ESL=("ESL", sum)
                                                )
        df_PUMA['P_URI_Raw'] = df_PUMA['P_ESL'] * df_PUMA['P_SOV'] / df_PUMA['P_RCA']
        df_PUMA.index.name = 'index'
        df_PUMA['PUMA'] = df_PUMA.index
        df_PUMA = utils.calculate_kmeans(df_PUMA, data_column='P_URI_Raw', score_column='P_URI',
                                         n_cluster=5)
        df_PUMA = utils.calculate_quantile(df_PUMA, data_column='P_URI_Raw', score_column='P_URI_QT',
                                         n_cluster=5)
        df_PUMA = utils.calculate_equal_interval(df_PUMA, data_column='P_URI_Raw', score_column='P_URI_EI',
                                         n_cluster=5)
        gdf_URI = gdf_URI.merge(df_PUMA[['P_ESL', 'P_SOV', 'P_RCA', 'P_URI_Raw', 'P_URI', 'P_URI_QT', 'P_URI_EI', 'PUMA']], left_on='PUMA',
                                right_on='PUMA', how='left')
        #repeat for boros
        df_boro = gdf_URI.groupby(["BOROCODE"]).agg(B_SOV=("SOV", wm),
                                                    B_RCA=("RCA", wm),
                                                    B_ESL=("ESL", sum)
                                                    )
        df_boro['B_URI_Raw'] = df_boro['B_ESL'] * df_boro['B_SOV'] / df_boro['B_RCA']
        df_boro.index.name = 'index'
        df_boro['BOROCODE'] = df_boro.index
        df_boro = utils.calculate_kmeans(df_boro, data_column='B_URI_Raw', score_column='B_URI',
                                         n_cluster=5)
        df_boro = utils.calculate_quantile(df_boro, data_column='B_URI_Raw', score_column='B_URI_QT',
                                         n_cluster=5)
        df_boro = utils.calculate_equal_interval(df_boro, data_column='B_URI_Raw', score_column='B_URI_EI',
                                         n_cluster=5)
        gdf_URI = gdf_URI.merge(df_boro[['B_ESL', 'B_SOV', 'B_RCA', 'B_URI_Raw', 'B_URI', 'B_URI_QT', 'B_URI_EI', "BOROCODE"]],
                                left_on='BOROCODE', right_on='BOROCODE', how='left')
        path_save = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI_FULL\URI_FULL_{}_tract.shp'.format(
            self.hazard_name, self.hazard_name)
        gdf_URI.to_file(path_save)







