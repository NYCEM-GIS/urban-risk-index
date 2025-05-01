import pandas as pd
import geopandas as gpd
import numpy as np
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
from URI.PARAMS.params import PARAMS
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()

class ESL_EXH:
    def __init__(self):
        
        # Consolidated constants
        self.path_population_tract = PATHNAMES.population_by_tract
        self.path_ecostress = PATHNAMES.ESL_EXH_ecostress_2020
        self.path_stormevents = PATHNAMES.stormevents_table
        self.path_stormeventsboroughs = PATHNAMES.stormeventsboroughs_table
        self.path_hosp = PATHNAMES.ESL_EXH_hosp_data
        self.path_emerg = PATHNAMES.ESL_EXH_emerg_data
        self.path_hosp_2016 = PATHNAMES.ESL_EXH_hosp_2016
        self.path_emerg_2016 = PATHNAMES.ESL_EXH_emerg_2016
        self.value_life = PARAMS['value_of_stat_life'].value
        self.yearly_outage = PARAMS['EXH_outage_person_hrs_per_year'].value
        self.loss_outage_hr = PARAMS['loss_day_power'].value / 24.
        self.loss_per_moderate_injury_2016 = PARAMS['value_moderate_injury'].value
        self.loss_per_serious_injury_2016 = PARAMS['value_serious_injury'].value
        self.deaths_year = PARAMS['EXH_deaths_per_year'].value
        self.start_date = HARDCODED.heat_event_count_start_date
        self.end_date = HARDCODED.heat_event_count_end_date

        # export directory
        self.path_results_injury = PATHNAMES.ESL_EXT_loss_injury
        self.path_results_death = PATHNAMES.EXH_ESL_deaths_per_year_tract
        self.path_results_power = PATHNAMES.ESL_EXH_loss_power

    def _join_ecostress(self, gdf_tract:gpd.GeoDataFrame, pop_field: str) -> gpd.GeoDataFrame:
        # Read Ecostress data
        df_ecostress = pd.read_csv(self.path_ecostress)
        df_ecostress['boroct2020'] = df_ecostress['boroct2020'].astype(str)

        gdf_tract = gdf_tract.merge(df_ecostress[['boroct2020', 'PCT90']], left_on='BCT_txt', right_on='boroct2020', how='inner')

        gdf_tract['ecostress_rank'] = utils.normalize_rank_percentile(
            gdf_tract['PCT90'].values,
            list_input_null_values=[-999],
            output_null_value=-999
        )
        gdf_tract['Weighting_Factor'] = gdf_tract['ecostress_rank'] * gdf_tract[pop_field]

        return gdf_tract
    
    def _calculate_tract_injury_rate(self, df:pd.DataFrame, df_2016:pd.DataFrame, gdf_tract:gpd.GeoDataFrame,metric:str) -> gpd.GeoDataFrame:

        #%% load hospitalizations or emergency visits.  These are the most severe injuries
        # keep only the borough estimates
        df = df.loc[df['Geography Name'] != 'New York City', :]

        #%% add borough code to dataframe
        df['borocode'] = df['Geography Name'].apply(lambda x: utils.get_borough_code(x))

        #%% get borough specific average
        df_bor = df[['borocode', 'Y Value']].groupby('borocode').mean()

        #%% open 2016 data to convert from age-adjusted to annual rate
        df_2016['ratio'] = df_2016['Estimated Annual Rate (per 100,000 residents)'] /  df_2016['Age-Adjusted Rate (per 100,000 residents)']
        df_2016['borocode'] = df_2016['Borough'].apply(lambda x: utils.get_borough_code(x))

        df_bor = pd.merge(df_bor, df_2016, on='borocode', how='left')

        df_bor["boro_" + metric] = df_bor['Y Value'] * df_bor['ratio']

        # Pre-merge gdf_tract with df_bor to simplify calculations
        df_bor['borocode'] = df_bor['borocode'].astype(str)
        gdf_tract = gdf_tract.merge(df_bor[["borocode", "boro_" + metric]], on='borocode', how='left')

        # %% calculate tract level hops and emerg rates
        gdf_tract[metric] = gdf_tract['boro_' + metric] * gdf_tract['pop_2020'] / 100000.  # number of hops per year for each tract

        gdf_tract.drop(columns=['boro_' + metric], inplace=True)  # drop unnecessary columns
        return gdf_tract
    
    def calculate_power_loss(self):
        yearly_loss = self.yearly_outage * self.loss_outage_hr

        gdf_tract = utils.get_blank_tract(add_pop=True)
        # append ecostress data to gdf_tract
        gdf_tract = self._join_ecostress(gdf_tract, 'pop_2020')

        pop_total_weighted = gdf_tract['Weighting_Factor'].sum()
        gdf_tract['Loss_2016'] = yearly_loss * gdf_tract['Weighting_Factor'] / pop_total_weighted
        gdf_tract['Loss_USD'] = utils.convert_USD(gdf_tract['Loss_2016'], 2016).values
        gdf_tract['BCT_txt'] = gdf_tract['BCT_txt'].astype(str)

        return gdf_tract


    
    def calculate_injury_loss(self):
        # Load hospitalization and emergency visit data
        df_hosp = pd.read_csv(self.path_hosp, skiprows=14, skipfooter=5, engine='python')
        df_hosp_2016 = pd.read_csv(self.path_hosp_2016, skiprows=6, skipfooter=23, engine='python')
        df_emerg = pd.read_csv(self.path_emerg, skiprows=14, skipfooter=5, engine='python')
        df_emerg_2016 = pd.read_csv(self.path_emerg_2016, skiprows=6, skipfooter=23, engine='python')

    
        gdf_tract = utils.get_blank_tract(add_pop=True)
        gdf_tract = self._join_ecostress(gdf_tract, 'pop_2020')

        gdf_tract = self._calculate_tract_injury_rate(df_hosp, df_hosp_2016, gdf_tract, 'Hosp_per_100000')
        gdf_tract = self._calculate_tract_injury_rate(df_emerg, df_emerg_2016, gdf_tract, 'Emerg_per_100000')

        gdf_tract['N_emerg_uniq'] = gdf_tract['Emerg_per_100000'] - gdf_tract['Hosp_per_100000']  # unique emergency room visits
        gdf_tract['N_hosp'] = gdf_tract['Hosp_per_100000']  # hospitalizations

        loss_moderate_total = utils.convert_USD(self.loss_per_moderate_injury_2016, 2016)  # convert to 2022 dollars
        loss_serious_total = utils.convert_USD(self.loss_per_serious_injury_2016, 2016)  # convert to 2022 dollars
        gdf_tract['Loss_USD'] = (gdf_tract['N_hosp'] * loss_serious_total + gdf_tract['N_emerg_uniq'] * loss_moderate_total) * gdf_tract['Weighting_Factor']  # total loss in USD
        
        return gdf_tract

    def calculate_death_loss(self):
        df_stormevents = pd.read_excel(self.path_stormevents)
        df_stormeventsboroughs = pd.read_excel(self.path_stormeventsboroughs)
        gdf_tract = utils.get_blank_tract(add_pop=True)
        # Filter storm events for heat events within the date range
        df_stormevents['StartDate'] = pd.to_datetime(df_stormevents['StartDate'])
        df_stormevents['EndDate'] = pd.to_datetime(df_stormevents['EndDate'])
        df_stormevents = df_stormevents[
            (df_stormevents['StartDate'] > self.start_date) &
            (df_stormevents['EndDate'] < self.end_date) &
            (df_stormevents['Name'].str.contains('Heat'))
        ]

        # Count heat events per borough directly using groupby
        df_borcount = (
            df_stormeventsboroughs[df_stormeventsboroughs['StormEventId'].isin(df_stormevents['Id'])]
            .groupby('BoroughId')
            .size()
            .reindex(range(1, 6), fill_value=0)
            .to_frame(name='Heat_Events_Per_Year')
        )

        n_years = (self.end_date - self.start_date).days / 365.25
        df_borrate = df_borcount / n_years
        df_borrate.index = [str(x) for x in df_borrate.index]

        gdf_events_per_year = pd.merge(gdf_tract, df_borrate, left_on='borocode', right_index=True, how='inner')


        # Calculate borough population proportions
        df_population_borough = gdf_tract.groupby('borocode')['pop_2020'].sum()
        citywide_population = df_population_borough.sum()
        df_population_borough_proportion = df_population_borough / citywide_population

        # Allocate deaths per year to boroughs based on population proportion
        df_borrate['deaths_year_borough'] = self.deaths_year * df_population_borough_proportion

        # Merge borough death rates with tract data
        gdf_deaths_per_event = gdf_events_per_year.merge(
            df_borrate[['deaths_year_borough']],
            left_on='borocode',
            right_index=True,
            how='left'
        )

        # Calculate deaths per event for each borough
        gdf_deaths_per_event['deaths_per_event_boro'] = (
            gdf_deaths_per_event['deaths_year_borough'] / gdf_deaths_per_event['Heat_Events_Per_Year']
        )

        # Calculate deaths per event for each tract
        # Calculate tract to borough population proportion
        gdf_deaths_per_event['tract_to_borough_pop_proportion'] = (
            gdf_deaths_per_event['pop_2020'] / gdf_deaths_per_event.groupby('borocode')['pop_2020'].transform('sum')
        )

        # Calculate deaths per event for each tract
        gdf_deaths_per_event['deaths_per_event'] = (
            gdf_deaths_per_event['deaths_per_event_boro'] * gdf_deaths_per_event['tract_to_borough_pop_proportion']
        )
        # # bring in ecostress data
        gdf_deaths_per_event = self._join_ecostress(gdf_deaths_per_event, 'pop_2020')

        gdf_deaths_per_event['deaths_per_event_weighted'] = gdf_deaths_per_event['deaths_per_event'] * gdf_events_per_year['Weighting_Factor']
        gdf_loss = gdf_events_per_year.merge(gdf_deaths_per_event.drop(columns='geometry'), on='BCT_txt', how='left')
        gdf_loss['deaths_year'] = gdf_loss['Heat_Events_Per_Year'] * gdf_loss['deaths_per_event_weighted']
        gdf_loss['Loss_USD'] = gdf_loss['deaths_year'] * self.value_life

        return gdf_events_per_year