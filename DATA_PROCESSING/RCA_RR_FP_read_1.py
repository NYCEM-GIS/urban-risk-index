""" read in the community infrastructure factor into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from census import Census
from us import states
from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% #%% open tract
gdf_tract = utils.get_blank_tract()

#%% open insurance policies
path_fp = params.PATHNAMES.at['RCA_RR_FP_raw', 'Value']
gdf_fp = gpd.read_file(path_fp)

#%% create scratch folder if not already
folder_scratch = params.PATHNAMES.at['RCA_RR_FP_SCORE_scratch', 'Value']
if not os.path.exists(folder_scratch):
    os.mkdir(folder_scratch)

#%% count buildings by tract and save result in scratch
#open buildings
path_footprint = params.PATHNAMES.at['ESL_CST_building_footprints', 'Value']
gdf_footprint = gpd.read_file(path_footprint, driver='FileGBD', layer='NYC_Buildings_composite_20200110')
#spatial join to get count
print("Begin Join")
gdf_join = gpd.sjoin(gdf_footprint, gdf_tract, how='left', op='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['BIN'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'BIN': 0}, inplace=True)
path_count = params.PATHNAMES.at['RCA_RR_FP_building_count_csv', "Value"]
gdf_tract.rename(columns={"BIN":"Building_Count"}, inplace=True)
df_count.to_csv(path_count)

#%%count number of policies by tract
gdf_join = gpd.sjoin(gdf_fp, gdf_tract, how='left', op='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['Type'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'Type': 0}, inplace=True)
gdf_tract.rename(columns={"Type":"Policy_Count"}, inplace=True)

#%%calc percent of buildings covered
def calc_percent_covered(policies, buildings):
    if buildings==0:
        result = 0
    else:
        result = 100.* policies / buildings
    if result > 100:
        print("Warning: more policies than buildings with {} policies and {} buildings.".format(policies, buildings))
    return min(result, 100)

gdf_tract['Percent_Coverage'] = gdf_tract.apply(lambda row: calc_percent_covered(row['Policy_Count'], row['Building_Count']),
                                                axis=1)

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Percent_Coverage')


#%% save results in
path_results = params.PATHNAMES.at['RCA_RR_FP_score', 'Value']
gdf_tract.to_file(path_results)

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_results)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating RR factor FP.")







