"""
calculate the total economic loss due to deaths from extreme heat (EXH)
"""

#%% load packages
import numpy as np
import pandas as pd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_stormevents = PATHNAMES.stormevents_table
path_stormeventsboroughs = PATHNAMES.stormeventsboroughs_table
path_population_tract = PATHNAMES.population_by_tract
path_ecostress = PATHNAMES.ESL_EXH_ecostress_2020
# Hard-coded
start_date = HARDCODED.heat_event_count_start_date
end_date = HARDCODED.heat_event_count_end_date
# Params
deaths_year = PARAMS['EXH_deaths_per_year'].value
value_life = PARAMS['value_of_stat_life'].value
# Output paths
path_results = PATHNAMES.EXH_ESL_deaths_per_year_tract

#%% LOAD DATA
df_stormevents = pd.read_excel(path_stormevents)
df_stormeventsboroughs = pd.read_excel(path_stormeventsboroughs)
df_population = pd.read_excel(path_population_tract, skiprows=5)
df_ecostress = pd.read_csv(path_ecostress)
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% screen out heat events
heat_events_bool = ['Heat' in x for x in df_stormevents['Name']]
df_stormevents = df_stormevents.loc[heat_events_bool, :]

#%% screen out using date range
df_stormevents['StartDate'] = pd.to_datetime(df_stormevents['StartDate'])
df_stormevents['EndDate'] = pd.to_datetime(df_stormevents['EndDate'])
df_stormevents = df_stormevents.loc[df_stormevents['StartDate']>start_date]
df_stormevents = df_stormevents.loc[df_stormevents['EndDate']<end_date]

#%% get the count per borough
#make empty dataframe to populate with borough count
df_borcount = pd.DataFrame(index=[1, 2, 3, 4, 5],
                           data={'Heat_Events_Per_Year': np.zeros(5)})
# loop through event storm event id in borough count list.
# if is a stormevent with extreme heat, add 1
for idx in df_stormeventsboroughs.index:
    this_stormeventid = df_stormeventsboroughs.at[idx, 'StormEventId']
    if this_stormeventid in df_stormevents['Id'].values:
        this_borid = int(df_stormeventsboroughs.at[idx, 'BoroughId'])
        df_borcount.at[this_borid, 'Heat_Events_Per_Year'] += 1

#%% convert to annual rate of extreme heat events per year
n_years = (end_date - start_date).days / 365.25
df_borrate = df_borcount / n_years
df_borrate.index = [str(x) for x in df_borrate.index]

#%% populate tract dataset
gdf_events_per_year = pd.merge(gdf_tract, df_borrate, left_on='borocode', right_index=True, how='inner')

#%% load population
df_population.dropna(inplace=True, subset=['2020 DCP Borough Code', '2020 Census Tract'])

#%% get population for each borough
#get borough population
df_population_borough = df_population.groupby('2020 DCP Borough Code').sum()[2020]

#%%calculate m =  # deaths due to extreme heat per 1000 people
x = df_population_borough.values
y = df_borrate['Heat_Events_Per_Year'].values
numerator = deaths_year
denominator = np.array([x[i] * y[i] for i in np.arange(len(x))]).sum()/1000.
m = numerator / denominator

#%%find id for join on population
df_population['BCT_ID'] = [str(int(df_population['2020 DCP Borough Code'].iloc[i])) + \
                           str(int(df_population['2020 Census Tract'].iloc[i])).zfill(6) for i in np.arange(len(df_population))]

gdf_deaths_per_event = gdf_tract.merge(df_population[[2020, 'BCT_ID']], left_on='BCT_txt', right_on='BCT_ID', how='inner')

#%% calculate number of deaths per heat event
gdf_deaths_per_event['deaths_per_event'] = [m*x/1000. for x in gdf_deaths_per_event[2020]]

#%% raname columns 2020
gdf_deaths_per_event.rename(columns={2020: 'Pop2020'}, inplace=True)

#%% merge Ecostress data with gdf_events_per_year to get PCT90 into the events dataframe
gdf_events_per_year['BCT_txt'] = gdf_events_per_year['BCT_txt'].astype(str)
df_ecostress['boroct2020'] = df_ecostress['boroct2020'].astype(str)
gdf_events_per_year = gdf_events_per_year.merge(gdf_deaths_per_event[['BCT_txt', 'Pop2020']], on='BCT_txt', how='left')
gdf_events_per_year = gdf_events_per_year.merge(df_ecostress[['boroct2020', 'PCT90']], 
                                                left_on='BCT_txt', right_on='boroct2020', how='inner')

#%% Calculate Weighting Factor using Ecostress PCT90
gdf_events_per_year['ecostress_rank'] = utils.normalize_rank_percentile(
    gdf_events_per_year['PCT90'].values,
    list_input_null_values=[-999],
    output_null_value=-999)
gdf_events_per_year['Weighting_Factor'] = gdf_events_per_year['ecostress_rank'] * gdf_events_per_year['Pop2020']

#%% Recalculate number of deaths per heat event with weighting factor
gdf_deaths_per_event['deaths_per_event_weighted'] = gdf_deaths_per_event['deaths_per_event'] * gdf_events_per_year['Weighting_Factor']

#%% Merge into single dataframe and calculate weighted losses
gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
gdf_loss['deaths_year'] = gdf_loss['Heat_Events_Per_Year'] * gdf_loss['deaths_per_event_weighted']
gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * value_life

#%% convert value of lost life to 2019 value
value_life = utils.convert_USD(value_life, 2022)

#%% mere into single dataframe and calculate
#gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
#gdf_loss['deaths_year'] = gdf_loss['Heat_Events_Per_Year'] * gdf_loss['deaths_per_event']
#gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * value_life


#%% save results in
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

