#%% read packages
import geopandas as gpd
import pandas as pd
import duckdb
import os
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES


class RCA_RR:
    def __init__(self):
        # Input paths
        self.path_fp = PATHNAMES.RCA_RR_FP_raw
        self.path_footprint = PATHNAMES.ESL_CST_building_footprints

        # Output paths
        self.path_results = PATHNAMES.RCA_RR_FP_score

            # Calculate percent coverage

    
    def _connect_to_db(self):
        """Connect to the DuckDB database and load the required extensions."""
        con = duckdb.connect()
        con.install_extension("spatial")
        con.load_extension("spatial")

        # Load data
        gdf_tract = utils.get_blank_tract()
        gdf_tract['geometry'] = gdf_tract['geometry'].to_wkt()
        con.execute("CREATE TABLE tracts AS SELECT * FROM gdf_tract")
        con.execute(f"CREATE TABLE footprints AS SELECT * FROM '{self.path_footprint}'")
        con.execute(f"CREATE TABLE policies AS SELECT * FROM '{self.path_fp}'")

        return con
    
    def _get_count_within_tract(self, con, table_name:str, uid: str) -> pd.DataFrame:

        """Count the number of buildings or policies within each tract."""

        df = con.sql(
            f"""
                SELECT 
                    t.BCT_txt,
                    COUNT({table_name}.{uid}) AS Building_Count
                FROM 
                    tracts t
                LEFT JOIN 
                    {table_name}
                ON 
                    ST_Within(ST_Centroid({table_name}.geom), ST_GeomFromText(t.geometry))
                WHERE 
                    t.BCT_txt IS NOT NULL
                GROUP BY 
                    t.BCT_txt
            """
        ).df()

        return df
    
    def _calc_percent_covered(self, policies, buildings):
        if buildings == 0:
            result = 0
        else:
            result = 100. * policies / buildings
        return min(result, 100)
        
    def calculate_flood_policies(self):
        """Perform all calculations related to flood policies and coverage."""
        con = self._connect_to_db()

        gdf_buildings = self._get_count_within_tract(con, 'footprints', 'BIN')
        gdf_policies = self._get_count_within_tract(con, 'policies', 'Policy_Num')

        gdf_final = pd.concat([gdf_buildings, gdf_policies], axis=1)


        gdf_final['Percent_Coverage'] = gdf_final.apply(
            lambda row: self._calc_percent_covered(
                row['Policy_Count'], row['Building_Count']),
            axis=1
        )

        # Calculate score
        gdf_final = utils.calculate_kmeans(gdf_final, data_column='Percent_Coverage')

        return gdf_final
    
    def calculate_flood_policies_geopandas(self):

        #%% LOAD DATA
        gdf_tract = utils.get_blank_tract()
        gdf_fp = gpd.read_file(self.path_fp)
        gdf_footprint = gpd.read_file(self.path_footprint)

        #%% count buildings by tract and save result in scratch
        #spatial join to get count
        gdf_join = gpd.sjoin(gdf_footprint, gdf_tract, how='left', predicate='within')
        gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
        df_count = gdf_join.pivot_table(index='BCT_txt', values=['BIN'], aggfunc=len)
        gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
        gdf_tract.fillna(value={'BIN': 0}, inplace=True)
        gdf_tract.rename(columns={"BIN": "Building_Count"}, inplace=True)

        #%%count number of policies by tract
        gdf_join = gpd.sjoin(gdf_fp, gdf_tract, how='left', predicate='within')
        gdf_join.dropna(subset={'BCT_txt'}, inplace=True)
        df_count = gdf_join.pivot_table(index='BCT_txt', values=['Type'], aggfunc=len)
        gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_index=True, how='left')
        gdf_tract.fillna(value={'Type': 0}, inplace=True)
        gdf_tract.rename(columns={"Type": "Policy_Count"}, inplace=True)


        gdf_tract['Percent_Coverage'] = gdf_tract.apply(
            lambda row: self._calc_percent_covered(row['Policy_Count'], row['Building_Count']),
        axis=1)

        #%% calculate score
        gdf_tract = utils.calculate_kmeans(gdf_tract, data_column='Percent_Coverage')

        return gdf_tract
    
    def export_results(self, gdf_tract):

        # Save results
        gdf_tract.to_file(self.path_results)

        # # Plot results
        # plotting.plot_notebook(
        #     gdf_tract,
        #     column='Score',
        #     title='RCA_RR_FP: Flood Insurance Coverage',
        #     legend='Score',
        #     cmap='Blues',
        #     type='score'
        # )

        # Document results
        try:
            text = """ 
            The data was produced by {}
            Located in {}
            """.format(os.path.basename(__file__), os.path.dirname(__file__))
            path_readme = os.path.dirname(self.path_results)
            utils.write_readme(path_readme, text)
        except Exception as e:
            print(f"Failed to write README: {e}")

        print("Finished calculating RR factor RF: flood insurance coverage.")

if __name__ == "__main__":
    rr = RCA_RR()
    rr.calculate_flood_policies()
