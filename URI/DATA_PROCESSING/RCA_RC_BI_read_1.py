""" get bikability score"""

#%% read packages
import pandas as pd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_bike_score = PATHNAMES.RCA_RC_BI_bikescore_csv
# Output paths
path_output = PATHNAMES.RCA_RC_BI_score

#%% LOAD DATA
df_bike_score = pd.read_csv(path_bike_score)
gdf_tract = utils.get_blank_tract()

#%% load walkscore and merge to tract shapefile
temp = df_bike_score['BCT_txt']
df_bike_score['BCT_txt'] = [str(x) for x in temp]
gdf_tract = gdf_tract.merge(df_bike_score[['BCT_txt', 'bikescore']], on='BCT_txt', how='left')

gdf_tract.fillna(gdf_tract['bikescore'].median(), inplace=True)

#%% calculate score
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='bikescore')

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Score', title='RCA_RC_BI: Bikability',
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
print("Finished calculating RCA factor: bikability.")