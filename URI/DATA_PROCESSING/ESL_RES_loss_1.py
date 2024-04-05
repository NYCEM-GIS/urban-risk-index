""" Calculate respiratory illness losses """

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

#%% EXTRACT PARAMETERS
# Input paths
path_covid = params.PATHNAMES.at['ESL_RES_COVID_deaths', 'Value']
path_PVI_gdb = params.PATHNAMES.at['ESL_RES_PVI_gbd', 'Value']
path_PVI_layer = params.PATHNAMES.at['ESL_RES_PVI_layer', 'Value']
path_zcta = params.PATHNAMES.at['BOUNDARY_zcta', 'Value']

# Params
Loss_life = params.PARAMS.at['value_of_stat_life', 'Value']
# Hard-coded
P_mild = 0.049
P_severe = 0.01
R_mild_attack = 0.18
R_severe_attack = 0.33
R_mild_hosp = 0.01
R_severe_hosp = 0.12
R_mild_death = 0.003
R_severe_death = 0.025
Loss_life = utils.convert_USD(Loss_life, 2022)
Loss_wages_2019 = 958.66
Loss_wages = utils.convert_USD(Loss_wages_2019, 2019)
Loss_hosp_2016 = 107000
Loss_hosp = utils.convert_USD(Loss_hosp_2016, 2016)
Loss_econ_mild_2019 = 5000000000  # total
Loss_econ_mild = utils.convert_USD(Loss_econ_mild_2019, 2019)
Loss_econ_severe_2019 = 68000000000
Loss_econ_severe = utils.convert_USD(Loss_econ_severe_2019, 2019)
update_data = False  # set to True to update data

# Output paths
path_loss_death = params.PATHNAMES.at['ESL_RES_death_loss', 'Value']
path_loss_economy = params.PATHNAMES.at['ESL_RES_economy_loss', 'Value']
path_loss_injury = params.PATHNAMES.at['ESL_RES_injury_loss', 'Value']
path_loss_wages = params.PATHNAMES.at['ESL_RES_wages_loss', 'Value']

#%% LOAD DATA
gdf_tracts = utils.get_blank_tract(add_pop=True)
gdf_PVI = gpd.read_file(path_PVI_gdb, drive='FileGDB', layer=path_PVI_layer)
if update_data:
    url = r'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/totals/data-by-modzcta.csv'
    df_covid = pd.read_csv(url, error_bad_lines=False)
    df_covid.to_csv(path_covid)
df_covid = pd.read_csv(path_covid)
gdf_zcta = gpd.read_file(path_zcta)

#%% modify tracts
gdf_tracts['tract_area_sqmi'] = gdf_tracts.geometry.area/(5280**2)
gdf_tracts['tract_pop_per_sqmi'] = gdf_tracts['pop_2020'] / gdf_tracts['tract_area_sqmi']

#%% open vulnerability index
gdf_PVI = utils.project_gdf(gdf_PVI)
gdf_PVI['COMMDIST_area_sqmi'] = gdf_PVI.geometry.area/(5280.**2)

#%% get number of vulnerable people in each tract
gdf_union = gpd.overlay(gdf_tracts, gdf_PVI, how='union')
# drop portions that don't overlap with tracts
gdf_union.dropna(subset=['BCT_txt'], inplace=True)
# assume areas of tracts not covered by PVI have zero vulnerable opo
gdf_union.fillna(value={'Overall_Density_per_SqMi': 0, 'COMMDIST': 0}, inplace=True)
#%% get number of vulnerable persons in the DISTCOMMs
gdf_union['union_area_sqmi'] = gdf_union.geometry.area/(5280.**2)
# the raw value will be refined  based on population distribution
gdf_union['union_vul_pop_raw'] = gdf_union['union_area_sqmi'] * gdf_union['Overall_Density_per_SqMi']
gdf_union['union_pop'] = gdf_union['union_area_sqmi'] * gdf_union['tract_pop_per_sqmi']
gdf_union['union_vul_pop'] = np.zeros(len(gdf_union))
for i, idx in enumerate(gdf_union.index):
    this_union_pop = gdf_union.loc[idx, 'union_pop']
    this_COMMDIST = gdf_union.loc[idx, 'COMMDIST']
    this_COMMDIST_pop = gdf_union.loc[gdf_union['COMMDIST'] == this_COMMDIST, 'union_pop'].sum()
    this_COMMDIST_vul_pop = gdf_union.loc[gdf_union['COMMDIST'] == this_COMMDIST, 'union_vul_pop_raw'].sum()
    gdf_union.loc[idx, 'union_vul_pop'] = this_COMMDIST_vul_pop * this_union_pop / this_COMMDIST_pop
df_group = gdf_union.groupby('geoid')[['union_vul_pop']].sum()
gdf_tracts = gdf_tracts.merge(df_group, left_on='geoid', right_index=True, how='left')
gdf_tracts['pct_total_burden_PVI'] = gdf_tracts['union_vul_pop'] / gdf_tracts['union_vul_pop'].sum()
# the overlay is causing some gaps, causing nan.  fill with average value
gdf_tracts.fillna(value={'pct_total_burden_PVI': gdf_tracts['pct_total_burden_PVI'].median()}, inplace=True)

#%% cases data
df_covid['MODIFIED_ZCTA_STR'] = [str(x) for x in df_covid['MODIFIED_ZCTA']]

