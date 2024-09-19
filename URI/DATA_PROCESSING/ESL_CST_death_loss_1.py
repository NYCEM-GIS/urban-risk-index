""" calculate storm related deaths from the HH&C database"""


#%% read packages
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
path_eventtypes = PATHNAMES.HHC_eventtypes
path_stormeventtypes = PATHNAMES.HHC_stormeventtypes
path_storms = PATHNAMES.stormevents_table
path_FLD_loss = PATHNAMES.ESL_FLD_hazus_loss
path_HIW_loss = PATHNAMES.ESL_CST_hazus_loss
path_population_tract = PATHNAMES.population_by_tract
# Hard-coded
start_date = PARAMS['hhc_event_count_start_date'].value
end_date = PARAMS['hhc_event_count_end_date'].value
n_years = (end_date - start_date).days / 365.25
# Output paths
path_output = PATHNAMES.ESL_CST_deaths_loss

#%% LOAD DATA
df_types = pd.read_excel(path_eventtypes)
df_stormevents = pd.read_excel(path_stormeventtypes)
df_storms = pd.read_excel(path_storms)
gdf_tract = utils.get_blank_tract()
gdf_FLD = gpd.read_file(path_FLD_loss)
gdf_HIW = gpd.read_file(path_HIW_loss)
df_pop = pd.read_excel(path_population_tract, skiprows=5)

#%% only keep storms of event type 7
df_coastalevents = df_stormevents.loc[df_stormevents['EventTypeId']==6, :]

#%% find these 32 events in
df_storms.index= df_storms['Id']
id_coastal = [df_coastalevents.at[idx, 'StormEventId'] for idx in df_coastalevents.index]
df_storms_cst = df_storms.loc[id_coastal, :]

#%% cut off data
df_storms_cst['StartDate'] = pd.to_datetime(df_storms_cst['StartDate'])
df_storms_cst['EndDate'] = pd.to_datetime(df_storms_cst['EndDate'])
df_storms_cst = df_storms_cst.loc[df_storms_cst['StartDate']>start_date]
df_storms_cst = df_storms_cst.loc[df_storms_cst['EndDate']<end_date]

#%% count fatalities and injuries
n_deaths = df_storms_cst['Fatalities'].sum() / n_years
n_injuries = df_storms_cst['Injuries'].sum() / n_years
loss_deaths = PARAMS.at['value_of_stat_life', 'Value'] * n_deaths
#no injuries
loss_deaths_total = utils.convert_USD(loss_deaths, 2022)

#%%  distribute loss by population and total losses from coastal flooding and hurricane wind
#join losses
gdf_tract = gdf_tract.merge(gdf_FLD[['BCT_txt', 'Loss_USD']], on='BCT_txt', how='left')
gdf_tract.rename(columns={'Loss_USD':'Loss_USD_FLD'}, inplace=True)
gdf_tract = gdf_tract.merge(gdf_HIW[['BCT_txt', 'Loss_USD']], on='BCT_txt', how='left')
gdf_tract.rename(columns={'Loss_USD':'Loss_USD_HIW'}, inplace=True)
#join population
df_pop.dropna(inplace=True, subset=['2020 DCP Borough Code', '2020 Census Tract'])
df_pop.rename(columns={2020:'pop_2020'}, inplace=True)
df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2020 DCP Borough Code'])) + str(int(df_pop.at[x,'2020 Census Tract'])).zfill(6) for x in df_pop.index]
gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2020']], on='BCT_txt', how='left')
gdf_tract['weight'] = gdf_tract['pop_2020'] * (gdf_tract['Loss_USD_FLD']+gdf_tract['Loss_USD_HIW'])
gdf_tract['Loss_USD'] = loss_deaths_total * gdf_tract['weight'] / gdf_tract['weight'].sum()

#%% save as output
gdf_tract.to_file(path_output)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CST: Deaths Loss',
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
print("Finished calculating CST death loss.")