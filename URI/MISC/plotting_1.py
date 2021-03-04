""" make plots for distribution, and notebooks"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests
from mpl_toolkits.axes_grid1 import make_axes_locatable

import URI.MISC.params_1 as params
import URI.MISC.utils_1 as utils
utils.set_home()
make_plots = params.SETTINGS.at['make_plots', 'Value']

bool_save = 1

#%% define for plotting
def plot_score(gdf, column, title, legend, cmap):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf.plot(ax=ax, column=column, legend=True, cmap=cmap, categorical=True,
                  legend_kwds={'title': 'Score', 'bbox_to_anchor':(.2, .9),
                               'frameon':False})
    gdf.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title(title, fontsize=20)
    plt.show()
    pass

def plot_raw(gdf, column, title, legend, cmap):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.title(title, fontsize=20)
    plt.axis('off')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=1.0)
    gdf.plot(ax=ax, column=column, legend=True, cmap=cmap, categorical=False, cax=cax,
                    legend_kwds={'label': legend})
    gdf.boundary.plot(ax=ax, color='k', lw=0.1)
    pass

def plot_notebook(gdf, column, title, legend, cmap, type='score'):
    if make_plots:
        if type=='score':
            plot_score(gdf, column, title, legend, cmap)
            plt.show()
            pass
        elif type=='raw':
            plot_raw(gdf, column, title, legend, cmap)
            plt.show()
            pass
        else:
            pass
    else:
        pass


def plot_URI_nb(haz, gdf_data):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf_data.plot(ax=ax, column='URI', legend=True, cmap='Greys', categorical=True,
                  legend_kwds={'title': 'Value', 'bbox_to_anchor':(.2, .9),
                               'frameon':False})
    gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title('Urban Risk Index - {}'.format(haz), fontsize=20)
    plt.show()
    pass

def plot_ESL_nb(gdf_ESL, title):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    # if ((haz=='EXH') and (title=='Loss USD - Deaths')):
    #     gdf_ESL.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False, vmax=1.5e6,
    #                   legend_kwds={'label': 'Loss [USD]'})
    # else:
    gdf_ESL.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False,
                      legend_kwds={'label': 'Loss [USD]'})
    gdf_ESL.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title(title, fontsize=20)
    plt.show()
    pass

def plot_RCA_nb(haz, gdf_data):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf_data.plot(ax=ax, column='RCA', legend=True, cmap='Blues', categorical=False,
                      legend_kwds={'label': 'Resilience Capacity Score'})
    gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title('Resilience Capacity - {}'.format(haz), fontsize=20)
    plt.show()

def plot_SOV_nb(gdf_data):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf_data.plot(ax=ax, column='SOV', legend=True, cmap='Reds', categorical=False,
                      legend_kwds={'label': 'Social Vulnerability Score'})
    gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title('Social Vulnerability Score - All Hazards', fontsize=20)
    plt.show()

def plot_inline(gdf_data, column, scheme='equal_interval'):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    if scheme=='equal_interval':
        gdf_data.plot(ax=ax, column=column, categorical=False, legend=True)
    else:
        gdf_data.plot(ax=ax, column=column, categorical=False, legend=True,
                      scheme=scheme)
    plt.show()

if __name__ == '__main__':

    gdf = utils.get_blank_tract()
    plot_notebook(gdf, column='Acres', title = 'Title', legend = 'Legend', cmap='Blues', type='raw')

    # list_haz_name = ['Extreme Heat', 'Winter Weather', 'Coastal Storm',
    #        'Coastal Erosion', 'High Winds']
    # for i, haz in enumerate(list_haz):
    #     path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\URI\\URI_{}_1.pdf'.format(haz)
    #     path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\URI_{}_tract.shp'.format(haz, haz)
    #     gdf_data = gpd.read_file(path_data)
    #     fig = plt.figure(figsize=(9, 6.5))
    #     ax = fig.add_subplot(111)
    #     plt.axis('off')
    #     # divider = make_axes_locatable(ax)
    #     # cax = divider.append_axes("right", size="5%", pad=0.5)
    #     gdf_data.plot(ax=ax, column='URI', legend=True, cmap='Greys', categorical=True,
    #                   legend_kwds={'title': 'Value', 'bbox_to_anchor':(.2, .9),
    #                                'frameon':False})
    #     gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    #     plt.title('Urban Risk Index - {}'.format(list_haz_name[i]), fontsize=20)
    #     if bool_save: plt.savefig(path_save)
    #     plt.show()
    #
    # #%% plot ESL
    # for i, haz in enumerate(list_haz):
    #     path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\ESL\\ESL_{}_1.pdf'.format(haz)
    #     path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\ESL\ESL_{}_tract.shp'.format(haz, haz)
    #     gdf_data = gpd.read_file(path_data)
    #     fig = plt.figure(figsize=(9, 6.5))
    #     ax = fig.add_subplot(111)
    #     plt.axis('off')
    #     # divider = make_axes_locatable(ax)
    #     # cax = divider.append_axes("right", size="5%", pad=0.5)
    #     if haz=='EXH':
    #         gdf_data.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False, vmax=1.5e6,
    #                       legend_kwds={'label': 'Loss [USD]'})
    #     else:
    #         gdf_data.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False,
    #                       legend_kwds={'label': 'Loss [USD]'})
    #     gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    #     plt.title('Expected Annual Loss - {}'.format(list_haz_name[i]), fontsize=20)
    #     if bool_save: plt.savefig(path_save)
    #     plt.show()
    #
    # #%% plot RCA
    # list_haz = ['EXH', 'WIW', 'CST', 'CER', 'HIW', 'ERQ', 'FLD']
    # list_haz_name = ['Extreme Heat', 'Winter Weather', 'Coastal Storm',
    #        'Coastal Erosion', 'High Winds', 'Earthquake',
    #        'Flooding']
    # for i, haz in enumerate(list_haz):
    #     path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\RCA\\RCA_{}_1.pdf'.format(haz)
    #     path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\RCA\RCA_{}_tract.shp'.format(haz, haz)
    #     gdf_data = gpd.read_file(path_data)
    #     fig = plt.figure(figsize=(9, 6.5))
    #     ax = fig.add_subplot(111)
    #     plt.axis('off')
    #     # divider = make_axes_locatable(ax)
    #     # cax = divider.append_axes("right", size="5%", pad=0.5)
    #     gdf_data.plot(ax=ax, column='RCA', legend=True, cmap='Blues', categorical=False,
    #                       legend_kwds={'label': 'Resilience Capacity Score'})
    #
    #     gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    #     plt.title('Resilience Capacity - {}'.format(list_haz_name[i]), fontsize=20)
    #     if bool_save: plt.savefig(path_save)
    #     plt.show()
    #
    # #%% plot SOV
    # path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\SOV\\SOV_1.pdf'
    # path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\SOV\SOV_tract.shp'
    # gdf_data = gpd.read_file(path_data)
    # fig = plt.figure(figsize=(9, 6.5))
    # ax = fig.add_subplot(111)
    # plt.axis('off')
    # gdf_data.plot(ax=ax, column='SOV', legend=True, cmap='Reds', categorical=False,
    #                   legend_kwds={'label': 'Social Vulnerability Score'})
    # gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    # plt.title('Social Vulnerability Score - All Hazards', fontsize=20)
    # if bool_save: plt.savefig(path_save)
    # plt.show()