#%% open modified ZCTA shapefile
gdf_zcta = utils.project_gdf(gdf_zcta)
gdf_zcta['ZCTA_area_sqmi'] = gdf_zcta.geometry.area/(5280**2)

gdf_zcta = gdf_zcta.merge(df_covid, left_on='modzcta', right_on='MODIFIED_ZCTA_STR', how='left')
# set null values to zero, because they are parks
gdf_zcta.fillna(value={'COVID_DEATH_COUNT': 0}, inplace=True)
gdf_union = gpd.overlay(gdf_tracts, gdf_zcta, how='union')

#%%
# drop portions that don't overlap with tracts
gdf_union.dropna(subset=['BCT_txt'], inplace=True)

#%%
# assume areas of tracts not covered by PVI have zero vulnerable opo
gdf_union.fillna(value={'COVID_DEATH_COUNT': 0, 'MODIFIED_ZCTA_STR': '0'}, inplace=True)

#%% get number of deaths in the in the DISTCOMMs
gdf_union['union_area_sqmi'] = gdf_union.geometry.area/(5280.**2)
# the raw value will be refined  based on population distribution
gdf_union['union_pop'] = gdf_union['union_area_sqmi'] * gdf_union['tract_pop_per_sqmi']
gdf_union['union_death_count'] = np.zeros(len(gdf_union))
for i, idx in enumerate(gdf_union.index):
    this_union_pop = gdf_union.at[idx, 'union_pop']
    this_ZCTA = gdf_union.loc[idx, 'MODIFIED_ZCTA_STR']
    this_ZCTA_pop = gdf_union.loc[gdf_union['MODIFIED_ZCTA_STR']==this_ZCTA, 'union_pop'].sum()
    this_ZCTA_case_count = gdf_union.at[idx, 'COVID_DEATH_COUNT']
    gdf_union.loc[idx, 'union_death_count'] = this_ZCTA_case_count * this_union_pop / this_ZCTA_pop
df_group = gdf_union.groupby('geoid')[['union_death_count']].sum()
gdf_tracts = gdf_tracts.merge(df_group, left_on='geoid', right_index=True, how='left')
gdf_tracts['pct_total_burden_deaths'] = gdf_tracts['union_death_count'] / gdf_tracts['union_death_count'].sum()

# #%% take average of both approaches to get average death rate
gdf_tracts['pct_burden_average'] = (gdf_tracts[['pct_total_burden_deaths',
                                               'pct_total_burden_PVI']].mean(axis=1))/(gdf_tracts[['pct_total_burden_deaths',
                                               'pct_total_burden_PVI']].mean(axis=1)).sum()

#%%  calculate death losses
mild_death_count = gdf_tracts.pop_2020.sum() * P_mild * R_mild_attack * R_mild_death
severe_death_count = gdf_tracts.pop_2020.sum() * P_severe * R_severe_attack * R_severe_death
annual_death_count = mild_death_count + severe_death_count
annual_death_loss = annual_death_count * Loss_life
gdf_tract_death = gdf_tracts.copy()
gdf_tract_death['Loss_USD'] = annual_death_loss * gdf_tracts['pct_burden_average']
gdf_tract_death[['geoid', 'BCT_txt', 'Loss_USD', 'geometry']].to_file(path_loss_death)

#%% calculate injury losses
mild_injury_count = gdf_tracts.pop_2020.sum() * P_mild * R_mild_attack * R_mild_hosp
severe_injury_count = gdf_tracts.pop_2020.sum() * P_severe * R_severe_attack * R_severe_hosp
annual_injury_count = mild_injury_count + severe_injury_count
annual_injury_loss = annual_injury_count * Loss_hosp
gdf_tract_injury = gdf_tracts.copy()
gdf_tract_injury['Loss_USD'] = annual_injury_loss * gdf_tracts['pct_burden_average']
gdf_tract_injury[['geoid', 'BCT_txt',  'Loss_USD', 'geometry']].to_file(path_loss_injury)

#%% calculate wages losses
annual_wages_loss = annual_injury_count * Loss_wages
gdf_tract_wages = gdf_tracts.copy()
gdf_tract_wages['Loss_USD'] = annual_wages_loss * gdf_tracts['pct_burden_average']
gdf_tract_wages[['geoid', 'BCT_txt', 'Loss_USD', 'geometry']].to_file(path_loss_wages)

#%% calculate economy losses, distributed by population
annual_econ_loss = P_mild * Loss_econ_mild + P_severe * Loss_econ_severe
gdf_tract_econ = gdf_tracts.copy()
gdf_tract_econ['Loss_USD'] = annual_econ_loss * gdf_tracts['pop_2020'] / gdf_tracts['pop_2020'].sum()
gdf_tract_econ[['geoid', 'BCT_txt', 'Loss_USD', 'geometry']].to_file(path_loss_economy)

#%% plot
plotting.plot_notebook(gdf_tract_econ, column='Loss_USD', title='RES: Death Loss',
                       legend='Loss USD', cmap='Greens', type='raw')

#%%  document result with readme
try:
    text = """ 
    The data was produced by {}
    Located in {}
    """.format(os.path.basename(__file__), os.path.dirname(__file__))
    path_readme = os.path.dirname(path_loss_death)
    utils.write_readme(path_readme, text)
except:
    pass

#%% output complete message
print("Finished calculating RES loss.")