""" read in the NFIP Policies into tract level map"""

#%% read packages
import geopandas as gpd
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_fp = PATHNAMES.RCA_RR_FP_raw
path_footprint = PATHNAMES.ESL_CST_building_footprints

# Output paths
path_results = PATHNAMES.RCA_RR_FP_score

#%% LOAD DATA
gdf_tract = utils.get_blank_tract()
gdf_fp = gpd.read_file(path_fp)
gdf_footprint = gpd.read_file(path_footprint)

#%% count buildings by tract and save result in scratch
#spatial join to get count
gdf_join = gpd.sjoin(gdf_footprint, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['BIN'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'BIN': 0}, inplace=True)
gdf_tract.rename(columns={"BIN": "Building_Count"}, inplace=True)

#%%count number of policies by tract
gdf_join = gpd.sjoin(gdf_fp, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['Type'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'Type': 0}, inplace=True)
gdf_tract.rename(columns={"Type": "Policy_Count"}, inplace=True)


#%%calc percent of buildings covered
def calc_percent_covered(policies, buildings):
    if buildings == 0:
        result = 0
    else:
        result = 100. * policies / buildings
    return min(result, 100)


gdf_tract['Percent_Coverage'] = gdf_tract.apply(
    lambda row: calc_percent_covered(row['Policy_Count'], row['Building_Count']),
    axis=1)

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Percent_Coverage')

#%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RR_FP: Flood Insurance Coverage',
                       legend='Score', cmap='Blues', type='score')

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
print("Finished calculating RR factor RF: flood insurance coverage.")







