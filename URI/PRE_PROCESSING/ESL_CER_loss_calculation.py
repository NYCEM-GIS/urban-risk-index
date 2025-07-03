""" calculate CER losses due to ecosystem degradation """

import numpy as np
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
from URI.PARAMS.params import PARAMS

utils.set_home()

class ESL_CER:
    def __init__(self):
        # Input paths
        self.path_shoreline = PATHNAMES.ESL_CER_CEHA_length

        # Parameters
        self.value_per_ft2 = PARAMS['value_per_acre_marine'].value / 43560.0
        self.list_locations = [
            'Rockaway_East', 'Rockaway_West', 'Rockaway_Middle',
            'Coney_Island',
            'Annandale_Staten_Island', 'Oakwood_Beach_Staten_Island', 'South_Shore_Staten_Island'
        ]
        self.dict_erosion_rate_ft_yr = {
            loc: PARAMS[f'erosion_rate_{loc}_ft_yr'].value for loc in self.list_locations
        }

        # Output paths
        self.path_output = PATHNAMES.ESL_CER_ecosystem_loss

    def load_data(self):
        self.gdf_shoreline = gpd.read_file(self.path_shoreline)
        self.gdf_tract = utils.get_blank_tract()

    def calculate_erosion_rate(self):
        # Assign erosion rates to shoreline data
        self.gdf_shoreline['erosion_rate_ft_yr'] = [
            self.dict_erosion_rate_ft_yr.get(zone, 0) for zone in self.gdf_shoreline['CER_Zone']
        ]

        # Merge shoreline data with tract data
        self.gdf_tract = self.gdf_tract[['BCT_txt', 'geometry']].merge(
            self.gdf_shoreline.drop(columns='geometry'),
            left_on='BCT_txt',
            right_on='BOROCT',
            how='left'
        )

        # Set erosion rate and length to 0 for all other tracts
        self.gdf_tract.fillna(value={'erosion_rate_ft_yr': 0, 'Shape_Leng': 0}, inplace=True)

        return self.gdf_tract

    def calculate_loss(self):
        # Convert value per ft² to 2019 dollars
        value_per_ft2_2019 = utils.convert_USD(self.value_per_ft2, 2016)

        # Calculate eroded area over 100 years and associated loss
        self.gdf_tract['Eroded_area_ft2_years'] = (
            np.arange(1, 101).sum() * self.gdf_tract['erosion_rate_ft_yr'] * self.gdf_tract['Shape_Leng']
        )
        self.gdf_tract['shoreline_value_lost'] = (
            self.gdf_tract['Eroded_area_ft2_years'] * value_per_ft2_2019
        )
        # Annualize loss
        self.gdf_tract['Loss_USD'] = self.gdf_tract['shoreline_value_lost'] / 100.0

        return self.gdf_tract

    def export_results(self):
        # Save results to file
        self.gdf_tract.to_file(self.path_output)

        # Document result with a readme
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(self.path_output)
            utils.write_readme(path_readme, text)
        except Exception as e:
            print(f"Error writing README: {e}")

    def plot_results(self):
        # Plot results
        plotting.plot_notebook(
            self.gdf_tract,
            column='Loss_USD',
            title='CER: Ecosystem Loss',
            legend='Loss USD',
            cmap='Greens',
            type='raw'
        )

if __name__ == "__main__":
    cer_esl = ESL_CER()
    cer_esl.load_data()
    cer_esl.calculate_erosion_rate()
    cer_esl.calculate_loss()
    cer_esl.export_results()
    cer_esl.plot_results()
    print("Finished calculating CER ecosystem loss.")