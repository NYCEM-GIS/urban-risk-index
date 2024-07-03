"""
calculate the total economic loss due to deaths from extreme heat (EXH)
"""

#%% load packages
import numpy as np
import pandas as pd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_stormevents = params.PATHNAMES.at['stormevents_table', 'Value']
path_stormeventsboroughs = params.PATHNAMES.at['stormeventsboroughs_table', 'Value']
path_population_tract = params.PATHNAMES.at['population_by_tract', 'Value']
# Hard-coded
start_date = params.HARDCODED.at['heat_event_count_start_date', 'Value']
end_date = params.HARDCODED.at['heat_event_count_end_date', 'Value']
# Params
deaths_year = params.PARAMS.at['EXH_deaths_per_year', 'Value']
value_life = params.PARAMS.at['value_of_stat_life', 'Value']
# Output paths
path_results = params.PATHNAMES.at['EXH_ESL_deaths_per_year_tract', 'Value']

#%% LOAD DATA
df_stormevents = pd.read_excel(path_stormevents)
df_stormeventsboroughs = pd.read_excel(path_stormeventsboroughs)
df_population = pd.read_excel(path_population_tract, skiprows=5)
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

#%% convert value of lost life to 2019 value
value_life = utils.convert_USD(value_life, 2022)

#%% mere into single dataframe and calculate
gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
gdf_loss['deaths_year'] = gdf_loss['Heat_Events_Per_Year'] * gdf_loss['deaths_per_event']
gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * value_life

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
