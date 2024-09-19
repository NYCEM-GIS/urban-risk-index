""" Calculate respiratory illness losses """

#%% load packages
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_loss = PATHNAMES.ESL_EMG_loss
# Params
loss_per_death = PARAMS['value_of_stat_life'].value
loss_per_death = utils.convert_USD(loss_per_death, 2022)
# Hard-coded
N_outbreaks = 7.
start_year = 1981
end_year = 2020 #inclusive
total_outbreak_deaths = 12049.34  #for 7 events

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)

#%%loss calculation
P_outbreak_yr = N_outbreaks / (end_year - start_year + 1)  #add 1 because inclusive
deaths_per_outbreak = total_outbreak_deaths / N_outbreaks
deaths_per_year = deaths_per_outbreak * P_outbreak_yr
loss_per_year = deaths_per_year * loss_per_death

#%% assign to populations
gdf_tract['Loss_USD'] = loss_per_year * gdf_tract['pop_2020']/gdf_tract['pop_2020'].sum()

#%% save
gdf_tract[['geoid', 'BCT_txt', 'Loss_USD', 'geometry']].to_file(path_loss)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='EMG: Deaths Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

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
print("Finished calculating EMG loss.")


