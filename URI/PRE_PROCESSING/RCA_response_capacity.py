import geopandas as gpd
import pandas as pd
import os
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
        gdf_tract = self.calculate_kmeans(gdf_tract, data_column='ac_per_rnk')

        # Save results
        self.export_results(gdf_tract, self.path_results_ac, key='ac')

        # Plot results
        self.plot_notebook(
            gdf_tract, column='Score', title='RCA_RC_AC: Air Conditioning',
            legend='Score', cmap='Blues', plot_type='score'
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