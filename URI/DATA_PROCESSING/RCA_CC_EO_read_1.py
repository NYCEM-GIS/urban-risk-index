""" read in the community infrastructure factor into tract level map"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_events = params.PATHNAMES.at['RCA_CC_EO_locations', 'Value']
path_CC_EO = params.PATHNAMES.at['RCA_CC_EO_score', 'Value']
# Settings
epsg = params.SETTINGS.at['epsg', 'Value']
# Output paths
path_output = params.PATHNAMES.at['RCA_CC_EO_score', 'Value']

#%% LOAD DATA
df_events = pd.read_csv(path_events)
gdf_tract = gpd.read_file(path_CC_EO)

#%% open education and outreach points
#create point map with lat and lon
gdf_events = gpd.GeoDataFrame(df_events, geometry = gpd.points_from_xy(df_events.Longitude, df_events.Latitude),
                              crs=4326)
gdf_events['Event_ID'] = np.arange(len(gdf_events))
gdf_events = gdf_events.to_crs(epsg=epsg)
#drop na values
gdf_events.dropna(subset=['Latitude', 'Longitude'], inplace=True)

#%% get count from tract
#gdf_tract = utils.calculate_radial_count(gdf_events, column_key='Event_ID', buffer_distance_ft=2640)

#%% calculate score with kmeans clustering
gdf_result = utils.calculate_kmeans(gdf_tract, data_column='Fraction_C', score_column='Score',
                                    n_cluster=5)

#%% save as output
gdf_result.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_result, column='Score', title='RCA_CC_EO: Education and Outreach',
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
print("Finished calculating RCA factor: Education and Outreach.")