

""" compare speaks english less than well vs less than very well"""

#%%% import packages
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from census import Census
from us import states
from MISC import params_1 as params
from MISC import utils_1 as utils
from MISC import plotting_1 as plotting
utils.set_home()

#%% load cdc covi score at tract level and reproject
path_sovi = params.PATHNAMES.at['SOV_tract', 'Value']
gdf_sovi = gpd.read_file(path_sovi)
#reproject
epsg = params.SETTINGS.at['epsg', 'Value']
gdf_sovi = gdf_sovi.to_crs(epsg=epsg)

#%% calcualte speaks english less than well
gdf_sovi['ENG_less_well'] = gdf_sovi['E_LIMENG'] / gdf_sovi['E_TOTPOP']

#%% load tract
gdf_tract = utils.get_blank_tract()

#%% merge
gdf_tract = gdf_tract.merge(gdf_sovi[['FIPS', 'ENG_less_well', 'E_TOTPOP']], left_on='Stfid', right_on='FIPS', how='left')


#%%
c = Census("fde2495ae880d06dc1acbdc40a96ba0cffbf5ae8")
response_total = c.acs5.state_county_tract('B06007_001E', states.NY.fips, '*', Census.ALL)
response_eng1 = c.acs5.state_county_tract('B06007_005E', states.NY.fips, '*', Census.ALL)
response_eng2 = c.acs5.state_county_tract('B06007_008E', states.NY.fips, '*', Census.ALL)
list_tract1 = [x['tract'] for x in response_total]
list_state = [x['state'] for x in response_total]
list_county = [x['county'] for x in response_total]
list_total = [x['B06007_001E'] for x in response_total]
list_tract2 = [x['tract'] for x in response_eng1]
list_eng1 = [x['B06007_005E'] for x in response_eng1]
list_tract3 = [x['tract'] for x in response_eng2]
list_eng2 = [x['B06007_008E'] for x in response_eng2]

#%%
df = pd.DataFrame(index=np.arange(len(list_tract1)), data={'eng1':list_eng1,
                                          'eng2': list_eng2,
                                            'tot':list_total,
                                           'tract':list_tract1,
                                           'county':list_county,
                                           'state':list_state})
df['Eng1_Eng2'] = (df['eng1']+df['eng2'])
df['Stfid'] = [df.loc[x,"state"] + df.loc[x, 'county']+df.loc[x,'tract'] for x in df.index]
#%% merge
gdf_tract = gdf_tract.merge(df[['Eng1_Eng2', 'Stfid', 'tot']], left_on='Stfid', right_on='Stfid', how='inner')

#%%
gdf_tract['Eng_less_very_well'] = gdf_tract['Eng1_Eng2']/gdf_tract['E_TOTPOP']

#%%
gdf_tract_nan = gdf_tract.dropna(subset=['ENG_less_well', 'Eng_less_very_well'])
from sklearn.metrics import r2_score
r2 = r2_score(gdf_tract_nan['ENG_less_well'].values, gdf_tract_nan['Eng_less_very_well'].values)

#%% plot
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)
ax.plot(gdf_tract_nan['ENG_less_well'], gdf_tract_nan['Eng_less_very_well'], '.')
plt.xlabel('Fraction Speaks English Less Than Well (CDC-SOVI, ACS 2014-2018)')
plt.ylabel('Fraction Speaks English Less Than Very Well (API, ACS 2014-2018)')
ax.plot([0, 1], [0, 1], '--', color='.5')
plt.grid(linestyle='dashed')
plt.tight_layout()
plt.show()

gdf_tract_nan[['ENG_less_well','Eng_less_very_well']].to_csv(r'C:\Users\Dwilusz\Downloads\Speak_Well.csv')