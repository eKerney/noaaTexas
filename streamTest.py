import streamlit as st
import pandas as pd
import numpy as np

import datetime as dt
import getpass
import pandas as pd
import time
import matplotlib.pyplot as plt 
import os
import requests

class NOAAData(object):
    def __init__(self, token='ZXvAfJZyarrTJkcgefnAHuXmNAeATfci'):
        try: 
          # NOAA API Endpoint
          self.url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'
          # User input added
          if token == False:
            token = getpass.getpass('NOAA API V2 TOKEN: ')
          else:
            token = token
          self.h = dict(token=token)
          print(f'Successfully created NOAAData API Object: {self}')
        except:
          print(f'COULD NOT CREATE NOAAData API OBJECT')

    def poll_api(self, req_type, payload):
        # Initiate http request - kwargs are constructed into a dict and passed as optional parameters
        # Ex (limit=100, sortorder='desc', startdate='1970-10-03', etc)
        r = requests.get(self.url + req_type, headers=self.h, params=payload)

        if r.status_code != 200:  # Handle erroneous requests
            print("Error: " + str(r.status_code))
        else:
            r = r.json()
            try:
                return r['results']  # Most JSON results are nested under 'results' key
            except KeyError:
                return r  # for non-nested results, return the entire JSON string
   
    def stationData(self, dataSetID, stationID, startDate, endDate, limit):
        req_type = 'data'
        #startDate = input(f'Start Date(ex. 2021-01-01): ')
        #endDate = input(f'End Date(ex. 2021-01-31): ')
        params = {'datasetid': dataSetID, 'stationid': stationID, 'startdate': startDate, 'enddate': endDate, 'limit': limit}
        #params = {'datasetid': 'GHCND', 'stationid': 'GHCND:USW00024155', 'startdate': '2022-01-01', 'enddate': '2022-01-10', 'limit': 1000}
        data = self.poll_api(req_type, params)
        self.df = pd.DataFrame(data)
        return self.df

    def filterDF(self, param):
        #params = ['AWND','PRCP','SNOW','SNWD','TAVG','TMAX','TMIN','WDF2','WDF5','WSF2','WSF5']
        #for i, p in enumerate(params):
        #  print(f'{i} - {p}')
        #ind = int(input(f'SELECT A WEATHER PARAMETER INDEX: '))
        dfFiltered = self.df[self.df.datatype == param ]
        return dfFiltered
    
    # weatherData = noaa.fetch_data(datasetid='GHCND', stationid='GHCND:USW00024155', startdate='2022-01-01', enddate='2022-01-10', limit=1000)
@st.cache
def getNOAAData(m, y, s):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'DETROIT METRO AP MI':'USW00094847','PENDLETON OR': 'USW00024155','CORPUS CHRISTI NWS TX':'USC00412011','LAS VEGAS INTL AIRPORT NV':'USW00023169','MIAMI NWSFO FL':'USC00085667'}                                         
    noaa = NOAAData()
    noaa.stationData('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000)
    return noaa

def getPlot(noaa, station):
    AWND = noaa.filterDF('AWND')
    PRCP = noaa.filterDF('PRCP')
    SNOW = noaa.filterDF('SNOW')
    TAVG = noaa.filterDF('TAVG')
    TMAX = noaa.filterDF('TMAX')
    TMIN = noaa.filterDF('TMIN')
    WSF2 = noaa.filterDF('WSF2')
    WSF5 = noaa.filterDF('WSF5')
    fig, ax = plt.subplots(figsize=(12,8))
    AWND.plot(ax=ax, linewidth=3, x='date', linestyle='--', color='grey')
    TAVG.plot(ax=ax, linewidth=3, x='date', color='black')
    TMAX.plot(ax=ax, kind='bar',x='date', color='red')
    TMIN.plot(ax=ax, kind='bar',x='date', color='blue')
    WSF5.plot(ax=ax, linewidth=3, x='date', linestyle='-', color='orange')
    plt.xticks(rotation = 90) 
    plt.title((f'{station}'), fontsize=26, color='black')
    st.pyplot(fig)   
 
st.title('NOAA Weather Station Comparison ')

station = st.sidebar.selectbox(
     'SELECT STATION',
     ('PENDLETON OR','DETROIT METRO AP MI','CORPUS CHRISTI NWS TX','MIAMI NWSFO FL','LAS VEGAS INTL AIRPORT NV'))     
year = st.sidebar.selectbox(
     'SELECT YEAR',
     ('2021','2020','2019','2018','2017'))
month = st.sidebar.select_slider(
     'SELECT MONTH',
     options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'])

noaa = getNOAAData(month, year, station)
getPlot(noaa, station)
st.subheader('Raw Data')

st.write(noaa.df)
st.markdown('---')
st.markdown('---')



DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')
@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data = load_data(10000)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

#st.subheader('Number of pickups by hour')
#hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
#st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)

### NOAA Object Classes


