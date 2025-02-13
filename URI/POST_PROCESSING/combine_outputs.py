import pandas as pd
import geopandas as gpd
from pathlib import Path
import os
import sys
sys.path.extend([Path(__file__).parent.parent.parent])
import URI.PARAMS.path_names as PATHNAMES

list_abbrev_haz = ['CER', 'CSF', 'CSW', 'ERQ', 'EXH', 'WIW', 'ALL']

alias_path = PATHNAMES.dashboard_aliases
path_nta = PATHNAMES.BOUNDARY_nta
nta_folder = PATHNAMES.OUTPUTS_folder + r'\URI\NTA'
path_save = PATHNAMES.OUTPUTS_folder + r'\Dashboard\URI_Combined_NTA.shp'

aliases = pd.read_excel(alias_path)


#%% open and merge all URI shapefiles
gdf_all = gpd.read_file(path_nta)
for i, haz in enumerate(list_abbrev_haz):
    print(haz)
    path_haz = os.path.join(nta_folder, f'URI_{haz}_NTA.shp')
    gdf_haz = gpd.read_file(path_haz)
    gdf_haz = gdf_haz.set_index('nta2020')
    list_col_keep = [col for col in gdf_haz.columns if ((haz in col) or (col not in gdf_all.columns))]
    gdf_all = gdf_all.merge(gdf_haz[list_col_keep], left_on='nta2020', right_index=True, how='left')


list_col_keep = aliases['Field Name'].to_list() + ['geometry']
gdf_all[list_col_keep].to_file(path_save)
