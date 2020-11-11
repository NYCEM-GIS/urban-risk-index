""" shelter capacity"""
#need to handle nan values

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

#%% load data
path_sc = params.PATHNAMES.at['RCA_RC_SC_raw', 'Value']
df_sc = pd.read_excel(path_sc, sheet_name='AC Capacity')
df_nta2ac = pd.read_excel(path_sc, sheet_name='NTA to AC')

#%% load population data
path_pop = params.PATHNAMES.at['population_by_tract', 'Value']
df_pop = pd.read_excel(path_pop, skiprows=5)
df_pop = df_pop.iloc[1:, :]
df_pop.index=np.arange(len(df_pop))
df_pop['BCT_txt'] = [str(int(df_pop.at[x, '2010 DCP Borough Code'])) + str(int(df_pop.at[x,'2010 Census Tract'])).zfill(6) for x in df_pop.index]

#%%load neighborhood data
path_nta = params.PATHNAMES.at['BOUNDARY_neighborhood', 'Value']
gdf_nta = gpd.read_file(path_nta)
gdf_nta = utils.project_gdf(gdf_nta)

#%% load tract
path_block = params.PATHNAMES.at['census_blocks', 'Value']
gdf_block = gpd.read_file(path_block)
gdf_tract = gdf_block[['BCT_txt', 'BoroCode', 'geometry']].dissolve(by='BCT_txt', as_index=False)
gdf_tract = utils.project_gdf(gdf_tract)
gdf_tract.index = np.arange(len(gdf_tract))

#%% load neighborhood to track
path_nta2ct = params.PATHNAMES.at['BOUNDARY_tract_to_neighborhood', 'Value']
df_nta2ct = pd.read_excel(path_nta2ct)
df_nta2ct['BCT_txt'] = [str(int(df_nta2ct.at[x, '2010 NYC Borough Code'])) + str(int(df_nta2ct.at[x,'2010 Census Tract'])).zfill(6) for x in df_nta2ct.index]


#%% get population of each area command and pop density of shelter
#add nta code to tract number
df_pop = df_pop.merge(df_nta2ct[['Neighborhood Tabulation Area (NTA)Code', 'BCT_txt']], on='BCT_txt', how='left')
#add AC to nta code
df_pop = df_pop.merge(df_nta2ac[['NTA Code', 'Area Command']], left_on='Neighborhood Tabulation Area (NTA)Code',
                      right_on='NTA Code', how='left')
#eliminate nan values.  These are parks, cemetarys, airports with <0.1% of population
df_pop.dropna(subset=['Area Command'], inplace=True)
#sum result
df_pop_ac = df_pop.groupby(by='Area Command').sum()[[2010]]
#merge with AC capacity numbers
df_sc = df_sc.merge(df_pop_ac, left_on='Area Command', right_index=True, how='left')
df_sc['Shelter Capacity per 1000 residents'] = df_sc['Tot Long-Term Capacity'] * 1000 / df_sc[2010]

#%% merge back to the tracts
df_pop = df_pop.merge(df_sc[['Area Command', 'Shelter Capacity per 1000 residents']], on='Area Command', how='left')
gdf_tract = gdf_tract.merge(df_pop, on='BCT_txt', how='left')

#%%assign -999 to null values
gdf_tract.fillna(value={'Shelter Capacity per 1000 residents': -999}, inplace=True)

#%% calculate score
#need to handle missing data
gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Shelter Capacity per 1000 residents')

#%% save as output
gdf_tract.rename(columns={2010:'2010 Pop', 2000:'2000 Pop'}, inplace=True)
path_output = params.PATHNAMES.at['RCA_RC_SC_score', 'Value']
gdf_tract.to_file(path_output)

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
print("Finished calculating RCA factor: shelter capacity")