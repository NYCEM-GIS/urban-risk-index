"""
calculate the total economic loss due to deaths from EXH
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()


#### GET EVENT FREQUENCY

#%% open all storm events
#open storm events
path_stormevents = params.PATHNAMES.at['stormevents_table', 'Value']
path_stormeventsboroughs = params.PATHNAMES.at['stormeventsboroughs_table', 'Value']
df_stormevents = pd.read_excel(path_stormevents)
df_stormeventsboroughs = pd.read_excel(path_stormeventsboroughs)

#%% screen out heat events
heat_events_bool = ['Heat' in x for x in df_stormevents['Name']]
df_stormevents = df_stormevents.loc[heat_events_bool, :]

#%% screen out using date range
#get start, end date
start_date = params.HARDCODED.at['heat_event_count_start_date', 'Value']
end_date = params.HARDCODED.at['heat_event_count_end_date', 'Value']
df_stormevents = df_stormevents.loc[df_stormevents['StartDate']>start_date]
df_stormevents = df_stormevents.loc[df_stormevents['EndDate']<end_date]

#%% get the count per borough
#make empty dataframe to populate with borough count
df_borcount = pd.DataFrame(index=[1, 2, 3, 4, 5],
                           data={'Heat_Events_Per_Year':np.zeros(5)})
#loop through event storm event id in borough count list.
#if is a stormevent with extreme heat, add 1
for idx in df_stormeventsboroughs.index:
    this_stormeventid = df_stormeventsboroughs.at[idx, 'StormEventId']
    if this_stormeventid in df_stormevents['Id'].values:
        this_borid = int(df_stormeventsboroughs.at[idx, 'BoroughId'])
        df_borcount.at[this_borid,'Heat_Events_Per_Year'] += 1

#%% convert to annual rate of extreme heat events per year
n_years = (end_date - start_date).days / 365.25
df_borrate = df_borcount / n_years
df_borrate.index  = [str(x) for x in df_borrate.index]

#%% save annual rate for the death rate calculation
path_borough_event_rate = params.PATHNAMES.at['EXH_events_per_borough', 'Value']
df_borrate.to_csv(path_borough_event_rate)

#%% populate block dataset
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_block = pd.merge(gdf_block, df_borrate, left_on='BoroCode', right_index=True, how='inner')

#reproject
epsg = params.SETTINGS.at['epsg', 'Value']
gdf_block = gdf_block.to_crs(epsg = epsg)

#%% dissolve to tract level
gdf_tract = gdf_block[['BCT_txt', 'geometry', 'Heat_Events_Per_Year']].dissolve(by='BCT_txt', aggfunc='mean')

#%% save results in
path_results = params.PATHNAMES.at['EXH_events_per_year_tracts', 'Value']
gdf_tract.to_file(path_results)

#### GET ANNUAL DEATH BY TRACT

#%% get number of deaths per year
deaths_year = params.PARAMS.at['EXH_deaths_per_year', 'Value']

#%% get the number of events per borough.  Note this is calculated by EXH_frequency_1.py
path_borough_event_rate = params.PATHNAMES.at['EXH_events_per_borough', 'Value']
df_borrate = pd.read_csv(path_borough_event_rate)

#%% load population
path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
df_population = pd.read_excel(path_population_tract, skiprows=5)
df_population.dropna(inplace=True)

#%% get population for each borough
#get borough population
df_population_borough = df_population.groupby('2010 DCP Borough Code').sum()[2010]

#%%calculate m =  # deaths due to extreme heat per 1000 people
x  = df_population_borough.values
y = df_borrate['Heat_Events_Per_Year'].values
numerator = deaths_year
denominator = np.array([x[i] * y[i] for i in np.arange(len(x))]).sum()/1000.
m = numerator / denominator

#%% import block and dissolve to tract
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'geometry']].dissolve(by='BCT_txt', as_index=False)

#%%find id for join on population
df_population['BCT_ID'] = [str(int(df_population['2010 DCP Borough Code'].iloc[i])) + \
                           str(int(df_population['2010 Census Tract'].iloc[i])).zfill(6) for i in np.arange(len(df_population))]

gdf_tract = gdf_tract.merge(df_population[[2010, 'BCT_ID']], left_on='BCT_txt', right_on='BCT_ID', how='inner')

#%% calculate number of deaths per heat event
gdf_tract['deaths_per_event'] = [m*x/1000. for x in gdf_tract[2010]]

#%% raname columns 2010
gdf_tract.rename(columns={2010:'Pop2010'}, inplace=True)

#%% save results in
path_results = params.PATHNAMES.at['EXH_deaths_per_event', 'Value']
gdf_tract.to_file(path_results)

#### GET LOSS BY TRACT

#%% load the event rate, death rate, and cost per death
path_events_per_year = params.PATHNAMES.at['EXH_events_per_year_tracts', 'Value']
gdf_events_per_year = gpd.read_file(path_events_per_year)
path_deaths_per_event = params.PATHNAMES.at['EXH_deaths_per_event', 'Value']
gdf_deaths_per_event = gpd.read_file(path_deaths_per_event)
value_life_2016 = params.PARAMS.at['value_of_stat_life_2016', 'Value']

#%% convert value of lost life to 2019 value
value_life = utils.convert_USD(value_life_2016, 2016)

#%% mere into single dataframe and calculate
gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
gdf_loss['deaths_year'] = gdf_loss['Heat_Event'] * gdf_loss['deaths_per']
gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * value_life

#%% save results in
path_results = params.PATHNAMES.at['EXH_ESL_deaths_per_year_tract', 'Value']
gdf_loss.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_loss, column='Loss_USD', title='EXH: Deaths Loss',
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
print("Finished calculating EXH loss due to excess deaths.")




