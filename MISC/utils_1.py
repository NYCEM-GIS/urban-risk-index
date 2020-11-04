""" Contains utilities that are used by all scripts """

import numpy as np
import pandas as pd
from MISC import params_1 as params
import os
import scipy.stats as stats
import geopandas as gpd

#%% set home directory
def set_home():
    os.chdir(params.PATHNAMES.at['home', 'Value'])
set_home()

#%% create readme
def write_readme(path_readme, readme_text):
    f = open(path_readme + "\\README.txt", "w")
    f.write(readme_text)
    f.close()

#%% normalize score to scale of 0 to 1 (exclusive)
    #values should be numpy array
def normalize_rank_percentile(values, list_input_null_values=[-999], output_null_value=-999):
    #remove null values from array
    values_trim = np.delete(values, np.where(np.isin(values, list_input_null_values)))
    #add a very high values and low value to prevent 0 and 100 values
    values_trim = np.r_[-1e20, values_trim, 1e20]
    #look through and calculate values_out
    values_out = np.zeros(len(values))
    for i, val in enumerate(values):
        if np.isin(val, list_input_null_values):
            values_out[i] = output_null_value
        else:
            values_out[i] = stats.percentileofscore(values_trim, val, kind='rank')/100
    return values_out

#%% zonal statistics with input shapefile into output shapefile
#handle null values.
def convert_to_tract_average(path_data, column_name, column_name_out,
                             list_input_null_values=[-999], output_null_value=-999):
    #get data to convert
    gdf_data = gpd.read_file(path_data)
    epsg = params.SETTINGS.at['epsg', 'Value']
    gdf_data = gdf_data.to_crs(epsg=epsg)
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = gdf_tract.to_crs(epsg=epsg)

    #get spatial union, drop areas with no tract
    gdf_union = gpd.overlay(gdf_tract, gdf_data, how='union')
    gdf_union.dropna(subset=['BCT_txt'], inplace=True)

    #calculate area of each union slice
    gdf_union['area_ft2'] = gdf_union['geometry'].area
    # for each tract, calculate area weighted average of contributions
    # if some values are null, use other values.  If all value are null, assign null
    output_null_value = -999
    list_input_null_values = [-999]
    gdf_tract[column_name_out] = np.zeros(len(gdf_tract))
    for i, idx in enumerate(gdf_tract.index):
        this_BCT = gdf_tract.at[idx, 'BCT_txt']
        # get slices from this tract
        this_gdf_union = gdf_union.loc[gdf_union['BCT_txt'] == this_BCT, :]
        # remove null data values
        this_gdf_union.dropna(subset=[column_name], inplace=True)
        # remove null values based on list
        for null_val in list_input_null_values:
            keep_bool = (this_gdf_union[column_name].values != null_val)
            this_gdf_union = this_gdf_union.loc[keep_bool, :]
        # if nothing left, set tract value to null value
        if len(this_gdf_union) == 0:
            gdf_tract.at[idx, column_name_out] = output_null_value
        # otherise set to spatially weighted average
        else:
            DATA_VALUE_tract_ave = np.average(this_gdf_union[column_name].values,
                                              weights=this_gdf_union['area_ft2'].values)
            gdf_tract.at[idx, column_name_out] = DATA_VALUE_tract_ave
    return gdf_tract

#%% convert value to 2018 dollars using consumer price index (CPI)
def convert_USD(base_value, base_year: int):
    #get target year from parameters
    target_year = params.SETTINGS.at['target_year', 'Value']
    #load CPI index
    path_CPI = params.PATHNAMES.at['CPI_table', 'Value']
    df_CPI = pd.read_excel(path_CPI, skiprows=10,
                           index_col=0, parse_dates=True)
    #get the yearly average
    df_CPI_year = df_CPI.resample('Y').mean()
    df_CPI_year.index = df_CPI_year.index.year
    index_factor = df_CPI_year.at[target_year, 'CPIAUCNS' ] / df_CPI_year.at[base_year, 'CPIAUCNS' ]
    target_value = base_value * index_factor
    return target_value

#%% calculate RCA using pre-processed factors
#all factors should be census tract level results
#list_factors_gdf is a list of the factors as geodataframes
#list_factors_columns is a list of the column names with the relevant scor
#dict_buckets is a coding for the RCA bucket for each factor.  It is blank for now.
def calculate_RCA(list_factor_gdfs, list_factor_columns, dict_buckets={}):
    # get data to convert
    epsg = params.SETTINGS.at['epsg', 'Value']
    path_block = params.PATHNAMES.at['census_blocks', 'Value']
    gdf_block = gpd.read_file(path_block)
    gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
    gdf_tract = gdf_tract.to_crs(epsg=epsg)
    #open each gdf and take average of all factor columns (for now)
    for i, gdf in enumerate(list_factor_gdfs):
        gdf_tract = gdf_tract.merge(gdf.drop(columns='geometry'), on='BCT_txt')
    #no nan handling for now
    gdf_tract['Composite_Score'] = gdf_tract[list_factor_columns].mean(axis=1)
    return gdf_tract












