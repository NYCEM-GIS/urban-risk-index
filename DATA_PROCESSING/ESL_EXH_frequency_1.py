"""
Calculates the frequency of extreme heat events.
Uses table from HH&C
Puts data into GIS at tract level
"""

#%% load packages
import time
time_start = time.time()

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

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

#%%  document result with readme if possible
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
time_run = round((time.time() - time_start) / 60.0, 1)
print("Finished calculating EXH event rate in {} minutes.".format(time_run))




