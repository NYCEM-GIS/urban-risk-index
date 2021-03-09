""" list folder names for report"""

path_raw = r'C:\temp\AAA_URI_SANDBOX\1_RAW_INPUTS'
path_processed = r'C:\temp\AAA_URI_SANDBOX\2_PROCESSED_INPUTS'

import os
import pandas as pd

os.chdir(path_raw)
list_raw = next(os.walk('.'))[1]
df = pd.DataFrame(data={'list_raw': list_raw})
df.to_csv('C://temp/list_raw.csv')


os.chdir(path_processed)
list_raw = next(os.walk('.'))[1]
df = pd.DataFrame(data={'list_raw': list_raw})
df.to_csv('C://temp/list_processed.csv')

os.chdir(r'C:\temp\AAA_URI_SANDBOX\4_CODE\URI\DATA_PROCESSING')
list_raw = os.listdir()
df = pd.DataFrame(data={'list_raw': list_raw})
df.to_csv('C://temp/list_code_1.csv')



os.chdir(r'C:\temp\AAA_URI_SANDBOX\4_CODE\URI\CALCULATE')
list_raw = os.listdir()
df = pd.DataFrame(data={'list_raw': list_raw})
df.to_csv('C://temp/list_code_2.csv')


os.chdir(r'C:\temp\AAA_URI_SANDBOX\4_CODE\URI\MISC')
list_raw = os.listdir()
df = pd.DataFrame(data={'list_raw': list_raw})
df.to_csv('C://temp/list_code_3.csv')