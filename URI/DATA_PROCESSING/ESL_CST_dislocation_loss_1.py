""" estimate cost of dislocated residents from coastal storms """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
import URI.MISC.plotting_1 as plotting
utils.set_home()

#%% EXTRACT PARAMETERS
# Input paths
path_footprint_depths = params.PATHNAMES.at['ESL_CST_building_footprints_depth', 'Value']

# Params
floor_height = params.PARAMS.at['building_floor_height_ft', 'Value']  # assume floor dislocated every 10 ft
flood_disp_height = params.PARAMS.at['building_floor_height_flood_threshold_ft', 'Value']  # assume displacement after 1 ft flooding
ave_displacement_days = params.PARAMS.at['average_duration_CST_displacement_days', 'Value']
P_C1 = 1./params.PARAMS.at['RI_of_category_1_storm_yr', 'Value']
P_C3 = 1./params.PARAMS.at['RI_of_category_3_storm_yr', 'Value']
val_nyc_night_lodging = params.PARAMS.at['cost_nyc_night_lodging', 'Value']
val_nyc_per_diem = params.PARAMS.at['cost_nyc_per_diem', 'Value']
val_nyc_home_meal_per_day = params.PARAMS.at['cost_nyc_home_meals_per_day', 'Value']
# Output Paths
path_results = params.PATHNAMES.at['ESL_CST_dislocation_loss', 'Value']

#%% LOAD DATA
gdf_tract = utils.get_blank_tract(add_pop=True)
gdf_depths = gpd.read_file(path_footprint_depths)

#%%  get probabilities of coastal storm events
# HMP guidelines says "According to these NHC probability models, New York City should
# expect to experience a lower-category hurricane on average once every 19 years
# and a major hurricane (Category 3 or greater) on average once every 74 years.
# assume annual probability of cat 1 is 1/19, and cat 3 is 1/74.  Don't consider 2 or 4

#%% get count of residential units.
df_units = pd.pivot_table(gdf_depths, values='UnitsRes', index='BASE_BBL', aggfunc=len)
df_units.rename(columns={'UnitsRes': 'UnitsRes_Count'}, inplace=True)
gdf_depths = gdf_depths.merge(df_units, left_on='BASE_BBL', right_index=True, how='left')
gdf_depths['Units_Res_Per_Building'] = gdf_depths['UnitsRes'] / gdf_depths['UnitsRes_Count']
N_persons_per_residence = gdf_tract['pop_2020'].sum() / gdf_depths['Units_Res_Per_Building'].sum()


#%%  calculate N floors flooded
def N_floors_flooded(N_floors, depth_flooding):
    if np.isnan(depth_flooding):
        depth_flooding = 0
    if np.isnan(N_floors):
        N_floors = 0
    if N_floors == 0:
        results = 0
    else:
        max_n_floors_flooded = (depth_flooding // floor_height) + np.where( depth_flooding % floor_height >= 1.0, 1, 0)
        results = np.minimum(N_floors, max_n_floors_flooded )
    return results


gdf_depths['C1_N_floors_flooded'] = gdf_depths.apply(
    lambda row: N_floors_flooded(row['NumFloors'],
                                 row['C1_depth']),
    axis=1)
gdf_depths['C3_N_floors_flooded'] = gdf_depths.apply(
    lambda row: N_floors_flooded(row['NumFloors'],
                                 row['C2_depth']),
    axis=1)


#%% calculate number of residential units flooded
def N_residents_displaced(N_floors_flooded, N_floors, N_res_units):
    if np.isnan(N_floors_flooded):
        N_floors_flooded = 0
    if np.isnan(N_floors):
        N_floors = 0
    if np.isnan(N_res_units):
        N_res_units = 0
    if N_floors == 0:
        results = 0
    elif N_floors_flooded == 0:
        results = 0
    else:
        results = N_res_units * N_persons_per_residence
    return results


gdf_depths['C1_N_residents_displaced'] = gdf_depths.apply(
    lambda row: N_residents_displaced(row['C1_N_floors_flooded'],
                                      row['NumFloors'],
                                      row['Units_Res_Per_Building']),
    axis=1)
gdf_depths['C3_N_residents_displaced'] = gdf_depths.apply(
    lambda row: N_residents_displaced(row['C3_N_floors_flooded'],
                                      row['NumFloors'],
                                      row['Units_Res_Per_Building']),
    axis=1)

#%% calculate displacement cost
# assume values are today's dollars
gdf_depths['C1_UDS_Loss_Displacement'] = gdf_depths['C1_N_residents_displaced'] * ave_displacement_days * (val_nyc_night_lodging/N_persons_per_residence + val_nyc_per_diem + val_nyc_home_meal_per_day)
gdf_depths['C3_UDS_Loss_Displacement'] = gdf_depths['C3_N_residents_displaced'] * ave_displacement_days * (val_nyc_night_lodging/N_persons_per_residence + val_nyc_per_diem + val_nyc_home_meal_per_day)
gdf_depths['Loss_USD'] = gdf_depths['C1_UDS_Loss_Displacement']*P_C1 + gdf_depths['C3_UDS_Loss_Displacement'] * P_C3

#%% get tract for each building
gdf_points = gdf_depths.copy()
gdf_points.geometry = gdf_points.geometry.centroid
gdf_points = gpd.sjoin(gdf_points, gdf_tract[['BCT_txt', 'geometry']], how='left', op='within')

#%% aggregate to tract level and merge
df_loss = pd.pivot_table(gdf_points, values='Loss_USD', index='BCT_txt', aggfunc=sum)

#%% merge to gdf_tracts
gdf_tract = gdf_tract.merge(df_loss, on='BCT_txt', how='left')
gdf_tract.fillna(value={'Loss_USD': 0}, inplace=True)

#%% save results in
gdf_tract.to_file(path_results)

#%% plot
plotting.plot_notebook(gdf_tract, column='Loss_USD', title='CST: Dislocation Loss',
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
print("Finished calculating CST dislocation Loss.")








