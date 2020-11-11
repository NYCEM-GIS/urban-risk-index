""" make plots for distribution, and notebooks"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests
from mpl_toolkits.axes_grid1 import make_axes_locatable

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

bool_save = 1

#%% define for plotting

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

def plot_ESL_nb(haz, gdf_ESL, title):
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

if __name__ == '__main__':

    #%% plot URI
    list_haz = ['EXH']
    for haz in list_haz:
        path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\URI\\URI_{}_1.pdf'.format(haz)
        path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\URI\URI_{}_tract.shp'.format(haz, haz)
        gdf_data = gpd.read_file(path_data)
        fig = plt.figure(figsize=(9, 6.5))
        ax = fig.add_subplot(111)
        plt.axis('off')
        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes("right", size="5%", pad=0.5)
        gdf_data.plot(ax=ax, column='URI', legend=True, cmap='Greys', categorical=True,
                      legend_kwds={'title': 'Value', 'bbox_to_anchor':(.2, .9),
                                   'frameon':False})
        gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
        plt.title('Urban Risk Index - Extreme Heat', fontsize=20)
        if bool_save: plt.savefig(path_save)
        plt.show()

    #%% plot ESL
    for haz in list_haz:
        path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\ESL\\ESL_{}_1.pdf'.format(haz)
        path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\ESL\ESL_{}_tract.shp'.format(haz, haz)
        gdf_data = gpd.read_file(path_data)
        fig = plt.figure(figsize=(9, 6.5))
        ax = fig.add_subplot(111)
        plt.axis('off')
        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes("right", size="5%", pad=0.5)
        if haz=='EXH':
            gdf_data.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False, vmax=1.5e6,
                          legend_kwds={'label': 'Loss [USD]'})
        else:
            gdf_data.plot(ax=ax, column='Loss_USD', legend=True, cmap='Greens', categorical=False,
                          legend_kwds={'label': 'Loss [USD]'})
        gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
        plt.title('Expected Annual Loss - Extreme Heat', fontsize=20)
        if bool_save: plt.savefig(path_save)
        plt.show()

    #%% plot RCA
    list_haz = ['EXH', 'WIW', 'CST', 'CER', 'HIW', 'ERQ', 'FLD']
    list_haz_name = ['Extreme Heat', 'Winter Weather', 'Coastal Storm',
           'Coastal Erosion', 'High Winds', 'Earthquake',
           'Flooding']
    for i, haz in enumerate(list_haz):
        path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\RCA\\RCA_{}_1.pdf'.format(haz)
        path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\RCA\RCA_{}_tract.shp'.format(haz, haz)
        gdf_data = gpd.read_file(path_data)
        fig = plt.figure(figsize=(9, 6.5))
        ax = fig.add_subplot(111)
        plt.axis('off')
        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes("right", size="5%", pad=0.5)
        gdf_data.plot(ax=ax, column='RCA', legend=True, cmap='Blues', categorical=False,
                          legend_kwds={'label': 'Resilience Capacity Score'})

        gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
        plt.title('Resilience Capacity - {}'.format(list_haz_name[i]), fontsize=20)
        if bool_save: plt.savefig(path_save)
        plt.show()

    #%% plot SOV
    path_save = params.PATHNAMES.at['FIGURES_folder', 'Value'] + r'\\SOV\\SOV_1.pdf'
    path_data = params.PATHNAMES.at['OUTPUTS_folder', 'Value'] + r'\SOV\SOV_tract.shp'
    gdf_data = gpd.read_file(path_data)
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf_data.plot(ax=ax, column='SOV', legend=True, cmap='Reds', categorical=False,
                      legend_kwds={'label': 'Social Vulnerability Score'})
    gdf_data.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title('Social Vulnerability Score - All Hazards', fontsize=20)
    if bool_save: plt.savefig(path_save)
    plt.show()