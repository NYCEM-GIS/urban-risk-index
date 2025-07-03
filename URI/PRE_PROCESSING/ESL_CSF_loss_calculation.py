""" calculate various losses due to coastal storms """

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.settings as SETTINGS
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.hardcoded as HARDCODED
utils.set_home()

class CSF_ESL:
    def __init__(self):
        # Input paths
        self.path_dot = PATHNAMES.ESL_CST_dot_table
        self.path_cst_loss = PATHNAMES.ESL_FLD_hazus_loss
        self.path_flood_bronx = PATHNAMES.ESL_CSF_hazus_bronx
        self.path_flood_kings = PATHNAMES.ESL_CSF_hazus_kings
        self.path_flood_manhattan = PATHNAMES.ESL_CSF_hazus_manhattan
        self.path_flood_queens = PATHNAMES.ESL_CSF_hazus_queens
        self.path_flood_richmond = PATHNAMES.ESL_CSF_hazus_richmond

        # Settings
        self.ref_year = SETTINGS.target_year

        # Parameters
        self.ave_displacement_days = HARDCODED.average_duration_CST_displacement_days
        self.val_nyc_night_lodging = PARAMS['cost_nyc_night_lodging'].value
        self.val_nyc_per_diem = PARAMS['cost_nyc_per_diem'].value
        self.val_nyc_home_meal_per_day = PARAMS['cost_nyc_home_meals_per_day'].value
        self.ave_persons_per_residence = PARAMS['ave_persons_per_residence'].value

        # Output paths
        self.path_output_transportation = PATHNAMES.ESL_CST_loss_transportation
        self.path_output_dislocation = PATHNAMES.ESL_CST_dislocation_loss
        self.path_output_hazus = PATHNAMES.ESL_FLD_hazus_loss

    def load_data(self):
        self.gdf_tract = utils.get_blank_tract(add_pop=True)
        self.df_dot = pd.read_excel(self.path_dot, sheet_name='Major Storm Events', skiprows=2, skipfooter=4, index_col=0)
        self.gdf_fld = gpd.read_file(self.path_cst_loss)
        self.gdf_flood_bronx = gpd.read_file(self.path_flood_bronx)
        self.gdf_flood_kings = gpd.read_file(self.path_flood_kings)
        self.gdf_flood_manhattan = gpd.read_file(self.path_flood_manhattan)
        self.gdf_flood_queens = gpd.read_file(self.path_flood_queens)
        self.gdf_flood_richmond = gpd.read_file(self.path_flood_richmond)

    def combine_flood_data(self, column_name):
        gdf_flood_data_list = [
            self.gdf_flood_bronx, 
            self.gdf_flood_kings, 
            self.gdf_flood_manhattan, 
            self.gdf_flood_queens, 
            self.gdf_flood_richmond,
        ]
        gdf_flood_data_by_tract_list = []

        for fld_file in gdf_flood_data_list:
            fld_file['tract'] = fld_file['block'].str[0:11]  # Tract ID is equal to the first 11 digits of the block id
            fld_file_by_tract = fld_file[['tract', column_name, 'geometry']].dissolve(by='tract', as_index=False, aggfunc='sum')
            gdf_flood_data_by_tract_list.append(fld_file_by_tract)

        gdf_flood = gpd.GeoDataFrame(pd.concat(gdf_flood_data_by_tract_list, ignore_index=True))
        return gdf_flood

    def export_results(self, gdf, path_output, title):
        # save as output
        gdf.to_file(path_output)

        # document result with readme
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(path_output)
            utils.write_readme(path_readme, text)
        except:
            pass

        # output complete message
        print(f"Finished calculating {title}.")

    def plot_results(self, gdf, column, title):
        plotting.plot_notebook(gdf, column=column, title=title, legend='Loss USD', cmap='Greens', type='raw')

    def calculate_transportation_loss(self):
        # calculate annual loss
        dot_loss_tot = [utils.convert_USD(x, self.ref_year) for x in self.df_dot.loc['Total Costs', :].values]
        dot_loss_ave = np.average(dot_loss_tot)

        # distribute loss according to flood damage
        self.gdf_tract = self.gdf_tract.merge(self.gdf_fld[['BCT_txt', 'Loss_USD']], on='BCT_txt', how='inner')
        self.gdf_tract.rename(columns={"Loss_USD":"weight"}, inplace=True)
        self.gdf_tract['Loss_USD'] = dot_loss_ave * self.gdf_tract['weight'] / self.gdf_tract['weight'].sum()

    def calculate_dislocation_loss(self):
        # Flood Data Preprocessing
        gdf_flood = self.combine_flood_data('DisplacedP')

        # Displacement cost = cost of lodging and food minus average daily cost of food at home for duration of displacement per person
        gdf_flood['Loss_USD'] = gdf_flood['DisplacedP'] * self.ave_displacement_days * (self.val_nyc_night_lodging/self.ave_persons_per_residence + self.val_nyc_per_diem - self.val_nyc_home_meal_per_day)

        # merge with tracts
        self.gdf_tract = self.gdf_tract.merge(gdf_flood[['tract', 'Loss_USD']], left_on='geoid', right_on=['tract'], how='left')
        self.gdf_tract['Loss_USD'] = self.gdf_tract['Loss_USD'].fillna(0)

    def calculate_hazus_loss(self):
        # Flood Data Preprocessing
        gdf_flood = self.combine_flood_data('EconLoss')
        gdf_flood.rename(columns={'EconLoss': 'Loss_USD'}, inplace=True)

        # convert from 2018 dollars
        gdf_flood.Loss_USD = utils.convert_USD(gdf_flood.Loss_USD.values, 2018)

        # merge with tracts
        self.gdf_tract = self.gdf_tract.merge(gdf_flood[['tract', 'Loss_USD']], left_on='geoid', right_on=['tract'], how='left')
        self.gdf_tract['Loss_USD'] = self.gdf_tract['Loss_USD'].fillna(0)

if __name__ == "__main__":
    csf_esl = CSF_ESL()
    csf_esl.load_data()
    
    csf_esl.calculate_transportation_loss()
    csf_esl.export_results(csf_esl.gdf_tract, csf_esl.path_output_transportation, "CST Transportation loss")
    csf_esl.plot_results(csf_esl.gdf_tract, 'Loss_USD', 'CSF: Transportation Loss')
    
    csf_esl.calculate_dislocation_loss()
    csf_esl.export_results(csf_esl.gdf_tract, csf_esl.path_output_dislocation, "CSF dislocation loss")
    csf_esl.plot_results(csf_esl.gdf_tract, 'Loss_USD', 'CSF: Dislocation Loss')
    
    csf_esl.calculate_hazus_loss()
    csf_esl.export_results(csf_esl.gdf_tract, csf_esl.path_output_hazus, "CSF Building Damage")
    csf_esl.plot_results(csf_esl.gdf_tract, 'Loss_USD', 'CSF: Building Damage')