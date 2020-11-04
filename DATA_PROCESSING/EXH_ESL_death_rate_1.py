"""
Calculates the death rate due to extreme heat
Assume there are 121 excess deaths each year due to extreme heat (Matte et al 2016)
"""

#%% load packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

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
print("Finished calculating EXH death rate.")





