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
        pass

    def calculate_injury_loss(self):
        # ...existing code from ESL_WIW_injury_loss_1.py...
        # Replace direct file paths with self.path_* attributes
        # Replace hardcoded parameters with self.loss_per_moderate_injury_2016 and self.loss_per_serious_injury_2016
        # Save results to self.path_output_injury
        pass

    def calculate_death_loss(self):
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
