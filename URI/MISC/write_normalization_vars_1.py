""" Write table of possible normalization factors"""

#%% read packages
import numpy as np
import geopandas as gpd
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
from URI.MISC import utils_1 as utils
utils.set_home()

#%% #%% open tract
gdf_tract = utils.get_blank_tract(add_pop=True)

#%% open footprint
#open buildings
path_footprint = PATHNAMES.ESL_CST_building_footprints
gdf_footprint = gpd.read_file(path_footprint)

#%% gdt building count
gdf_join = gpd.sjoin(gdf_footprint, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['BIN'], aggfunc=len)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'BIN': 0}, inplace=True)
gdf_tract.rename(columns={"BIN":"Building_Count"}, inplace=True)

#%% estimate floor area
#note this is conservatively high because num_floors is largest # in building group
#ex: in co-op city, all buildings are marked as 33 floors, but some are only 4.
gdf_footprint['Floor_sqft'] = gdf_footprint['Shape_Area'] * np.maximum(gdf_footprint['NumFloors'], 1)
gdf_join = gpd.sjoin(gdf_footprint, gdf_tract, how='left', predicate='within')
gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
df_count = gdf_join.pivot_table(index='BCT_txt', values=['Floor_sqft'], aggfunc=sum)
gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
gdf_tract.fillna(value={'Floor_sqft': 0}, inplace=True)


#%% add square miles
gdf_tract['Sq_miles'] = gdf_tract.geometry.area / (5280.**2)

#%% trim to only necessary
gdf_tract = gdf_tract[['BCT_txt', 'Sq_miles', 'Building_Count', 'Floor_sqft', 'pop_2020', 'geometry']]
gdf_tract.rename(columns={"Sq_miles":"AREA_SQMI", "Building_Count":"BLD_CNT", "Floor_sqft":'FLOOR_SQFT', 'pop_2020':'POP'}, inplace=True)

#%% save to other
path_norm = PATHNAMES.OTH_normalize_values
gdf_tract.to_file(path_norm)
