""" Calculate earthquake-related losses using HAZUS data """

#%% read packages
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
from URI.PARAMS.params import PARAMS
utils.set_home()

class ESL_ERQ:
    def __init__(self):
        # Input paths
        self.path_erq_hazus = PATHNAMES.ESL_ERQ_hazus

        # Output paths
        self.path_output = PATHNAMES.ESL_ERQ_hazus_loss

        # Parameters
        self.ref_year = 2018  # Reference year for currency conversion

    def load_data(self):
        """Load the required data."""
        self.gdf_tract = utils.get_blank_tract(add_pop=True)
        self.df_hazus = gpd.read_file(self.path_erq_hazus)

    def calculate_hazus_loss(self):
        """Calculate earthquake-related losses."""
        # Merge HAZUS data with tract data
        self.gdf_tract = self.gdf_tract.merge(
            self.df_hazus[['tract', 'EconLoss']],
            left_on='geoid',
            right_on='tract',
            how='left'
        )

        # Convert to current USD
        self.gdf_tract['EconLoss'] = utils.convert_USD(self.gdf_tract['EconLoss'].values, self.ref_year)

        # Convert total loss to USD
        self.gdf_tract['Loss_USD'] = self.gdf_tract['EconLoss'] * 1000.0

        return self.gdf_tract

    def export_results(self):
        """Save results to output file and document them."""
        # Save as output
        self.gdf_tract.to_file(self.path_output)

        # Document result with a README
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(self.path_output)
            utils.write_readme(path_readme, text)
        except Exception as e:
            print(f"Error writing README: {e}")

        # Output complete message
        print("Finished calculating ERQ Building Damage.")

    def plot_results(self):
        """Plot the results."""
        plotting.plot_notebook(
            self.gdf_tract,
            column='Loss_USD',
            title='ERQ: Building Damage',
            legend='Loss USD',
            cmap='Greens',
            type='raw'
        )

if __name__ == "__main__":
    erq_esl = ESL_ERQ()
    erq_esl.load_data()
    erq_esl.calculate_loss()
    erq_esl.export_results()
    erq_esl.plot_results()