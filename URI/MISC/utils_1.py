""" Contains utilities that are used by all scripts """

import os
import warnings
import geopandas as gpd
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.cluster import KMeans
from URI.MISC import params_1 as params
from shapely.ops import nearest_points
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES



#%% set home directory
def set_home():
    os.chdir(PATHNAMES.home)
set_home()

#%% create readme
def write_readme(path_readme, readme_text):
    f = open(path_readme + "\\README.txt", "w")
    f.write(readme_text)
    f.close()


#%% normalize score to scale of 0 to 1 (exclusive)
# values should be numpy array
def normalize_rank_percentile(values, list_input_null_values=None, output_null_value=-999):
    # remove null values from array
    if list_input_null_values is None:
        list_input_null_values = [-999]
    values_trim = np.delete(values, np.where(np.isin(values, list_input_null_values)))
    # add a very high values and low value to prevent 0 and 100 values
    values_trim = np.r_[-1e20, values_trim, 1e20]
    # look through and calculate values_out
    values_out = np.zeros(len(values))
    for i, val in enumerate(values):
        if np.isin(val, list_input_null_values):
            values_out[i] = output_null_value
        else:
            values_out[i] = stats.percentileofscore(values_trim, val, kind='rank')/100
    return values_out


#%% convert value to 2018 dollars using consumer price index (CPI)
def convert_USD(base_value, base_year: int):
    #get target year from parameters
    target_year = PARAMS['target_year'].value
    #load CPI index
    path_CPI = PATHNAMES.CPI_table
    df_CPI = pd.read_excel(path_CPI, skiprows=10,
                           index_col=0, parse_dates=True)
    #get the yearly average
    df_CPI_year = df_CPI.resample('Y').mean()
    df_CPI_year.index = df_CPI_year.index.year
    index_factor = df_CPI_year.at[target_year, 'CPIAUCNS' ] / df_CPI_year.at[base_year, 'CPIAUCNS' ]
    target_value = base_value * index_factor
    return target_value


#%% calculate kmeans score and label
def calculate_kmeans(df, data_column, score_column='Score', n_cluster=5, reverse=False):
    if score_column in df.columns:
        print("warning: kmeans score already exists.")
        return df
    else:
        if len(df) < 5:
            df_result = df.copy()
            df_result[score_column] = np.ones(len(df))*3
        else:
            kmeans = KMeans(n_clusters=5)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df['Cluster_ID'] = kmeans.fit_predict(np.round(df[[data_column]], 6))
            # make lookup for class label
            df_label = pd.DataFrame()
            df_label['Cluster_ID'] = np.arange(n_cluster)
            df_label['Cluster_Center'] = kmeans.cluster_centers_.flatten()
            df_label.sort_values('Cluster_Center', inplace=True)
            if not reverse:
                df_label[score_column] = np.arange(1, n_cluster+1)
            else:
                df_label[score_column] = np.arange(n_cluster, 0, -1)
            # assign score to each cluster
            df_result = df.merge(df_label[['Cluster_ID', score_column]], on='Cluster_ID', how='left')
            df_result.drop(columns={'Cluster_ID'}, inplace=True)
        return df_result

