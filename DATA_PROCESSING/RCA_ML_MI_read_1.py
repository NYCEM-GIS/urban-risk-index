"""
Mitigation investment -
"""#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% open mitigation geopackages
path_gdb = params.PATHNAMES.at['RCA_ML_MI_gdb', 'Value']
epsg = params.SETTINGS.at['epsg', 'Value']
gdf_points = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_Actions_Points_20190401')
gdf_points = gdf_points.to_crs(epsg = epsg)
gdf_lines = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_Actions_Lines_20190401')
gdf_lines = gdf_lines.to_crs(epsg = epsg)
gdf_polygons = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_Actions_Polygons_20190401')
gdf_polygons = gdf_polygons.to_crs(epsg = epsg)

#%% open mitigation dataset table
path_table = params.PATHNAMES.at['RCA_ML_MI_table', 'Value']
df_table = pd.read_excel(path_table)

#%% remove not mapped, no cost (from 687 to 207)
df_table = df_table.loc[df_table['Cost Estimate']>0, :]
df_table.dropna(subset=['Cost Estimate'], inplace=True)
df_table = df_table.loc[df_table['Mapped'] != 'Not Mapped', :]

#%% create single geodatabase with buffered area of all remaining points, lines, polygons
#get line features from table
gdf_points_valid = gdf_points[['HMP_Index_1', 'geometry']].merge(df_table[['HMP Index',
                                                'HMP Hazard Addressed', 'Cost Per Haz Addressed']],
                                                left_on='HMP_Index_1', right_on='HMP Index', how='inner')
gdf_points_valid['geometry'] = gdf_points_valid['geometry'].buffer(distance = 2640)
gdf_lines_valid = gdf_lines[['HMP_Index_1', 'geometry']].merge(df_table[['HMP Index',
                                                'HMP Hazard Addressed', 'Cost Per Haz Addressed']],
                                                left_on='HMP_Index_1', right_on='HMP Index', how='inner')
gdf_lines_valid['geometry'] = gdf_lines_valid['geometry'].buffer(distance = 2640)
gdf_polygons_valid = gdf_polygons[['HMP_Index_1', 'geometry']].merge(df_table[['HMP Index',
                                                'HMP Hazard Addressed', 'Cost Per Haz Addressed']],
                                                left_on='HMP_Index_1', right_on='HMP Index', how='inner')
gdf_polygons_valid['geometry'] = gdf_polygons_valid['geometry'].buffer(distance = 2640)

#combine into one
gdf_buffer = pd.concat([gdf_points_valid, gdf_lines_valid, gdf_polygons_valid]).reset_index(drop=True)

#%% load the tract dataset
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = gdf_tract.to_crs(epsg=epsg)
gdf_tract['area_ft2'] = gdf_tract['geometry'].area
gdf_tract.index = np.arange(len(gdf_tract))

#%% create blank table to populate with investment values for each hazard
list_hazards =['CBRN', 'Coastal Erosion', 'Coastal Storms', 'Flooding',
                   'Earthquakes', 'Extreme Heat', 'Winter Weather', 'Winter Storms', 'Disease Outbreaks',
                   'Cyber Threats']
df_value = pd.DataFrame(index = gdf_tract['BCT_txt'], data = np.zeros([len(gdf_tract), len(list_hazards)]))
df_value.columns = list_hazards


#%% loop through each project and assign cost to correct table buckets
print("Calculating investment per hazard...", end='')
for i, idx in enumerate(gdf_buffer.index):
    this_buffer = gdf_buffer.loc[[idx]]
    this_intersect = gpd.overlay(gdf_tract, this_buffer, how='intersection')
    this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
    this_intersect['fraction_share'] = this_intersect['area_intersect_ft2'] / this_intersect['area_intersect_ft2'].sum()
    #loop through bucksts and add value
    this_hazard_list = this_buffer['HMP Hazard Addressed'].iloc[0].split(',')
    for hazard in list_hazards:
        if hazard in this_hazard_list:
            for BCT in this_intersect['BCT_txt']:
                this_fraction = this_intersect.loc[this_intersect['BCT_txt']==BCT, 'fraction_share'].iloc[0]
                df_value.at[BCT, hazard] += this_intersect.loc[this_intersect['BCT_txt']==BCT, 'Cost Per Haz Addressed'].iloc[0] * this_fraction
    if i % 50 == 0:
        print(".", end=''),
print('Done')

#%% update df_value columns to reflect hazard names
list_abbrev = ['EXH', 'WIW', 'CST', 'CER', 'CYB', 'RES', 'EMG', 'CRN', 'HIW', 'ERQ', 'FLD']
list_factors =[['Extreme Heat'], ['Winter Weather', 'Winter Storms'], ['Coastal Storms'], ['Coastal Erosion'],
               ['Cyber Threats'], ['Disease Outbreaks'], ['Disease Outbreaks'], ['CBRN'], [], ['Earthquakes'],
               ['Flooding']]
list_multipliers = [1, 1, 1, 1, 1, .5, .5, 1, 1, 1, 1]  #needed to split disease outbreak in half
for i, abbrev in enumerate(list_abbrev):
    df_value[list_abbrev[i]] = df_value[list_factors[i]].sum(axis=1) * list_multipliers[i]

#%% add to gdf
gdf_tract = gdf_tract.merge(df_value, on='BCT_txt', how='left')

#%% get score
for abbrev in list_abbrev:
    gdf_tract = utils.calculate_kmeans(gdf_tract, data_column=abbrev, score_column='Score_'+abbrev)

#%% save as output
path_output = params.PATHNAMES.at['RCA_ML_MI_score', 'Value']
path_output = r'.\2_PROCESSED_INPUTS\905_RCA_ML_MI_SCORE\RCA_ML_MI_score.shp'
gdf_tract.to_file(path_output)

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_output)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating RCA factor: Mitigation Investment.")








