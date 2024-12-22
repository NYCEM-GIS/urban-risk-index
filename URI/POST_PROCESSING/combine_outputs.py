import pandas as pd
import geopandas as gpd
import sys; 
sys.path.extend([r'C:\Users\HSprague\vscode\URI_Calculator_v1_1_TEMPLATE\4_CODE'])
import URI.PARAMS.path_names as PATHNAMES
import os

list_abbrev_haz = ['CER', 'CSF', 'CSW', 'ERQ', 'EXH', 'WIW', 'ALL']


alias_path = r'C:\Users\HSprague\ARCADIS\30194489 - NYCEM URI - Documents\Project\GIS Application\Dashboard Aliases.xlsx'
path_nta = PATHNAMES.BOUNDARY_nta
nta_folder = PATHNAMES.OUTPUTS_folder + r'\URI\NTA'
path_save = PATHNAMES.OUTPUTS_folder + r'\Dashboard\URI_Combined_NTA.shp'


aliases = pd.read_excel(alias_path)


#%% open and merge all URI shapefiles
gdf_all = gpd.read_file(path_nta)
for i, haz in enumerate(list_abbrev_haz):
    print(haz)
    path_haz = os.path.join(nta_folder, f'URI_{haz}_NTA.shp')
    # if i==0:
    #     gdf_all = gpd.read_file(path_haz)
    #     len_check = len(gdf_all.columns)
    # else:
    gdf_haz = gpd.read_file(path_haz)
    gdf_haz = gdf_haz.set_index('nta2020')
    list_col_keep = [col for col in gdf_haz.columns if ((haz in col) or (col not in gdf_all.columns))]
    gdf_all = gdf_all.merge(gdf_haz[list_col_keep], left_on='nta2020', right_index=True, how='left')
    # len_check += len(gdf_haz[list_col_keep].columns)


list_col_keep = aliases['Field Name'].to_list() + ['geometry']
gdf_all[list_col_keep].to_file(path_save)
