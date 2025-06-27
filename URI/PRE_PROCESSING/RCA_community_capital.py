#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
from census import Census
from us import states
import requests
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()


class RCA_CC:
    def __init__(self):
        #%% EXTRACT PARAMETERS
        self.gdf_buffer = gpd.GeoDataFrame()
        # Input paths
        self.path_community_infrastructure = PATHNAMES.RCA_CC_community_infrastructure_raw
        self.path_emergencty_operations = PATHNAMES.RCA_CC_EO_locations
        self.path_political_engagement = PATHNAMES.RCA_CC_PE_data
        self.path_boro_fip = PATHNAMES.Borough_to_FIP
        # Output paths
        self.path_results_community_infrastructure = PATHNAMES.RCA_CC_CI_score
        self.path_results_emergency_operations = PATHNAMES.RCA_CC_EO_score
        self.path_results_place_attachment = PATHNAMES.RCA_CC_PA_score
        self.path_results_political_engagement = PATHNAMES.RCA_CC_PE_score

    def calculate_community_infrastructure(self):
        #%% LOAD DATA
        gdf_tract = utils.get_blank_tract()
        gdf_data = gpd.read_file(self.path_community_infrastructure)  # community centers

        #%% tract data
        gdf_data = utils.project_gdf(gdf_data)
        gdf_data['OBJECTID'] = gdf_data.index
        gdf_tract['area_ft2'] = gdf_tract['geometry'].area

        #%% make shapefile with 1/2 mile radius
        gdf_buffer = gdf_data.copy()
        gdf_buffer['geometry'] = gdf_data['geometry'].buffer(distance=5280/2)

        #%% calculate intersections in a vectorized way
        gdf_intersect = gpd.overlay(gdf_tract, gdf_buffer[['OBJECTID', 'geometry']], how='intersection')
        gdf_intersect['area_intersect_ft2'] = gdf_intersect['geometry'].area
        gdf_intersect['Fraction_Covered'] = np.minimum(gdf_intersect['area_intersect_ft2'] / gdf_intersect['area_ft2'], 1.0)

        #%% group by 'BCT_txt' and calculate the sum
        df_fill = gdf_intersect[['BCT_txt', 'Fraction_Covered']].groupby('BCT_txt', as_index=False).sum()

        #%% get the sum  by tract and join
        df_sum = df_fill.groupby(by='BCT_txt').sum()
        gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')

        # fill nan with value 0
        gdf_tract.fillna(0, inplace=True)

        #%% calculate score
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Fraction_Covered')

        return gdf_tract
    
    def calculate_emergency_operations(self):
        #%% LOAD DATA
        df_events = pd.read_csv(self.path_emergencty_operations)

        #%% open education and outreach points
        # create point map with lat and lon
        gdf_events = gpd.GeoDataFrame(df_events, geometry=gpd.points_from_xy(df_events.Longitude, df_events.Latitude),
                                      crs=4326)
        gdf_events['Event_ID'] = np.arange(len(gdf_events))
        gdf_events = utils.project_gdf(gdf_events)
        # drop na values
        gdf_events.dropna(subset=['Latitude', 'Longitude'], inplace=True)

        #%% get count from tract
        gdf_tract = utils.calculate_radial_count(gdf_events, column_key='Event_ID', buffer_distance_ft=2640)

        #%% calculate score with kmeans clustering
        gdf_result = utils.calculate_kmeans(gdf_tract, data_column='Fraction_Covered')

        return gdf_result
    
    def calculate_place_attachment(self):
        #%% LOAD DATA
        gdf_tract = utils.get_blank_tract()
        session = requests.Session()
        session.verify = False
        c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8", session=session)

        #%% place attachment data
        response_pop_older_1yr = c.acs5.state_county_tract('B07204_001E', states.NY.fips, '*', Census.ALL)
        response_same_house_1yr_ago = c.acs5.state_county_tract('B07204_002E', states.NY.fips, '*', Census.ALL)
        response_diff_house_same_city_1yr_ago = c.acs5.state_county_tract('B07204_005E', states.NY.fips, '*', Census.ALL)
        list_tract1 = [x['tract'] for x in response_pop_older_1yr]
        list_state = [x['state'] for x in response_pop_older_1yr]
        list_county = [x['county'] for x in response_pop_older_1yr]
        list_pop_older_1yr = [x['B07204_001E'] for x in response_pop_older_1yr]
        list_tract2 = [x['tract'] for x in response_same_house_1yr_ago]
        list_same_house_1yr_ago = [x['B07204_002E'] for x in response_same_house_1yr_ago]
        list_tract3 = [x['tract'] for x in response_same_house_1yr_ago]
        list_diff_house_same_city_1yr_ago = [x['B07204_005E'] for x in response_diff_house_same_city_1yr_ago]


        #%%
        df = pd.DataFrame(
            index=np.arange(len(list_tract1)),
            data={'pop_older_1yr': list_pop_older_1yr,
                'same_house_1yr_ago': list_same_house_1yr_ago,
                'diff_house_same_city_1yr_ago': list_diff_house_same_city_1yr_ago,
                'tract': list_tract1,
                'county': list_county,
                'state': list_state}
        )
        df['Stfid'] = [df.loc[x, "state"] + df.loc[x, 'county']+df.loc[x, 'tract'] for x in df.index]

        #%% merge
        gdf_tract = gdf_tract.merge(df[['pop_older_1yr', 'Stfid', 'same_house_1yr_ago', 'diff_house_same_city_1yr_ago']], left_on='geoid', right_on='Stfid', how='inner')

        #%%
        gdf_tract['percent_living_in_NY_over_1yr'] = (gdf_tract['same_house_1yr_ago'] + gdf_tract['diff_house_same_city_1yr_ago'])/gdf_tract['pop_older_1yr'] * 100.
        # set missing values to median
        gdf_tract.fillna(gdf_tract['percent_living_in_NY_over_1yr'].median(), inplace=True)

        #%% xconvert to score 1-5
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='percent_living_in_NY_over_1yr', n_cluster=5)

        return gdf_tract
    
    def calculate_political_engagement(self):
        #%% LOAD DATA
        df_data = pd.read_excel(self.path_political_engagement)
        df_fips = pd.read_excel(self.path_boro_fip)


        #%% place attachment data
        df_data.dropna(inplace=True, subset=['Census Tract', 'Avg. Participation Score 2018']) #due to missing census tract number in data
        df_data['FIPS_CT_txt'] = [str(int(df_data.at[idx, 'Census Tract'])) for idx in df_data.index]

        #%% tract data
        gdf_tract = utils.get_blank_tract()

        #%% fips data
        df_fips['Bor_ID_str'] = [str(df_fips.at[idx, 'Bor_ID']) for idx in df_fips.index]
        df_fips['FIPS_mod'] = ['3600' + df_fips.at[idx, 'Bor_ID_str'] for idx in df_fips.index]

        #add fips id number
        gdf_tract = gdf_tract.merge(df_fips, left_on='borocode', right_on='Bor_ID_str', how='left')
        gdf_tract['FIPS_CT_txt'] = [str(gdf_tract.at[idx, 'FIPS_mod']) + gdf_tract.at[idx, 'BCT_txt'][1:] for idx in gdf_tract.index]

        #%% merge displacement score
        gdf_tract = gdf_tract.merge(df_data[['FIPS_CT_txt', 'Avg. Participation Score 2018']], left_on='FIPS_CT_txt', right_on='FIPS_CT_txt', how='left')

        #%% fill na value with median voter participation score
        values = {'Avg. Participation Score 2018': gdf_tract['Avg. Participation Score 2018'].median()}
        gdf_tract.fillna(value=values, inplace=True)

        #%% reclassify to score 1-5
        bins = [-np.inf, 21.8, 26.8, 31.6, 37.9, np.inf]
        labels = [1, 2, 3, 4, 5]
        gdf_tract['Score'] = pd.cut(gdf_tract['Avg. Participation Score 2018'], bins=bins, labels=labels).astype(int)

        return gdf_tract[['BCT_txt', 'Score']].copy()
            