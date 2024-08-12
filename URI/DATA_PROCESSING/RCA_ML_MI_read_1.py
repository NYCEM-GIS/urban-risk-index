"""
Mitigation investment -
"""#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_gdb = PATHNAMES.RCA_ML_MI_gdb
path_table = PATHNAMES.RCA_ML_MI_table
# Output paths
path_output = PATHNAMES.RCA_ML_MI_score

#%% LOAD DATA
gdf_points = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_action_points_update_20211027')
gdf_lines = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_action_lines_update_20211027')
gdf_polygons = gpd.read_file(path_gdb, driver='FileGDB', layer='Mitigation_action_polygons_update_20211213')
df_table = pd.read_excel(path_table)

#%% open mitigation geopackages
gdf_points = utils.project_gdf(gdf_points)
gdf_lines = utils.project_gdf(gdf_lines)
gdf_polygons = utils.project_gdf(gdf_polygons)

#%% remove not mapped, no cost (from 687 to 207)
df_table = df_table.loc[df_table['Cost Estimate'] > 0, :]
df_table.dropna(subset=['Cost Estimate'], inplace=True)
df_table = df_table.loc[df_table['Mapped'] != 'Not Mapped', :]

#%% remove everything but "completed"
df_table = df_table.loc[df_table['Schedule'] == 'Completed', :]

#%% create single geodatabase with buffered area of all remaining points, lines, polygons
# get line features from table
gdf_points_valid = gdf_points[['HMP_Index_1', 'geometry']].merge(
    right=df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
    left_on='HMP_Index_1',
    right_on='HMP Index',
    how='inner')
gdf_points_valid['geometry'] = gdf_points_valid['geometry'].buffer(distance=gdf_points_valid['Impact Buffer (miles)'].values * 5280.)
gdf_lines_valid = gdf_lines[['HMP_Index_1', 'geometry']].merge(
    df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
    left_on='HMP_Index_1',
    right_on='HMP Index',
    how='inner')
gdf_lines_valid['geometry'] = gdf_lines_valid['geometry'].buffer(distance=gdf_lines_valid['Impact Buffer (miles)'].values * 5280.)
gdf_polygons_valid = gdf_polygons[['HMP_Index_1', 'geometry']].merge(
    df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
    left_on='HMP_Index_1',
    right_on='HMP Index',
    how='inner')
gdf_polygons_valid['geometry'] = gdf_polygons_valid['geometry'].buffer(distance=gdf_polygons_valid['Impact Buffer (miles)'].values * 5280.)

# combine into one
gdf_buffer = pd.concat([gdf_points_valid, gdf_lines_valid, gdf_polygons_valid]).reset_index(drop=True)

#%% load the tract dataset
gdf_tract = utils.get_blank_tract()
gdf_tract['area_ft2'] = gdf_tract['geometry'].area

#%% create blank table to populate with investment values for each hazard
list_hazards = ['CBRN', 'Coastal Erosion', 'Coastal Storms', 'Flooding',
                'Earthquakes', 'Extreme Heat', 'Winter Weather', 'Winter Storms', 'Disease Outbreaks',
                'Cyber Threats']
df_value = pd.DataFrame(index=gdf_tract['BCT_txt'], data=np.zeros([len(gdf_tract), len(list_hazards)]))
df_value.columns = list_hazards


#%% loop through each project and assign cost to correct table buckets
print("Calculating investment per hazard...", end='')
for i, idx in enumerate(gdf_buffer.index):
    this_buffer = gdf_buffer.loc[[idx]]
    this_intersect = gpd.overlay(gdf_tract, this_buffer, how='intersection')
    this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
    this_intersect['fraction_share'] = this_intersect['area_intersect_ft2'] / this_intersect['area_intersect_ft2'].sum()
    # loop through bucksts and add value
    this_hazard_list = this_buffer['HMP Hazard Addressed'].iloc[0].split(',')
    for hazard in list_hazards:
        if hazard in this_hazard_list:
            for BCT in this_intersect['BCT_txt']:
                this_fraction = this_intersect.loc[this_intersect['BCT_txt'] == BCT, 'fraction_share'].iloc[0]
                df_value.at[BCT, hazard] += this_intersect.loc[this_intersect['BCT_txt'] == BCT, 'Cost Estimate'].iloc[0] * this_fraction
print('Done')

#%% update df_value columns to reflect hazard names
list_abbrev = ['EXH', 'WIW', 'CST', 'CER', 'CYB', 'RES', 'EMG', 'CRN', 'HIW', 'ERQ', 'FLD']
list_factors = [['Extreme Heat'], ['Winter Weather', 'Winter Storms'], ['Coastal Storms'], ['Coastal Erosion'],
                ['Cyber Threats'], ['Disease Outbreaks'], ['Disease Outbreaks'], ['CBRN'], [], ['Earthquakes'],
                ['Flooding']]
list_multipliers = [1, 1, 1, 1, 1, .5, .5, 1, 1, 1, 1]  # needed to split disease outbreak in half
for i, abbrev in enumerate(list_abbrev):
    df_value[list_abbrev[i]] = df_value[list_factors[i]].sum(axis=1) * list_multipliers[i]

#%% add to gdf
gdf_tract = gdf_tract.merge(df_value, on='BCT_txt', how='left')

#%% get score
for abbrev in list_abbrev:
    gdf_tract = utils.calculate_kmeans(gdf_tract, data_column=abbrev, score_column='Score_'+abbrev)

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
for haz in list_abbrev:
    plotting.plot_notebook(gdf_tract, column='Score_'+haz, title='RCA_ML_MI: Mitigation Investment ({})'.format(haz),
                           legend='Score', cmap='Blues', type='score')

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








