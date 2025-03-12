""" calculate storm related deaths from the HH&C database"""
#dependencies: ESL_FLD_hazus_1.py


#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.settings as SETTINGS
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_dot = PATHNAMES.ESL_CST_dot_table
path_cst_loss = PATHNAMES.ESL_FLD_hazus_loss
# Settings
ref_year = SETTINGS.target_year
# Output paths
path_output = PATHNAMES.ESL_CST_loss_transportation

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)
df_dot = pd.read_excel(path_dot, sheet_name='Major Storm Events', skiprows=2, skipfooter=4, index_col=0)
gdf_fld = gpd.read_file(path_cst_loss)

#%% calculate annual loss
dot_loss_tot = [utils.convert_USD(x, ref_year) for x in df_dot.loc['Total Costs', :].values]
dot_loss_ave = np.average(dot_loss_tot)

#%% distribute loss according to flood damage
#flood damage
gdf_tract = gdf_tract.merge(gdf_fld[['BCT_txt', 'Loss_USD']], on='BCT_txt', how='inner')
#rename Loss_USD as weight
gdf_tract.rename(columns={"Loss_USD":"weight"}, inplace=True)
gdf_tract['Loss_USD'] = dot_loss_ave * gdf_tract['weight'] / gdf_tract['weight'].sum()

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CSF: Transportation Loss',
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
print("Finished calculating CST Transportation loss.")
