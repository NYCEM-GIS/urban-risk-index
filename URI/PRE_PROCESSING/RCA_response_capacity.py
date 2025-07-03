import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.ops import nearest_points

import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS, ABBREVIATIONS
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()

class RCA_RC:
    def __init__(self):
        self.results = {}
        # Extract parameters
        self.list_abbrv = [x.abbreviation for x in ABBREVIATIONS.values() if (x.category == "Hazard") and  (x.status == 'Active')] # all active hazards
        self.buffer_radius = HARDCODED.search_buffer_for_shelter_capacity_ft  # in feet
        # Input paths
        self.path_ac = PATHNAMES.RCA_RC_ACH_raw
        self.path_ac_taskforce = PATHNAMES.RCA_RC_AC_ac_taskforce
        self.path_bike_score = PATHNAMES.RCA_RC_WA_walkscore_csv
        self.path_layer_cc = PATHNAMES.RCA_RC_CC_layer
        self.path_hospital = PATHNAMES.RCA_RC_EMA_raw
        self.path_evacuation_centers = PATHNAMES.RCA_RC_EP_raw
        self.path_evacauation_zone = PATHNAMES.RCA_RC_EP_evac_zones
        self.path_activation = PATHNAMES.RCA_RC_IE_activation
        self.path_layer_sc = PATHNAMES.RCA_RC_SC_layer
        self.path_walk_score = PATHNAMES.RCA_RC_WA_walkscore_csv
        self.path_footprint = PATHNAMES.ESL_CST_building_footprints
        # Output paths
        self.path_results_ac = PATHNAMES.RCA_RC_AC_score
        self.path_results_bikability = PATHNAMES.RCA_RC_BI_score
        self.path_results_cooling = PATHNAMES.RCA_RC_CC_score
        self.path_results_emergency_medical_facility = PATHNAMES.RCA_RC_EM_score
        self.path_results_evacuation_potential = PATHNAMES.RCA_RC_EP_score
        self.path_results_instituion_experience = PATHNAMES.RCA_RC_IN_score
        self.path_results_shelter_capacity = PATHNAMES.RCA_RC_SC_score
        self.path_results_transit_score = PATHNAMES.RCA_RC_TR_score
        self.path_results_walk_score = PATHNAMES.RCA_RC_WA_score

    def _update_ac_percentage(self, current_percent, pop, new_count):
        """
        Update air conditioning percentage.
        """
        if current_percent == -999.0:
            result = current_percent
        elif pop == 0:
            result = current_percent
        else:
            result = current_percent + (new_count / pop) * 100.0
        return min(result, 100)

    def calculate_ac(self):
        """
        Calculate air conditioning response capacity.
        """
        column_ac = "DATA_VALUE"
        column_ac_out = "ac_per"

        # Load data
        path_gbd = os.path.dirname(self.path_ac_taskforce)
        layer_gbd = os.path.basename(self.path_ac_taskforce)
        gdf_tf = gpd.read_file(path_gbd, driver='FileGDB', layer=layer_gbd)

        # Convert AC data to tract average
        gdf_tract = utils.convert_to_tract_average(self.path_ac, column_ac, column_ac_out)

        # Get tract population
        gdf_tract_pop = utils.get_blank_tract(add_pop=True)
        gdf_tract = gdf_tract.merge(gdf_tract_pop[['BCT_txt', 'pop_2020']], on='BCT_txt', how='left')

        # Get ACs added by program
        gdf_tf = utils.project_gdf(gdf_tf)

        # Get count within each tract
        gdf_join = gpd.sjoin(gdf_tf, gdf_tract, how='left', predicate='within')
        gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
        df_count = gdf_join.pivot_table(index='BCT_txt', values=['field'], aggfunc=len)
        gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
        gdf_tract.fillna(value={'field': 0}, inplace=True)

        gdf_tract['ac_per_post'] = gdf_tract.apply(
            lambda row: self._update_ac_percentage(row['ac_per'], row['pop_2020'], row['field']), axis=1
        )

        # Calculate percent rank
        gdf_tract['ac_per_rnk'] = utils.normalize_rank_percentile(
            gdf_tract['ac_per_post'].values,
            list_input_null_values=[-999],
            output_null_value=-999
        )

        print("Finished calculating RC factor AC: air conditioning.")

    def calculate_bikability(self):
        """
        Calculate bikability score.
        """
        # Load data
        df_bike_score = pd.read_csv(self.path_bike_score)
        gdf_tract = utils.get_blank_tract()

        # Merge bikability data with tract shapefile
        df_bike_score['BCT_txt'] = df_bike_score['BCT_txt'].astype(str)
        gdf_tract = gdf_tract.merge(df_bike_score[['BCT_txt', 'bikescore']], on='BCT_txt', how='left')

        # Fill missing values with the median
        gdf_tract['bikescore'].fillna(gdf_tract['bikescore'].median(), inplace=True)

        # Calculate score
        gdf_tract = self.calculate_kmeans(gdf_tract, data_column='bikescore')

        print("Finished calculating RCA factor: bikability.")

    def calculate_cooling_centers(self):
        #%% LOAD DATA
        gdf_cc = gpd.read_file(self.path_layer_cc)

        #%% calculate radial count using utility function
        gdf_tract = utils.calculate_radial_count(
            gdf_data=gdf_cc,
            column_key='NYCEM_ID',
            buffer_distance_ft=2640,  # 1/2 mile buffer
        )

        # fill nan with value 0
        gdf_tract.fillna(0, inplace=True)
        #%% calculate score
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Fraction_Covered')
        return gdf_tract
    
    def _distance_to_nearest(self, point, target_union):
        """
        Calculate the distance from a given point to the nearest geometry in a precomputed unary union.

        :param point: The point (Shapely geometry) for which to calculate the nearest distance.
        :param target_union: Precomputed unary union of all geometries in the target GeoDataFrame.
        :return: The distance to the nearest geometry.
        """
        # Find the nearest geometry and calculate the distance
        nearest_geom = nearest_points(point, target_union)[1]
        distance = point.distance(nearest_geom)

        return distance
    
    def calculate_emergency_medical_facility(self):
        #%% LOAD DATA
        gdf_hospital = gpd.read_file(self.path_hospital)
        gdf_tract = utils.get_blank_tract()

        #%% modify data
        gdf_hospital = utils.project_gdf(gdf_hospital)
        gdf_hospital['OBJECTID'] = np.arange(len(gdf_hospital))

        # Get centroids of tracts
        gdf_centroid = gdf_tract.copy()
        gdf_centroid['geometry'] = gdf_tract['geometry'].centroid

        # Calculate distances to hypothermia facilities
        subset_hypo = gdf_hospital[gdf_hospital['HYPOTHERMI'] == 1]
        hypothermia_union = subset_hypo['geometry'].unary_union
        gdf_tract['Distance_HYPO'] = gdf_centroid['geometry'].apply(
            lambda point: self._distance_to_nearest(point, hypothermia_union)
        )

        # Calculate distances to trauma facilities
        subset_trauma = gdf_hospital[gdf_hospital['TRAUMA'] == 1]
        trauma_union = subset_trauma['geometry'].unary_union
        gdf_tract['Distance_TRAUMA'] = gdf_centroid['geometry'].apply(
            lambda point: self._distance_to_nearest(point, trauma_union)
        )

        # Calculate distances to receiving facilities
        subset_receiving = gdf_hospital[gdf_hospital['RECEIVING'] == 1]
        receiving_union = subset_receiving['geometry'].unary_union
        gdf_tract['Distance_RECEIVING'] = gdf_centroid['geometry'].apply(
            lambda point: self._distance_to_nearest(point, receiving_union)
        )

        #%% write scores.  Set reverse=True because low distance values are better
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_HYPO', score_column='Score_WIW', reverse=True)
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_RECEIVING', score_column='Score_EXH', reverse=True)
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_TRAUMA', score_column='Score_CSW', reverse=True)
        gdf_tract['Score_ERQ'] = gdf_tract['Score_CSW']  # Distance to Trauma faciltiy
        gdf_tract['Score_CSF'] = gdf_tract['Score_CSW']  # Distance to Trauma faciltiy

        return gdf_tract

    def calculate_evacuation_potential(self):
        #%% LOAD DATA
        gdf_tract = utils.get_blank_tract()
        gdf_center = gpd.read_file(self.path_evacuation_centers)
        gdf_zone = gpd.read_file(self.path_evacauation_zone)

        # Project geospatial data
        gdf_center = utils.project_gdf(gdf_center)
        gdf_zone = utils.project_gdf(gdf_zone)

        #%%get centroid
        gdf_centroid = gdf_tract.copy()
        gdf_centroid['geometry'] = gdf_tract['geometry'].centroid

        #%% get for each pt get the nearest hospital for winter weather
        # Get the union of all geometries in gdf_center
        center_union = gdf_center.geometry.unary_union


        gdf_tract['Distance_Center'] = gdf_tract['geometry'].apply(
            lambda point: self._distance_to_nearest(point, center_union)
        )

        #%% write scores
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Distance_Center', score_column='Score', reverse=True)

        #%%assign 5 to everything in zone X of hurrican evac zone
        gdf_zone = gdf_zone.loc[gdf_zone.hurricane_ == 'X']
        gdf_tract_sjoin = gpd.sjoin(gdf_tract, gdf_zone, how='inner', predicate='within')
        gdf_tract_sjoin['Is_inland'] = 1
        gdf_tract = gdf_tract.merge(gdf_tract_sjoin[['BCT_txt', 'Is_inland']], how='left', on='BCT_txt')
        gdf_tract.loc[gdf_tract.Is_inland == 1, 'Score'] = 5

        return gdf_tract   
    
    def calculate_institution_experience(self):

        #%% LOAD DATA
        df_activation = pd.read_excel(self.path_activation, sheet_name='Summary')
        gdf_tract = utils.get_blank_tract()

        #%% open EOC activation spreadsheet
        print(df_activation.shape)

        #%% Get list of hazards and EOC activation keyword
        list_hazards = {'EXH': ['Heat'],
                        'WIW': ['Winter Weather'], 
                        'CSW': ['Coastal Storm'],  
                        'CSF': ['Coastal Storm', 'Flooding']}

        #%% Data preprocessing: Take only rows where CIMS TYPE is not na.
        df_activation = df_activation[df_activation['CIMS TYPE'].notna()]

        #%%
        df_count = pd.DataFrame(index=np.arange(len(self.list_abbrv)),
                                data={'abbrv': self.list_abbrv,
                                    'count_events': np.zeros(len(self.list_abbrv)),
                                    'count_days': np.zeros(len(self.list_abbrv))})

        #%% loop through each hazard to get count

        for abbrev in list_hazards.keys():
            keyword_list = list_hazards[abbrev]
            df_activation[abbrev] = df_activation['CIMS TYPE'].str.contains('|'.join(keyword_list))
            subset = df_activation[df_activation[abbrev]].copy()
            df_count.loc[df_count.abbrv == abbrev, 'count_events'] = len(subset)
            df_count.loc[df_count.abbrv == abbrev, 'count_days'] = subset.DURATION.sum()


        #%% calculate k-means cluster score
        df_count = utils.calculate_kmeans(df_count, 'count_days')

        #%% add results as score
        for abbrv in self.list_abbrv:
            gdf_tract['Score_{}'.format(abbrv)] = np.repeat(df_count.loc[df_count.abbrv == abbrv, 'Score'].values[0], len(gdf_tract))

        return gdf_tract

    def calculate_shelter_capacity(self):
        # Relevant input field names
        fn_long_term_capacity = 'Long_term_'  # URI 1.0 - "Long_term_capacity"

        #%% LOAD DATA
        gdf_tract = utils.get_blank_tract(add_pop=True)
        gdf_sc = gpd.read_file(self.path_layer_sc)
        gdf_sc = utils.project_gdf(gdf_sc)

        #%% modify tract
        gdf_tract['area_ft2'] = gdf_tract.geometry.area
        gdf_tract['pop_2020_density'] = gdf_tract['pop_2020'] / gdf_tract['area_ft2']

        # convert null to 0 values
        gdf_sc.fillna(value={fn_long_term_capacity: 0}, inplace=True)

        #%% allocate shelter beds to tracts based on population.
        #add column to count allocated shelter beds
        gdf_tract['LT_capacity_count'] = np.zeros(len(gdf_tract))
        #loop through each shelter and assign capacity to tracts
        for idx in gdf_sc.index:
            this_shelter = gdf_sc.loc[idx:idx, :].copy()
            this_capacity = this_shelter.at[idx, fn_long_term_capacity]

            # Buffer the shelter geometry
            this_shelter['geometry'] = this_shelter['geometry'].buffer(distance=self.buffer_radius)

            # Get intersecting tracts
            gdf_intersect = gpd.overlay(gdf_tract, this_shelter, how='intersection')

            # Calculate intersection areas and population
            gdf_intersect['area_ft2'] = gdf_intersect.geometry.area
            gdf_intersect['population'] = gdf_intersect['area_ft2'] * gdf_intersect['pop_2020_density']

            # Calculate capacity allocation for each intersecting tract
            gdf_intersect['capacity_allocation'] = (
                this_capacity * gdf_intersect['population'] / gdf_intersect['population'].sum()
            )

            # Aggregate capacity allocation by geoid and update the LT_capacity_count column in gdf_tract
            capacity_allocation_map = gdf_intersect.groupby('geoid')['capacity_allocation'].sum()
            gdf_tract['LT_capacity_count'] += gdf_tract['geoid'].map(capacity_allocation_map).fillna(0)

        #%% calculate capacity per 1000
        gdf_tract['capacity_allocation_per_1000'] = gdf_tract['LT_capacity_count'] * 1000. / gdf_tract['pop_2020']
        #set null values (with 0 population ) to 0
        gdf_tract.fillna(value={'capacity_allocation_per_1000': 0}, inplace=True)

        #%% calculate score
        #need to handle missing data
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='capacity_allocation_per_1000')
        return gdf_tract
    
    def calculate_transit_score(self):
        #%% LOAD DATA
        df_transit_score = pd.read_csv(self.pateh_walk_score)
        gdf_tract = utils.get_blank_tract()

        #%% modify walkscore and merge to tract shapefile
        temp = df_transit_score['BCT_txt']
        df_transit_score['BCT_txt'] = [str(x) for x in temp]
        gdf_tract = gdf_tract.merge(df_transit_score[['BCT_txt', 'transitscore']], on='BCT_txt', how='left')

        gdf_tract.fillna(gdf_tract['transitscore'].median(), inplace=True)

        #%% calculate score
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='transitscore')
        return gdf_tract
    
    def calculate_walk_score(self):
        #%% LOAD DATA
        df_walk_score = pd.read_csv(self.path_walk_score)
        gdf_tract = utils.get_blank_tract()

        #%% modify walkscore and merge to tract shapefile
        temp = df_walk_score['BCT_txt']
        df_walk_score['BCT_txt'] = [str(x) for x in temp]
        gdf_tract = gdf_tract.merge(df_walk_score[['BCT_txt', 'walkscore']], on='BCT_txt', how='left')

        gdf_tract.fillna(gdf_tract['walkscore'].median(), inplace=True)

        #%% calculate score
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='walkscore')
        return gdf_tract

# Example usage
if __name__ == "__main__":
    rca = RCA_RC()
    rca.calculate_ac()
    rca.calculate_bikability()