#%%
def calculate_quantile(df, data_column, score_column='Score_QT', n_cluster=5):
    percentile = [stats.percentileofscore(df[data_column], x, kind='rank') for x in df[data_column]]
    df[score_column] = [np.minimum(x//20 + 1, 5) for x in np.array(percentile)]
    return df

#%%
def calculate_percentile(df, data_column, score_column='Percentile'):
    if score_column in df.columns:
        print("warning: kmeans score already exists.")
        pass
    else:
        percentile = np.round([stats.percentileofscore(df[data_column].values, x, kind='rank') for x in np.round(df[data_column].values, 6)], 2)
        df[score_column] = percentile
        return df

#%% calculate equal interval score 1 to 5
def calculate_equal_interval(df, data_column, score_column='Score_EI', n_cluster=5):
    df[score_column] = pd.cut(df[data_column], n_cluster, labels=np.arange(1, 1 + n_cluster), duplicates='drop').astype(int)
    return df

#%% count number of points (or fraction of) within 1/2 mile of tract
#gdf_data is point layer, column_key is unique id for each point
def calculate_radial_count(gdf_data, column_key, buffer_distance_ft=2640):
    #load gdf_tract
    gdf_data = project_gdf(gdf_data)
    gdf_tract = get_blank_tract()
    gdf_tract['area_ft2'] = gdf_tract['geometry'].area
    #make shapefile with 1/2 mile radius
    gdf_buffer = gdf_data.copy()
    gdf_buffer['geometry'] = gdf_data['geometry'].buffer(distance=buffer_distance_ft)
    #create empty df to fill
    df_fill = pd.DataFrame(columns=['BCT_txt', 'Fraction_Covered'])
    # loop through each buffer, and add BCT_txt and area filled to list
    print("Calculating.", end='')
    for i, idx in enumerate(gdf_buffer.index):
        this_buffer = gdf_buffer.loc[[idx]]
        this_intersect = gpd.overlay(gdf_tract, this_buffer[[column_key, 'geometry']], how='intersection')
        this_intersect['area_intersect_ft2'] = this_intersect['geometry'].area
        this_intersect['Fraction_Covered'] = np.minimum(this_intersect['area_intersect_ft2'] / this_intersect['area_ft2'], 1.0)
        #add to df_fill
        df_fill = pd.concat([df_fill, this_intersect[['BCT_txt', 'Fraction_Covered']]])
        if i % 500 == 0:
            print(".", end=''),
    print('Done')
    #get the sum  by tract and join
    df_sum = df_fill.groupby(by='BCT_txt').sum()
    gdf_tract = gdf_tract.merge(df_sum, on='BCT_txt', how='left')
    #fill nan with value 0
    gdf_tract.fillna(0, inplace=True)
    return gdf_tract


#%%
def project_gdf(gdf):
    epsg = PARAMS['epsg'].value
    gdf = gdf.to_crs(epsg=epsg)
    return gdf


#%%
def get_blank_tract(add_pop=False):
    path_tract = PATHNAMES.BOUNDARY_tract
    list_exclude = PARAMS['list_excluded_tracts'].value
    gdf_tract = gpd.read_file(path_tract)
    bool_keep = [x not in list_exclude for x in gdf_tract['boroct2020']]
    gdf_tract = gdf_tract.loc[bool_keep, :].copy()
    gdf_tract['BCT_txt'] = gdf_tract['boroct2020'].values
    gdf_tract = project_gdf(gdf_tract)
    gdf_tract.index = np.arange(len(gdf_tract))
    if add_pop:
        path_population_tract = PATHNAMES.population_by_tract
        df_pop = pd.read_excel(path_population_tract, skiprows=5)
        df_pop.dropna(inplace=True, subset=['2020 DCP Borough Code', '2020 Census Tract'])
        df_pop.rename(columns={2020: 'pop_2020'}, inplace=True)
        df_pop['BCT_txt'] = [
            str(int(df_pop.at[x, '2020 DCP Borough Code'])) + str(int(df_pop.at[x, '2020 Census Tract'])).zfill(6) for x
            in df_pop.index]
        gdf_tract = gdf_tract.merge(df_pop[['BCT_txt', 'pop_2020']], on='BCT_txt', how='left')
    return gdf_tract

#%% divide by zero and set to 0 if denominator is 0
def divide_zero(x, y):
    if y == 0:
        return 0
    else:
        return x / y


# %% zonal statistics with input shapefile into output shapefile
# path data can either be string or actual data gdf file
# handle null values.
def convert_to_tract_average(path_data, column_name, column_name_out,
                             list_input_null_values=None, output_null_value=-999):
    # get data to convert
    if list_input_null_values is None:
        list_input_null_values = [-999]
    if type(path_data) == str:
        gdf_data = gpd.read_file(path_data)
    else:
        gdf_data = path_data.copy()
    gdf_tract = get_blank_tract()
    # get spatial union, drop areas with no tract
    gdf_union = gpd.overlay(gdf_tract, gdf_data, how='union')
    gdf_union.dropna(subset=['BCT_txt'], inplace=True)
    # calculate area of each union slice
    gdf_union['area_ft2'] = gdf_union['geometry'].area
    # for each tract, calculate area weighted average of contributions
    # if some values are null, use other values.  If all value are null, assign null
    gdf_tract[column_name_out] = np.zeros(len(gdf_tract))
    for i, idx in enumerate(gdf_tract.index):
        this_bct = gdf_tract.at[idx, 'BCT_txt']
        # get slices from this tract
        this_gdf_union = gdf_union.loc[gdf_union['BCT_txt'] == this_bct, :]
        # remove null data values
        this_gdf_union.dropna(subset=[column_name], inplace=True)
        # remove null values based on list
        for null_val in list_input_null_values:
            keep_bool = (this_gdf_union[column_name].values != null_val)
            this_gdf_union = this_gdf_union.loc[keep_bool, :]
        # if nothing left, set tract value to null value
        if len(this_gdf_union) == 0:
            gdf_tract.at[idx, column_name_out] = output_null_value
        # otherwise set to spatially weighted average
        else:
            data_value_tract_ave = np.average(this_gdf_union[column_name].values,
                                              weights=this_gdf_union['area_ft2'].values)
            gdf_tract.at[idx, column_name_out] = data_value_tract_ave
    return gdf_tract


def near(gdf, single_point, points_layer):
    # find the nearest point and return the corresponding Place value
    nearest = gdf.geometry == nearest_points(single_point, points_layer)[1]
    distance = single_point.distance(gdf[nearest]['geometry'].iloc[0])
    return distance






