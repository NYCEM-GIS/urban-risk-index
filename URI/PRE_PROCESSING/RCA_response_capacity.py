import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.ops import nearest_points

import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()

class RCA_RC:
    def __init__(self):
        self.results = {}
        # Extract parameters
        self.path_ac = PATHNAMES.RCA_RC_ACH_raw
        self.path_ac_taskforce = PATHNAMES.RCA_RC_AC_ac_taskforce
        self.path_results_ac = PATHNAMES.RCA_RC_AC_score
        self.path_bike_score = PATHNAMES.RCA_RC_WA_walkscore_csv
        self.path_results_bike = PATHNAMES.RCA_RC_BI_score
        self.path_layer_cc = PATHNAMES.RCA_RC_CC_layer
        self.path_results_cooling = PATHNAMES.RCA_RC_CC_score
        # Input paths
        self.path_hospital = PATHNAMES.RCA_RC_EMA_raw
        # Output paths
        self.path_results_emergency_medical_facility = PATHNAMES.RCA_RC_EM_score
        self.path_evacuation_centers = PATHNAMES.RCA_RC_EP_raw
        self.path_evacauation_zone = PATHNAMES.RCA_RC_EP_evac_zones
        # Output paths
        self.path_evacuation_potential = PATHNAMES.RCA_RC_EP_score

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
        gdf_tract = utils.get_blank_tract()
        gdf_cc = gpd.read_file(self.path_layer_cc)

        #%% modify tract
        gdf_tract['area_ft2'] = gdf_tract.geometry.area

        #%%  add 1/2 mile buffer
        gdf_cc_buffer = gdf_cc.copy()
        gdf_cc_buffer['geometry'] = gdf_cc['geometry'].buffer(distance=5280/2.)

        #%% create empty df to fill
        df_fill = pd.DataFrame(columns=['BCT_txt', 'Fraction_Covered'])

        #%% loop through each buffer, and add BCT_txt and area filled to list
        for i, idx in enumerate(gdf_cc_buffer.index):
            this_buffer = gdf_cc_buffer.loc[[idx]]
            # take intersection
            this_intersect = gpd.overlay(gdf_tract, this_buffer[['NYCEM_ID', 'geometry']], how='intersection')
            this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
            this_intersect['Fraction_Covered'] = np.minimum(this_intersect['area_intersect_ft2'] / this_intersect['area_ft2'], 1.0)
            # add to df_fill
            df_fill = pd.concat([df_fill, this_intersect[['BCT_txt', 'Fraction_Covered']]])


        #%% get the sum  by tract and join
        df_sum = df_fill.groupby(by='BCT_txt').sum()
        gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')

        # fill nan with value 0
        gdf_tract.fillna(0, inplace=True)

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
    
    def calculate_kmeans(self, gdf, data_column):
        """
        Apply k-means clustering to a GeoDataFrame column.
        """
        return utils.calculate_kmeans(gdf, data_column=data_column)

    def export_results(self, gdf, path_results, key):
        """
        Export GeoDataFrame results to a file and store them in the results dictionary.
        """
        gdf.to_file(path_results)
        self.results[key] = gdf
        print(f"Results for {key} saved to {path_results}")

    def plot_notebook(self, gdf, column, title, legend, cmap, plot_type):
        """
        Plot results in a Jupyter Notebook.
        """
        plotting.plot_notebook(
            gdf, column=column, title=title, legend=legend, cmap=cmap, type=plot_type
        )
# Example usage
if __name__ == "__main__":
    rca = RCA_RC()
    rca.calculate_ac()
    rca.calculate_bikability()