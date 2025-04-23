import numpy as np
import pandas as pd
import geopandas as gpd
import os
import datetime
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.settings as SETTINGS
from URI.PARAMS.params import PARAMS
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()




class WIW_ESL:
    def __init__(self):
        # Input paths
        self.path_tree = PATHNAMES.HHC_TreeServices
        self.path_events = PATHNAMES.stormevents_table
        self.path_event_types = PATHNAMES.HHC_eventtypes
        self.path_storm_event_types = PATHNAMES.HHC_stormeventtypes
        self.path_snow = PATHNAMES.ESL_WIW_snow_data
        self.path_road = PATHNAMES.ESL_WIW_road_cover
        self.path_hosp = PATHNAMES.ESL_WIW_hosp_data
        self.path_borid = PATHNAMES.Borough_to_FIP
        self.path_hosp_2016 = PATHNAMES.ESL_WIW_hosp_2016
        self.path_emerg = PATHNAMES.ESL_WIW_emerg_data
        self.path_emerg_2016 = PATHNAMES.ESL_WIW_emerg_2016
        self.path_deaths = PATHNAMES.ESL_WIW_deaths_data

        # Parameters
        self.service_buffer = HARDCODED.buffer_period_tree_servicing_days
        self.loss_per_moderate_injury_2016 = PARAMS['value_moderate_injury'].value
        self.loss_per_serious_injury_2016 = PARAMS['value_serious_injury'].value
        self.loss_per_death = PARAMS['value_of_stat_life'].value

        # Output paths
        self.path_output_tree = PATHNAMES.ESL_WIW_loss_tree
        self.path_output_snow = PATHNAMES.ESL_WIW_loss_snow
        self.path_output_injury = PATHNAMES.ESL_WIW_loss_injury
        self.path_output_deaths = PATHNAMES.ESL_WIW_loss_deaths

    def load_data(self):
        # Load dataframes from CSV and Excel files
        self.df_tree = pd.read_excel(self.path_tree, parse_dates=['DateInitiated', 'DateCreated'])
        self.df_events = pd.read_excel(self.path_events, parse_dates=['StartDate', 'EndDate'])
        self.df_event_types = pd.read_excel(self.path_event_types)
        self.df_storm_event_types = pd.read_excel(self.path_storm_event_types)
        self.df_snow = pd.read_excel(self.path_snow, sheet_name='Duplicate')
        self.df_road = pd.read_csv(self.path_road)
        self.df_hosp = pd.read_csv(self.path_hosp, skiprows=12, skipfooter=5, engine='python')
        self.df_borid = pd.read_excel(self.path_borid)
        self.df_hosp_2016 = pd.read_csv(self.path_hosp_2016, skiprows=6, skipfooter=17, engine='python')
        self.df_emerg = pd.read_csv(self.path_emerg, skiprows=12, skipfooter=5, engine='python')
        self.df_emerg_2016 = pd.read_csv(self.path_emerg_2016, skiprows=6, skipfooter=17, engine='python')
        self.df_deaths = pd.read_csv(self.path_deaths, skiprows=9, skipfooter=5, engine='python')

        # Load blank tract GeoDataFrame
        self.gdf_tract = utils.get_blank_tract(add_pop=True)

    def calculate_tree_loss(self):
        #%%  get hazard type id
        type_name = 'Winter Weather'
        type_id = self.df_event_types.loc[self.df_event_types.Name == type_name, 'Id'].values[0]

        #%% get all storm events ids with this hazard type
        df_EventsIds = self.df_events.copy()
        df_EventIds =self.df_storm_event_types.loc[self.df_storm_event_types.EventTypeId==type_id,:]
        df_EventIds.index = df_EventIds.StormEventId

        #%% get storm events with this id after 2000
        self.df_events.index = self.df_events.Id
        self.df_events['StartDate'] = pd.to_datetime(self.df_events['StartDate'])
        self.df_events['EndDate'] = pd.to_datetime(self.df_events['EndDate'])
        self.df_events = self.df_events.loc[df_EventIds.index, :]
        self.df_events = self.df_events.loc[self.df_events.StartDate >= datetime.datetime(year=2014, month=1, day=1), :]
        self.df_events = self.df_events.loc[self.df_events.EndDate < datetime.datetime(year=2024, month=1, day=1), :]

        #%% get tree service calls in this range
        self.df_tree['Is_Event'] = np.zeros(len(self.df_tree))
        self.df_tree['DateInitiated'] = pd.to_datetime(self.df_tree['DateInitiated'])
        for i, idx in enumerate(self.df_events.index):
            start_date = self.df_events.at[idx, 'StartDate']
            end_date = self.df_events.at[idx, 'EndDate'] + datetime.timedelta(days=self.service_buffer)
            self.df_tree.loc[((self.df_tree.DateInitiated >= start_date) & (self.df_tree.DateInitiated <= end_date)), 'Is_Event'] = 1

        #%%
        df_tree_1 = self.df_tree.loc[self.df_tree.Is_Event == 1,:]

        #%% only consider work orders
        df_tree_2 = df_tree_1.loc[((df_tree_1.HHCImportType != 0) & (df_tree_1.HHCImportType != 8)), :]

        #%% assume all work orders are 3500
        Loss_USD = len(df_tree_2) * 3500 / 10

        #%% plot distribution of tree services
        gdf_tree = gpd.GeoDataFrame(df_tree_2, geometry=gpd.points_from_xy(df_tree_2.Long, df_tree_2.Lat))
        gdf_tree = gdf_tree.loc[gdf_tree.Lat !=0, :]
        gdf_tree = gdf_tree.loc[gdf_tree.Long !=0, :]
        gdf_tree.crs = "EPSG:4326"
        gdf_tree = utils.project_gdf(gdf_tree)

        #%% get count per tract of tree services
        gdf_join = gpd.sjoin(gdf_tree, self.gdf_tract, how='left', predicate='within')
        gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
        df_count = gdf_join.pivot_table(index='BCT_txt', values=['Lat'], aggfunc=len)
        gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
        gdf_tract.fillna(value={'Lat': 0}, inplace=True)
        gdf_tract.rename(columns={"Lat":"Tree_Service_Count"}, inplace=True)

        #%% distribute losses weighted by the Tree Seri
        gdf_tract['Loss_USD'] = Loss_USD * gdf_tract['Tree_Service_Count'] / gdf_tract['Tree_Service_Count'].sum()

        return gdf_tract

    def calculate_snow_loss(self):
        #%%get costs based on 2018 dollars
        self.df_snow.index = np.arange(2007, 2024)
        self.df_snow['Snow Remove Cost'] = [utils.convert_USD(self.df_snow.at[idx, 'Snow Removal Cost'], idx) for idx in self.df_snow.index]
        ave_cost_year = self.df_snow['Snow Remove Cost'].mean() * 1000000

        #%% get length of road in each tract
        self.df_road.index = np.arange(len(self.df_road))
        self.df_road['BCT_txt'] = [str(self.df_road.at[idx, 'BCT_txt']) for idx in self.df_road.index]
        gdf_tract = self.gdf_tract.merge(self.df_road, on='BCT_txt', how='left')


        #%% distribute based on critical snow route length
        gdf_tract['Loss_USD'] = ave_cost_year * gdf_tract['Critical_Route_Length'] / gdf_tract['Critical_Route_Length'].sum()
        
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
    
    def calculate_injury_loss(self):
        # ...existing code from ESL_WIW_injury_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Replace hardcoded parameters with self.loss_per_moderate_injury_2016 and self.loss_per_serious_injury_2016
        # Save results to self.path_output_injury
        
        self.gdf_tract = self._calculate_tract_injury_rate(self.df_hosp, self.df_hosp_2016, self.gdf_tract, 'Hosp_per_100000')
        self.gdf_tract = self._calculate_tract_injury_rate(self.df_emerg, self.df_emerg_2016, self.gdf_tract, 'Emerg_per_100000')

        self.gdf_tract['N_emerg_uniq'] = self.gdf_tract['Emerg_per_100000'] - self.gdf_tract['Hosp_per_100000']  # unique emergency room visits
        self.gdf_tract['N_hosp'] = self.gdf_tract['Hosp_per_100000']  # hospitalizations

        loss_moderate_total = utils.convert_USD(self.loss_per_moderate_injury_2016, 2016)  # convert to 2022 dollars
        loss_serious_total = utils.convert_USD(self.loss_per_serious_injury_2016, 2016)  # convert to 2022 dollars
        self.gdf_tract['Loss_USD'] = self.gdf_tract['N_hosp'] * loss_serious_total + self.gdf_tract['N_emerg_uniq'] * loss_moderate_total  # total loss in USD
        
        return self.gdf_tract


    def calculate_death_loss(self):
        #%% get average number per year across NYC of load deaths
        N_deaths_year_NYC = self.df_deaths['Y Value'].mean()

        #%% load hospitalizations.
        # Assume that deaths are by borough same as the age-adjusted hospitalization rate
        # note it would be better to use unadjusted hospitalization rate, but that is available for only one year
        # so may be too noisy

        # remove NYC-level data
        df_hosp = self.df_hosp.loc[self.df_hosp['Geography Name'] != 'New York City', :]

        #%% add borough code to hosp data
        df_hosp['borocode'] = df_hosp.apply(lambda x: utils.get_borough_code(x), axis=1)  # add borough code to hosp data

        #%% get borough specific average
        df_hosp_mean = df_hosp.groupby('borocode')['Y Value'].mean()  # average number of hospitilizations per year per 100,000 people for each borough
        bor_pop = self.gdf_tract.groupby('borocode')['pop_2020'].sum()  # total population of each borough
        bor_pop.index.name = 'borocode'
        bor_pop.index = bor_pop.index.astype(int)
        hosp_rate = df_hosp_mean / 100000 * bor_pop  # total number of hospitalizations per year for each borough
        hosp_rate = hosp_rate / hosp_rate.sum()  # normalize to sum to 1 to get proportion of hospitalizations in each borough
        df_bor = N_deaths_year_NYC * hosp_rate / bor_pop  # death per person per year for each borough

        #  make a copy for gdf_tract
        gdf_tract = self.gdf_tract.copy()

        gdf_tract['N_deaths'] = gdf_tract.apply(lambda x: utils.calc_tract_deaths(
            gdf_tract=gdf_tract, 
            df_bor=df_bor,
            BCT_txt=x['BCT_txt'],
            ), 
        axis=1)

        #%% convert to loss
        loss_deaths_total = utils.convert_USD(self.loss_per_death, 2022)
        gdf_tract['Loss_USD'] = gdf_tract['N_deaths'] * loss_deaths_total

        return gdf_tract

    def export_results(self, gdf, path_output, title):
        # Save results and document with a README
        gdf.to_file(path_output)
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(path_output)
            utils.write_readme(path_readme, text)
        except:
            pass
        print(f"Finished calculating {title}.")

    def plot_results(self, gdf, column, title):
        plotting.plot_notebook(gdf, column=column, title=title, legend='Loss USD', cmap='Greens', type='raw')

if __name__ == "__main__":
    wiw_esl = WIW_ESL()
    wiw_esl.load_data()
    wiw_esl.calculate_tree_loss()
    wiw_esl.calculate_snow_loss()
    wiw_esl.calculate_injury_loss()
    wiw_esl.calculate_death_loss()
