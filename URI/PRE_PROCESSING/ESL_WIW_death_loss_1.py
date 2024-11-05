""" deaths due to winter storms"""

#%% read packages
import pandas as pd
import os
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_deaths = PATHNAMES.ESL_WIW_deaths_data
path_hosp = PATHNAMES.ESL_WIW_hosp_data
path_borid = PATHNAMES.Borough_to_FIP
# Params
loss_per_death = PARAMS['value_of_stat_life'].value
# Output paths
path_output = PATHNAMES.ESL_WIW_loss_deaths

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)
df_deaths = pd.read_csv(path_deaths, skiprows=9, skipfooter=5, engine='python')
df_hosp = pd.read_csv(path_hosp, skiprows=12, skipfooter=5, engine='python')
df_borid = pd.read_excel(path_borid)

#%% get average number per year across NYC of load deaths
N_deaths_year_NYC = df_deaths['Y Value'].mean()

#%% load hospitalizations.
# Assume that deaths are by borough same as the age-adjusted hospitalization rate
# note it would be better to use unadjusted hospitalization rate, but that is available for only one year
# so may be too noisy

# remove NYC-level data
df_hosp = df_hosp.loc[df_hosp['Geography Name'] != 'New York City', :]

#%% add borough code to hosp data
df_hosp['Bor_ID'] = [df_borid.loc[df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_hosp['Geography Name']]

#%% get borough specific average
df_bor = df_hosp[['Bor_ID', 'Y Value']].groupby('Bor_ID').mean()

#%% distribute deaths using rate as weight
df_bor['N_deaths_yr'] = N_deaths_year_NYC * df_bor['Y Value'] / df_bor['Y Value'].sum()


#%% distribute deaths by population within each borough
def calc_tract_deaths(BCT_txt):
    idx = gdf_tract.index[gdf_tract.BCT_txt == BCT_txt][0]
    this_bor = gdf_tract.at[idx, 'borocode']
    this_pop = gdf_tract.at[idx, 'pop_2020']
    this_bor_pop = gdf_tract.loc[gdf_tract.borocode == this_bor, 'pop_2020'].sum()
    this_N_deaths = df_bor.at[int(this_bor), 'N_deaths_yr']
    return this_N_deaths * this_pop / this_bor_pop


gdf_tract['N_deaths'] = gdf_tract.apply(lambda x: calc_tract_deaths(x['BCT_txt']), axis=1)

#%% convert to loss
loss_deaths_total = utils.convert_USD(loss_per_death, 2022)
gdf_tract['Loss_USD'] = gdf_tract['N_deaths'] * loss_deaths_total

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='WIW: Death Loss',
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
print("Finished calculating WIW death loss.")