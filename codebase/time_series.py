import numpy as np 
import pandas as pd 
import datetime

dateparse = lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')


FILE="./crime.csv"

d = pd.read_csv(FILE,
  header=0,names=['Dc_Dist', 'Psa', 'Dispatch_Date_Time', 'Dispatch_Date',
       'Dispatch_Time', 'Hour', 'Dc_Key', 'Location_Block', 'UCR_General',
       'Text_General_Code',  'Police_Districts', 'Month', 'Lon',
       'Lat'],dtype={'Dc_Dist':str,'Psa':str,
                'Dispatch_Date_Time':str,'Dispatch_Date':str,'Dispatch_Time':str,
                  'Hour':str,'Dc_Key':str,'Location_Block':str,
                     'UCR_General':str,'Text_General_Code':str,
              'Police_Districts':str,'Month':str,'Lon':str,'Lat':str},
             parse_dates=['Dispatch_Date_Time'],date_parser=dateparse)

# Fix Month to datetime Month
d['Month'] = d['Month'].apply(lambda x: datetime.datetime.strptime(x,'%Y-%m'))
print(d.groupby(['Month', 'Text_General_Code']).count())
