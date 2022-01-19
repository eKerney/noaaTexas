import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import getpass
import time
import matplotlib.pyplot as plt 
import os
import requests
import altair as alt
from functools import reduce
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
pd.options.mode.chained_assignment = None  # default='warn'

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

def getNOAAData(m, y, s):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'DETROIT METRO AP MI':'USW00094847','PENDLETON OR': 'USW00024155','CORPUS CHRISTI NWS TX':'USC00412011','LAS VEGAS INTL AIRPORT NV':'USW00023169','MIAMI NWSFO FL':'USC00085667'}                                         
    noaa = NOAAData()
    noaa.stationData('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000)
    return noaa

def getPlot(noaa, station, year, month):
    
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][0:10]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    # average daily wind given in meters/sec
    AWND = noaa.filterDF('AWND')
    AWND['AWND'] = AWND.apply(lambda d: (d['value'] * .223694), axis=1)
    AWND = AWND.drop(['value','datatype'], axis=1)
    # 5 second wind gust given in meters/sec
    WSF5 = noaa.filterDF('WSF5')
    WSF5['WSF5'] = WSF5.apply(lambda d: (d['value'] * .223694), axis=1)
    WSF5 = WSF5.drop(['value','datatype'], axis=1)
    # 2 minute sustained wind given in meters/sec
    WSF2 = noaa.filterDF('WSF2')
    WSF2['WSF2'] = WSF2.apply(lambda d: (d['value'] * .223694), axis=1)
    WSF2 = WSF2.drop(['value','datatype'], axis=1)
    # precipitation given in tenths of a millimeter
    PRCP = noaa.filterDF('PRCP')
    PRCP['PRCP'] = PRCP.apply(lambda d: (d['value'] * 0.1), axis=1)
    PRCP = PRCP.drop(['value','datatype'], axis=1)
    # snow given in actual illimeters
    SNOW = noaa.filterDF('SNOW')
    SNOW['SNOW'] = SNOW.apply(lambda d: (d['value']), axis=1)
    SNOW = SNOW.drop(['value','datatype'], axis=1)
    # All temps given in Celsius tenths of a degree
    TAVG = noaa.filterDF('TAVG')
    TAVG['TAVG'] = TAVG.apply(lambda d: (d['value'] * .18) + 32, axis=1)
    TAVG = TAVG.drop(['value','datatype'], axis=1)
    TMAX = noaa.filterDF('TMAX')
    TMAX['TMAX'] = TMAX.apply(lambda d: (d['value'] * .18) + 32, axis=1)
    TMAX = TMAX.drop(['value','datatype'], axis=1)
    TMIN = noaa.filterDF('TMIN')
    TMIN['TMIN'] = TMIN.apply(lambda d: (d['value'] * .18) + 32, axis=1)
    TMIN = TMIN.drop(['value','datatype'], axis=1)
    
    #fig, ax = plt.subplots(figsize=(12,8))
    #AWND.plot(ax=ax, linewidth=3, x='dayYear', linestyle='--', color='grey',y='AWND')
    #WSF5.plot(ax=ax, linewidth=3, x='dayYear', linestyle='-', color='orange',y='WSF5')
    #WSF2.plot(ax=ax, linewidth=3, x='dayYear', linestyle='-', color='green',y='WSF2')
    #TAVG.plot(ax=ax, linewidth=3, x='dayYear', color='black', y='TAVG')
    #TMAX.plot(ax=ax, kind='bar',x='dayYear', color='red', y='TMAX')
    #TMIN.plot(ax=ax, kind='bar',x='dayYear', color='blue',y='TMIN')
    #SNOW.plot(ax=ax, linewidth=3, x='dayYear', linestyle='--', color='purple',y='SNOW')
    #PRCP.plot(ax=ax, linewidth=3, x='dayYear', linestyle='-', color='blue',y='PRCP')
    #plt.xticks(rotation = 90) 
    #plt.title((f'{station}'), fontsize=26, color='black')
    
    # merge all dataframes into one dataframe to rule them all!
    dfs= [AWND, WSF5, WSF2, TAVG, TMAX, TMIN, SNOW, PRCP]
    dfM = reduce(lambda  left,right: pd.merge(left,right,on=['dayYear']), dfs)
    weatherPlots(AWND,PRCP,SNOW,TAVG,TMAX,TMIN,WSF5,WSF2, station, year,month, dfM)
    #st.pyplot(fig)   

