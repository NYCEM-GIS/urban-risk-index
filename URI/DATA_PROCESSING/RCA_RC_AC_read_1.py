"""
import ac data
convert into tract data with correct projection
"""

#%% load packages
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_ac = params.PATHNAMES.at['RCA_RC_ACH_raw', 'Value']
path_ac_taskforce = params.PATHNAMES.at['RCA_RC_AC_ac_taskforce', 'Value']
# Output paths
path_results = params.PATHNAMES.at['RCA_RC_AC_score', 'Value']

# Air conditioining
column_ac = "DATA_VALUE"
column_ac_out = "ac_per"

#%% LOAD DATA
path_gbd = os.path.dirname(path_ac_taskforce)
layer_gbd = os.path.basename(path_ac_taskforce)
gdf_tf = gpd.read_file(path_gbd, driver='FileGDB', layer=layer_gbd)

#%% convert ac data to track average

gdf_tract = utils.convert_to_tract_average(path_ac, column_ac, column_ac_out)

#%% get tract population
gdf_tract_pop = utils.get_blank_tract(add_pop=True)
gdf_tract = gdf_tract.merge(gdf_tract_pop[['BCT_txt', 'pop_2020']], on='BCT_txt', how='left')

#%% get ACs added by program
gdf_tf = utils.project_gdf(gdf_tf)

#%% get count within each tract
gdf_join = gpd.sjoin(gdf_tf, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['field'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'field': 0}, inplace=True)


#%% update ac percentage
def update_ac(current_percent, pop, new_count):
    if current_percent == -999.0:
        result = current_percent
    elif pop == 0:
        result = current_percent
    else:
        result = current_percent + (new_count/pop)*100.
    return min(result, 100)


gdf_tract['ac_per_post'] = gdf_tract.apply(lambda row: update_ac(row['ac_per'], row['pop_2020'], row['field']), axis=1)

#%% calculate percent rank
gdf_tract['ac_per_rnk'] = utils.normalize_rank_percentile(
    gdf_tract['ac_per_post'].values,
    list_input_null_values=[-999],
    output_null_value=-999)
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='ac_per_rnk')

#%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_AC: Air Conditioning',
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
print("Finished calculating RC factor AC: air conditioning.")

