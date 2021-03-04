""" calculate storm related deaths from the HH&C database"""
#dependencies: ESL_FLD_hazus_1.py


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% load tract
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% load DOT table
path_dot = params.PATHNAMES.at['ESL_CST_dot_table', 'Value']
df_dot = pd.read_excel(path_dot, sheet_name='Major Storm Events', skiprows=2, skipfooter=4, index_col=0)

#%% calculate annual loss
ref_year = params.SETTINGS.at['target_year', 'Value']
dot_loss_tot = [utils.convert_USD(x, ref_year) for x in df_dot.loc['Total Costs', :].values]
dot_loss_ave = np.average(dot_loss_tot)

#%% distribute loss according to flood damage
#load flood damage
path_fld_loss = params.PATHNAMES.at['ESL_FLD_hazus_loss', 'Value']
gdf_fld = gpd.read_file(path_fld_loss)
gdf_tract = gdf_tract.merge(gdf_fld[['BCT_txt', 'Loss_USD']], on='BCT_txt', how='inner')
#rename Loss_USD as weight
gdf_tract.rename(columns={"Loss_USD":"weight"}, inplace=True)
gdf_tract['Loss_USD'] = dot_loss_ave * gdf_tract['weight'] / gdf_tract['weight'].sum()

#%% save as output
path_output = params.PATHNAMES.at['ESL_CST_loss_dot', 'Value']
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CST: DOT Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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
print("Finished calculating CST DOT loss.")