def weatherPlots(AWND,PRCP,SNOW,TAVG,TMAX,TMIN,WSF5,WSF2,station, year, month, dfM):    
    st.write(f'## {station} DAILY WEATHER')
    fig, ax = plt.subplots(figsize=(10,4))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    bar1 = ax.bar(ind+width, dfM['WSF5'], width, color='orange', edgecolor='#c26e00', linewidth=1, alpha=0.7)
    bar2 = ax.bar(ind, dfM['WSF2'], width, color = '#ffe600', edgecolor='#b5a300', linewidth=1, alpha=0.7)
    line1 = ax.plot(ind+width, dfM['AWND'], color = '#e65525', linewidth=3.0, alpha=0.8)
    plt.ylabel('mph')
    plt.xticks(ind+width,dfM['dayYear'])
    legend_elements = [Patch(facecolor='orange', edgecolor='#c26e00', label='Max Wind Gust'),
        Patch(facecolor='#ffe600', edgecolor='#b5a300', label='Sustained Wind'),
        Line2D([0], [0], color='#e65525', lw=4, label='Avg Daily Wind')]
    plt.legend(handles=legend_elements, frameon=False)
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY WIND DATA - {month} {year}'), fontsize=20, color='black', pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    st.pyplot(fig)
    st.write('')

    fig, ax = plt.subplots(figsize=(10,4))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    bar1 = ax.bar(ind+width, dfM['TMAX'], width, color='#ff0000', edgecolor='#910000', linewidth=1, alpha=0.6)
    bar2 = ax.bar(ind, dfM['TMIN'], width, color = '#0019fc', edgecolor='#00095e', linewidth=1, alpha=0.5)
    line1 = ax.plot(ind+width, dfM['TAVG'], color = '#ae00ff', linewidth=3.0, alpha=0.7)
    plt.ylabel('F')
    plt.xticks(ind+width,dfM['dayYear'])
    legend_elements = [Patch(facecolor='#ff0000', edgecolor='#910000', label='Max Temperature'),
        Patch(facecolor='#0019fc', edgecolor='#00095e', label='Min Temperature'),
        Line2D([0], [0], color='#ae00ff', lw=4, label='Avg Daily Temp')]
    plt.legend(handles=legend_elements,frameon=False)
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY TEMP DATA - {month} {year}'), fontsize=20, color='black',pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    st.pyplot(fig)
    st.write('')

    fig, ax = plt.subplots(figsize=(10,4))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    bar1 = ax.bar(ind+width, dfM['PRCP'], width, color='green', edgecolor='#084700', linewidth=1, alpha=0.7)
    bar2 = ax.bar(ind, dfM['SNOW'], width, color = 'grey', edgecolor='#404040', linewidth=1, alpha=0.6)
    #line1 = ax.plot(ind+width, dfM['TAVG'], color = '#e65525', linewidth=4.0)
    plt.ylabel('mm')
    plt.xticks(ind+width,dfM['dayYear'])
    legend_elements = [Patch(facecolor='green', edgecolor='#084700', label='Precipitation'),
        Patch(facecolor='grey', edgecolor='#292929', label='Snow')]
    plt.legend(handles=legend_elements, frameon=False)
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY PRECIP DATA - {month} {year}'), fontsize=20, color='black', pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    st.pyplot(fig)

    st.write(f'## {station} - {month} {year}')
    maxTemp = alt.Chart(TMAX).mark_bar(color='red',opacity=0.7, size=10).encode(
        #x='dayYear',y='TMAX')
        alt.Y('TMAX:Q', scale=alt.Scale(domain=(-10, 120))), x='dayYear')
    minTemp = alt.Chart(TMIN).mark_bar(color='blue',opacity=0.7,size=10).encode(x='dayYear', y='TMIN')
    avgTemp = alt.Chart(TAVG).mark_line(color='purple').encode(x='dayYear', y='TAVG').properties(height=400, title='DAILY TEMPERATURE (F)')
    tempChart = maxTemp + minTemp + avgTemp 
    st.altair_chart(tempChart, use_container_width=True)

    maxWind = alt.Chart(WSF5).mark_bar(color='orange',opacity=0.8, size=10).encode(
        alt.Y('WSF5:Q',scale=alt.Scale(domain=(0, 80))), x='dayYear')
    susWind = alt.Chart(WSF2).mark_bar(color='yellow',opacity=0.7,size=10).encode(x='dayYear', y='WSF2')
    avgWind = alt.Chart(AWND).mark_line(color='grey').encode(x='dayYear', y='AWND').properties(height=400, title='DAILY WIND SPEED (mph)')
    windChart = maxWind + susWind + avgWind 
    st.altair_chart(windChart, use_container_width=True)

    dayPrecip = alt.Chart(PRCP).mark_bar(color='green',opacity=0.8, size=10).encode(
        y='PRCP',x='dayYear')
        #alt.Y('PRCP:Q', scale=alt.Scale(domain=(0, 100))), x='dayYear')
    daySnow = alt.Chart(SNOW).mark_bar(color='grey',opacity=0.7,size=10).encode(x='dayYear', y='SNOW').properties(height=400, title='DAILY PRECIP/SNOW (mm)')
    #daySnow = alt.Chart(SNOW).mark_line(color='grey').encode(x='dayYear', y='SNOW').properties(height=400)
    snowChart = dayPrecip + daySnow
    st.altair_chart(snowChart, use_container_width=True)
 
st.title('HISTORIC WEATHER SUITABILITY')

st.markdown('Data: NOAA Global Historical Climate Network (GHCN) - Daily land surface observations')

station = st.sidebar.selectbox(
     'SELECT STATION',
     ('PENDLETON OR','DETROIT METRO AP MI','LAS VEGAS INTL AIRPORT NV'))     
year = st.sidebar.selectbox(
     'SELECT YEAR',
     ('2021','2020','2019','2018','2017'))
month = st.sidebar.select_slider(
     'SELECT MONTH',
     options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'])

noaa = getNOAAData(month, year, station)
#st.write(noaa.df)
getPlot(noaa, station, year, month)

st.markdown('---')
