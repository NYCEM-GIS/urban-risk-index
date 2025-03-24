""" calculate various losses due to coastal storms """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.settings as SETTINGS
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()


def load_data(loss_function):

    def wrapper():

        return 

    return wrapper

def combine_flood_dataset():

    def wrapper(*args, **kwargs):
        gdf_flood_data_list = [
            gdf_flood_bronx, 
            gdf_flood_kings, 
            gdf_flood_manhattan, 
            gdf_flood_queens, 
            gdf_flood_richmond,
        ]
        gdf_flood_data_by_tract_list = []
        return 




def hazus_loss(gdf_flood):
    ##%% convert from 2018 dollars
    gdf_flood.Loss_USD = utils.convert_USD(gdf_flood.Loss_USD.values, 2018)

    #%% merge with tracts
    gdf_tract = gdf_tract.merge(gdf_flood[['tract', 'Loss_USD']], left_on='geoid', right_on=['tract'], how='left')
    gdf_tract['Loss_USD'] = gdf_tract['Loss_USD'].fillna(0)
