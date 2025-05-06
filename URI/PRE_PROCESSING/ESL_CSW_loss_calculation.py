import numpy as np
import pandas as pd
import geopandas as gpd
import os
import datetime
import URI.UTILITY.utils_1 as utils
import URI.UTILITY.plotting_1 as plotting
import URI.PARAMS.path_names as PATHNAMES
import URI.PARAMS.hardcoded as HARDCODED
from URI.PARAMS.params import PARAMS

utils.set_home()

class ESL_CSW:
    def __init__(self):
        """Initialize parameters."""
        
        # Paths
        self.path_hazus = PATHNAMES.ESL_CSW_hazus_wind
        self.path_hazus_output = PATHNAMES.ESL_CST_hazus_loss
        self.path_tree = PATHNAMES.HHC_TreeServices
        self.path_events = PATHNAMES.stormevents_table
        self.path_event_types = PATHNAMES.HHC_eventtypes
        self.path_storm_event_types = PATHNAMES.HHC_stormeventtypes
        self.path_tree_output = PATHNAMES.ESL_CST_loss_tree
        # Hardcoded values
        self.service_buffer = HARDCODED.buffer_period_tree_servicing_days
        self.loss_per_tree_service = 3500.0  # USD

    @classmethod
    def to_file(cls, gdf, path_output):
        """Save GeoDataFrame to file."""
        gdf.to_file(path_output)
        print(f"Saved results to {path_output}")


    @classmethod
    def plot_notebook(cls, gdf, column, title, legend, cmap):
        """Plot GeoDataFrame in a notebook."""
        plotting.plot_notebook(gdf, column=column, title=title, legend=legend, cmap=cmap, type='raw')

    def calculate_hazus_loss(self):
        """Calculate Hazus loss and save results."""
        # Load data
        gdf_tract = utils.get_blank_tract()
        df_hazus = gpd.read_file(self.path_hazus)

        # Convert from 2007 to URI dollars, multiply by 1000
        df_hazus['Loss_USD'] = utils.convert_USD(df_hazus.EconLoss, 2007) * 1000.

        # Merge to tract
        gdf_tract = gdf_tract.merge(df_hazus[['tract', 'Loss_USD']], left_on='geoid', right_on='tract', how='left')

        return gdf_tract




    def calculate_tree_loss(self):
        """Calculate Tree loss and save results."""
        # Load data
        df_tree = pd.read_excel(self.path_tree, parse_dates=['DateInitiated', 'DateCreated'])
        gdf_tract = utils.get_blank_tract()
        df_events = pd.read_excel(self.path_events, parse_dates=['StartDate', 'EndDate'])
        df_event_types = pd.read_excel(self.path_event_types)
        df_storm_event_types = pd.read_excel(self.path_storm_event_types)

        # Get hazard type id
        type_name = 'Tropical Cyclone'
        type_id = df_event_types.loc[df_event_types.Name == type_name, 'Id'].values[0]

        # Get all storm events ids with this hazard type
        df_event_ids = df_storm_event_types.loc[df_storm_event_types.EventTypeId == type_id, :]
        df_event_ids.index = df_event_ids.StormEventId

        # Filter storm events with this id after 2009
        df_events = df_events[df_events.Id.isin(df_event_ids.index)]
        df_events = df_events[(df_events.StartDate >= datetime.datetime(2014, 1, 1)) &
                              (df_events.EndDate < datetime.datetime(2024, 1, 1))]

        # Vectorized event matching
        df_tree['Is_Event'] = df_tree['DateInitiated'].apply(
            lambda date: any((date >= row['StartDate']) & (date <= row['EndDate'] + datetime.timedelta(days=self.service_buffer))
                             for _, row in df_events.iterrows())
        )

        # Filter tree services
        df_tree = df_tree[(df_tree['Is_Event'] == 1) & (df_tree['HHCImportType'] != 0) & (df_tree['HHCImportType'] != 8)]

        # Assume all work orders are 3500
        Loss_USD = len(df_tree) * self.loss_per_tree_service / 10

        # Create GeoDataFrame and filter invalid rows
        gdf_tree = gpd.GeoDataFrame(df_tree, geometry=gpd.points_from_xy(df_tree.Long, df_tree.Lat))
        gdf_tree = gdf_tree[(gdf_tree.Lat != 0) & (gdf_tree.Long != 0)]
        gdf_tree.crs = "EPSG:4326"
        gdf_tree = utils.project_gdf(gdf_tree)

        # get the count per tract of tree services
        gdf_join = gpd.sjoin(gdf_tree, gdf_tract, how='left', predicate='within')
        gdf_join.dropna(subset=['BCT_txt'], inplace=True)
        df_count = gdf_join.groupby('BCT_txt').size().reset_index(name='Tree_Service_Count')

        # Merge counts and calculate losses
        gdf_tract = gdf_tract.merge(df_count, left_on='BCT_txt', right_on='BCT_txt', how='left')
        gdf_tract['Tree_Service_Count'].fillna(0, inplace=True)
        gdf_tract['Loss_USD'] = Loss_USD * gdf_tract['Tree_Service_Count'] / gdf_tract['Tree_Service_Count'].sum()

        return gdf_tract