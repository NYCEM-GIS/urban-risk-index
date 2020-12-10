""" Opens and reads NRI data for NYC"""

#%% read packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
import requests

from MISC import params_1 as params
from MISC import utils_1 as utils
utils.set_home()

# %% open tract  (old way)
gdf_tract = utils.get_blank_tract()

#%% open, slice, and project NRI shapefile
path_NRI = params.PATHNAMES.at['OTH_NRI_data', 'Value']
gdf_NRI = gpd.read_file(path_NRI)
gdf_NRI = gdf_tract.merge(gdf_NRI.drop(columns='geometry'), left_on='Stfid', right_on='TRACTFIPS', how='inner')
gdf_NRI = utils.project_gdf(gdf_NRI)

#%% save as csv
path_csv = params.PATHNAMES.at['OTH_NRI_csv', 'Value']
gdf_NRI.to_excel(path_csv[:-4] + '.xlsx')

#%% get risk info
list_risks = [('AVLN', 'Avalanche'),
              ('CFLD', 'Coastal Flooding'),
              ('CWAV', 'Cold Wave'),
              ('DRGT', 'Drought'),
              ('ERQK', 'Earthquake'),
              ('HAIL', 'Hail'),
              ('HWAV', 'Heat Wave'),
              ('HRCN', 'Hurricane'),
              ('ISTM', 'Ice Storm'),
              ('LNDS', 'Landslide'),
              ('LTNG', 'Lightning'),
              ('RFLD', 'Riverine Flooding'),
              ('SWND', 'Strong Wind'),
              #('TRND', 'Tornado'),
              ('TSUN', 'Tsunami'),
              ('VLCN', 'Volcanic Activity'),
              ('WFIR', 'Wildfire'),
              ('WNTW', 'Winter Weather')]
list_abbr = [x[0] for x in list_risks]
list_names = [x[1] for x in list_risks]
list_abbr.reverse()
list_names.reverse()


#%% plot expected number of deaths by hazards
list_EALP = [gdf_NRI[x + '_EALP'].sum() for x in list_abbr]
x_pos = [i for i, _ in enumerate(list_abbr)]
fig = plt.figure(figsize=(6, 8))
ax = fig.add_subplot(111)
ax.barh(x_pos, list_EALP, color='red', alpha=.5)
plt.xlabel('Deaths / Year')
plt.ylabel('Hazard')
plt.yticks(x_pos, list_names)
plt.tight_layout()
plt.grid(linestyle='dotted')
plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_Deaths_1.png')
plt.show()

#%% plot expected building damage by hazard
list_EALB = [gdf_NRI[x + '_EALB'].sum()/1000000. for x in list_abbr]
x_pos = [i for i, _ in enumerate(list_abbr)]
fig = plt.figure(figsize=(6, 8))
ax = fig.add_subplot(111)
ax.barh(x_pos, list_EALB, color='green', alpha=.5)
ax.set_xlim([0, 60] )
for i, EALB in enumerate(list_EALB):
   plt.text(55, x_pos[i], round(EALB, 1))
plt.xlabel('Building Damage ($M) / Year')
plt.ylabel('Hazard')
plt.yticks(x_pos, list_names)
plt.tight_layout()
plt.grid(linestyle='dotted')
plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_Building_Damage_1.png')
plt.show()

#%% plot expected total loss
list_EALT = [gdf_NRI[x + '_EALT'].sum()/1000000 for x in list_abbr]
x_pos = [i for i, _ in enumerate(list_abbr)]
fig = plt.figure(figsize=(6, 8))
ax = fig.add_subplot(111)
ax.barh(x_pos, list_EALT, color='grey', alpha=.5)
#ax.set_xlim([0, 60] )
for i, EALT in enumerate(list_EALT):
   plt.text(85, x_pos[i], round(EALT, 1))
plt.xlabel('Total EAL ($M) / Year')
plt.ylabel('Hazard')
plt.yticks(x_pos, list_names)
plt.tight_layout()
plt.grid(linestyle='dotted')
plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_AllTotal_EAL_1.png')
plt.show()

#%% plot spatial distribution of total losses by hazards
for i in np.arange(len(list_abbr)):
    abbr = list_abbr[i]
    name = list_names[i]
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf_NRI.plot(ax=ax, column=abbr + "_EALT", legend=True, cmap='Blues', categorical=False,
                  legend_kwds={'label': 'USD'})
    gdf_NRI.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title(name + ' EAL', fontsize=20)
    plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_Map_{}_1.png'.format(name))
    plt.show()

#%% plot spatial distribution of total losses by hazards
fig = plt.figure(figsize=(9, 6.5))
ax = fig.add_subplot(111)
plt.axis('off')
gdf_NRI.plot(ax=ax, column="SOVI_SCORE", legend=True, cmap='Oranges', categorical=False,
              legend_kwds={'label': 'USD'})
gdf_NRI.boundary.plot(ax=ax, color='k', lw=0.1)
plt.title('SOVI Score', fontsize=20)
plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_Map_SOVI_1.png'.format(name))
plt.show()

#%% plot spatial distribution of total losses by hazards
fig = plt.figure(figsize=(9, 6.5))
ax = fig.add_subplot(111)
plt.axis('off')
gdf_NRI.plot(ax=ax, column="RESL_SCORE", legend=True, cmap='Greens', categorical=False,
              legend_kwds={'label': 'USD'})
gdf_NRI.boundary.plot(ax=ax, color='k', lw=0.1)
plt.title('RESL Score', fontsize=20)
plt.savefig(r'.\8_FIGURES\OTHER\NRI\Hazard_Map_Resilience_1.png'.format(name))
plt.show()



