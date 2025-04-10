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
        # ...existing code from ESL_WIW_tree_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Replace hardcoded parameters with self.service_buffer
        # Save results to self.path_output_tree
        pass

    def calculate_snow_loss(self):
        # ...existing code from ESL_WIW_snow_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Save results to self.path_output_snow
        #%% tracts 
        gdf_tract = utils.get_blank_tract()

        #%%get costs based on 2018 dollars
        self.df_snow.index = np.arange(2007, 2024)
        self.df_snow['Snow Remove Cost'] = [utils.convert_USD(self.df_snow.at[idx, 'Snow Removal Cost'], idx) for idx in self.df_snow.index]
        ave_cost_year = self.df_snow['Snow Remove Cost'].mean() * 1000000

        #%% get length of road in each tract
        self.df_road.index = np.arange(len(self.df_road))
        self.df_road['BCT_txt'] = [str(self.df_road.at[idx, 'BCT_txt']) for idx in self.df_road.index]
        gdf_tract = gdf_tract.merge(self.df_road, on='BCT_txt', how='left')


        #%% distribute based on critical snow route length
        gdf_tract['Loss_USD'] = ave_cost_year * gdf_tract['Critical_Route_Length'] / gdf_tract['Critical_Route_Length'].sum()
        
        return

    def calculate_injury_loss(self):
        # ...existing code from ESL_WIW_injury_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Replace hardcoded parameters with self.loss_per_moderate_injury_2016 and self.loss_per_serious_injury_2016
        # Save results to self.path_output_injury
        pass

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
        df_hosp['Bor_ID'] = [self.df_borid.loc[self.df_borid.Borough==x, 'Bor_ID'].iloc[0] for x in df_hosp['Geography Name']]

        #%% get borough specific average
        df_hosp_mean = df_hosp.groupby('Bor_ID')['Y Value'].mean()  # average number of hospitilizations per year per 100,000 people for each borough
        bor_pop = self.gdf_tract.groupby('borocode')['pop_2020'].sum()  # total population of each borough
        bor_pop.index.name = 'Bor_ID'
        bor_pop.index = bor_pop.index.astype(int)
        hosp_rate = df_hosp_mean / 100000 * bor_pop  # total number of hospitalizations per year for each borough
        hosp_rate = hosp_rate / hosp_rate.sum()  # normalize to sum to 1 to get proportion of hospitalizations in each borough
        df_bor = N_deaths_year_NYC * hosp_rate / bor_pop  # death per person per year for each borough

        #  make a copy for gdf_tract
        gdf_tract = self.gdf_tract.copy()

        gdf_tract['N_deaths'] = self.gdf_tract.apply(lambda x: utils.calc_tract_deaths(
            gdf_tract=gdf_tract, 
            df_bor=df_bor,
            BCT_txt=x['BCT_txt'],
            ), 
        axis=1)

        #%% convert to loss
        loss_deaths_total = utils.convert_USD(self.loss_per_death, 2022)
        gdf_tract['Loss_USD'] = gdf_tract['N_deaths'] * loss_deaths_total

        # ...existing code from ESL_WIW_death_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Replace hardcoded parameters with self.loss_per_death
        # Save results to self.path_output_deaths
        pass

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
