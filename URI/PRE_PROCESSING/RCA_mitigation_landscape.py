#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()


class RCA_ML:
    def __init__(self):
        # Input paths
        self.path_gi = PATHNAMES.RCA_ML_GI_raw
        self.path_mi_gdb = PATHNAMES.RCA_ML_MI_gdb
        self.path_mi_table = PATHNAMES.RCA_ML_MI_table
        self.path_pwf = PATHNAMES.RCA_ML_PWF_raw
        self.path_veg = PATHNAMES.RCA_ML_VC_table
        self.path_nta = PATHNAMES.BOUNDARY_nta
        # Output paths
        self.path_results_green_infrastructure = PATHNAMES.RCA_ML_GI_score
        self.path_results_mitigation_investment = PATHNAMES.RCA_ML_MI_score
        self.path_results_parks_water_features = PATHNAMES.RCA_ML_PWF_score
        self.path_results_vegetative_cover = PATHNAMES.RCA_ML_VC_score
    
    def calculate_green_infrastructure(self):
        #%% LOAD DATA
        gdf_gi = gpd.read_file(self.path_gi)

        #%% modify
        gdf_gi = utils.project_gdf(gdf_gi)
        gdf_gi['OBJECTID'] = np.arange(len(gdf_gi))

        #%% tracts
        gdf_tract = utils.get_blank_tract()

        #%% crete buffered tracts
        gdf_tract_buffer = gdf_tract.copy()
        gdf_tract_buffer['geometry'] = gdf_tract['geometry'].buffer(distance=528)
        gdf_tract_buffer['area_buffer_mi2'] = gdf_tract_buffer['geometry'].area / (5280*5280)

        #%% get count in each tract
        gdf_join = gpd.sjoin(gdf_tract_buffer, gdf_gi)
        count = gdf_join['BCT_txt'].value_counts()
        df_counts = pd.DataFrame(index=count.index, data={'count': count.values})

        #%% join results to tracts
        gdf_merge = gdf_tract.merge(df_counts, left_on='BCT_txt', right_index=True, how='left')
        gdf_merge.fillna(value=0, inplace=True)
        gdf_merge = utils.calculate_kmeans(gdf_merge, data_column='count', score_column='Score', n_cluster=5)

        return gdf_merge
    
    def calculate_mitigation_investment(self):
        #%% LOAD DATA
        gdf_points = gpd.read_file(self.path_mi_gdb, driver='FileGDB', layer='Mitigation_action_points_update_20211027')
        gdf_lines = gpd.read_file(self.path_mi_gdb, driver='FileGDB', layer='Mitigation_action_lines_update_20211027')
        gdf_polygons = gpd.read_file(self.path_mi_gdb, driver='FileGDB', layer='Mitigation_action_polygons_update_20211213')
        df_table = pd.read_excel(self.path_mi_table)

        #%% open mitigation geopackages
        gdf_points = utils.project_gdf(gdf_points)
        gdf_lines = utils.project_gdf(gdf_lines)
        gdf_polygons = utils.project_gdf(gdf_polygons)

        #%% remove not mapped, no cost (from 687 to 207)
        df_table = df_table.loc[df_table['Cost Estimate'] > 0, :]
        df_table.dropna(subset=['Cost Estimate'], inplace=True)
        df_table = df_table.loc[df_table['Mapped'] != 'Not Mapped', :]

        #%% remove everything but "completed"
        df_table = df_table.loc[df_table['Schedule'] == 'Completed', :]

        #%% create single geodatabase with buffered area of all remaining points, lines, polygons
        # get line features from table
        gdf_points_valid = gdf_points[['HMP_Index_1', 'geometry']].merge(
            right=df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
            left_on='HMP_Index_1',
            right_on='HMP Index',
            how='inner'
        )
        gdf_points_valid['geometry'] = gdf_points_valid['geometry'].buffer(
            distance=gdf_points_valid['Impact Buffer (miles)'].values * 5280.
        )
        gdf_lines_valid = gdf_lines[['HMP_Index_1', 'geometry']].merge(
            df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
            left_on='HMP_Index_1',
            right_on='HMP Index',
            how='inner'
        )
        gdf_lines_valid['geometry'] = gdf_lines_valid['geometry'].buffer(
            distance=gdf_lines_valid['Impact Buffer (miles)'].values * 5280.
        )
        gdf_polygons_valid = gdf_polygons[['HMP_Index_1', 'geometry']].merge(
            df_table[['HMP Index', 'HMP Hazard Addressed', 'Cost Estimate', "Impact Buffer (miles)"]],
            left_on='HMP_Index_1',
            right_on='HMP Index',
            how='inner'
        )
        gdf_polygons_valid['geometry'] = gdf_polygons_valid['geometry'].buffer(
            distance=gdf_polygons_valid['Impact Buffer (miles)'].values * 5280.
        )

        # combine into one
        gdf_buffer = pd.concat([gdf_points_valid, gdf_lines_valid, gdf_polygons_valid]).reset_index(drop=True)

        #%% load the tract dataset
        gdf_tract = utils.get_blank_tract()
        gdf_tract['area_ft2'] = gdf_tract['geometry'].area

        #%% create blank table to populate with investment values for each hazard
        list_hazards = ['Coastal Erosion', 'Coastal Storms', 'Flooding',
                        'Earthquakes', 'Extreme Heat', 'Winter Weather', 'Winter Storms']
        df_value = pd.DataFrame(index=gdf_tract['BCT_txt'], data=np.zeros([len(gdf_tract), len(list_hazards)]))
        df_value.columns = list_hazards


        # Precompute intersection areas and fraction shares for all buffers
        print("Calculating investment per hazard...", end='')

        # Perform intersection for all buffers at once
        gdf_intersections = gpd.overlay(gdf_tract, gdf_buffer, how='intersection')
        gdf_intersections['area_intersect_ft2'] = gdf_intersections['geometry'].area
        gdf_intersections['fraction_share'] = gdf_intersections['area_intersect_ft2'] / gdf_intersections.groupby('HMP_Index_1')['area_intersect_ft2'].transform('sum')

        # Expand hazards into multiple rows for each hazard in the list
        gdf_intersections = gdf_intersections.assign(
        hazard_list=gdf_intersections['HMP Hazard Addressed'].str.split(',')
        ).explode('hazard_list')

        # Filter only relevant hazards
        gdf_intersections = gdf_intersections[gdf_intersections['hazard_list'].isin(list_hazards)]

        # Calculate weighted cost for each BCT and hazard
        gdf_intersections['weighted_cost'] = gdf_intersections['Cost Estimate'] * gdf_intersections['fraction_share']

        # Aggregate costs by BCT and hazard
        df_aggregated = gdf_intersections.groupby(['BCT_txt', 'hazard_list'])['weighted_cost'].sum().unstack(fill_value=0)

        # Update df_value with aggregated results
        df_value.update(df_aggregated)

        # Update df_value columns to reflect hazard names
        mapping = {
            'EXH': ['Extreme Heat'],
            'WIW': ['Winter Weather', 'Winter Storms'],
            'CSF': ['Coastal Storms', 'Flooding'],
            'CER': ['Coastal Erosion'],
            'CSW': ['Coastal Storms'],
            'ERQ': ['Earthquakes']
        }

        # Use vectorized operations to sum relevant columns
        for abbrev, factors in mapping.items():
            df_value[abbrev] = df_value[factors].sum(axis=1)

        #%% add to gdf
        gdf_tract = gdf_tract.merge(df_value, on='BCT_txt', how='left')

        #%% get score
        for abbrev in mapping.keys():
            gdf_tract = utils.calculate_kmeans(gdf_tract, data_column=abbrev, score_column='Score_'+abbrev)
        
        return gdf_tract

