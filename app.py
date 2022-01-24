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
import matplotlib as mpl
mpl.rcParams['text.color'] = '#575757'
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
    st = ['USW00013722','US1OKOK0087','US1OKOK0106','US1OKOK0098','US1OKOK0075','US1OKOK0056','US1OKOK0071','US1OKOK0069','US1OKOK0107','US1OKOK0060','US1OKOK0029','US1OKOK0070','US1OKOK0105','US1OKOK0111','US1OKOK0109','US1OKOK0077']
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'TEST':st[0],'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    noaa = NOAAData()
    noaa.stationData('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000)
    return noaa

def getPlot(noaa, station, year, month):
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][8:10]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    # average daily wind given in meters/sec
    try:
        AWND = noaa.filterDF('AWND')
        AWND['AWND'] = AWND.apply(lambda d: (d['value'] * .223694), axis=1)
        AWND = AWND.drop(['value','datatype'], axis=1)
    except:
        AWND = pd.DataFrame(columns = ['dayYear', 'AWND'])
    # 5 second wind gust given in meters/sec
    try:
        WSF5 = noaa.filterDF('WSF5')
        WSF5['WSF5'] = WSF5.apply(lambda d: (d['value'] * .223694), axis=1)
        WSF5 = WSF5.drop(['value','datatype'], axis=1)
    except:
        WSF5 = pd.DataFrame(columns = ['dayYear', 'WSF5'])
    # 2 minute sustained wind given in meters/sec
    try:   
        WSF2 = noaa.filterDF('WSF2')
        WSF2['WSF2'] = WSF2.apply(lambda d: (d['value'] * .223694), axis=1)
        WSF2 = WSF2.drop(['value','datatype'], axis=1)
    except:
        WSF2 = pd.DataFrame(columns = ['dayYear', 'WSF2'])
    # precipitation given in tenths of a millimeter
    try:
        PRCP = noaa.filterDF('PRCP')
        PRCP['PRCP'] = PRCP.apply(lambda d: (d['value'] * 0.1), axis=1)
        PRCP = PRCP.drop(['value','datatype'], axis=1)
    except:
        PRCP = pd.DataFrame(columns = ['dayYear', 'PRCP'])
    # snow given in actual millimeters
    try:
        SNOW = noaa.filterDF('SNOW')
        SNOW['SNOW'] = SNOW.apply(lambda d: (d['value']) * 0.1, axis=1)
        SNOW = SNOW.drop(['value','datatype'], axis=1)
    except:
        SNOW = pd.DataFrame(columns = ['dayYear', 'SNOW'])
    # All temps given in Celsius tenths of a degree
    try:    
        TAVG = noaa.filterDF('TAVG')
        TAVG['TAVG'] = TAVG.apply(lambda d: (d['value'] * .18) + 32, axis=1)
        TAVG = TAVG.drop(['value','datatype'], axis=1)
    except:
        TAVG = pd.DataFrame(columns = ['dayYear', 'TAVG'])
    try:
        TMAX = noaa.filterDF('TMAX')
        TMAX['TMAX'] = TMAX.apply(lambda d: (d['value'] * .18) + 32, axis=1)
        TMAX = TMAX.drop(['value','datatype'], axis=1)
    except:
        TMAX = pd.DataFrame(columns = ['dayYear', 'TMAX'])
    try:
        TMIN = noaa.filterDF('TMIN')
        TMIN['TMIN'] = TMIN.apply(lambda d: (d['value'] * .18) + 32, axis=1)
        TMIN = TMIN.drop(['value','datatype'], axis=1)
    except:
        TMIN= pd.DataFrame(columns = ['dayYear', 'TMIN'])
    # merge all dataframes into one dataframe to rule them all!
    dfs= [AWND, WSF5, WSF2, TAVG, TMAX, TMIN, SNOW, PRCP]
    dfM = reduce(lambda left,right: pd.merge(left,right,on=['dayYear']), dfs)
    weatherPlots(AWND,PRCP,SNOW,TAVG,TMAX,TMIN,WSF5,WSF2, station, year,month, dfM)
    #st.pyplot(fig)   

def weatherPlots(AWND,PRCP,SNOW,TAVG,TMAX,TMIN,WSF5,WSF2,station, year, month, dfM):    
    st.write(f'<h2 style="text-align:center">{station}</h2>', unsafe_allow_html=True)
    # column layout for side by side charts
    col1, col2 = st.columns([1,1])
    txtC = '#575757'
    # plot for daily wind speed
    fig, ax = plt.subplots(figsize=(12,6))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    WSF5c,WSF5e,WSF2c,WSF2e,AWNDc = '#1bab6b','#00542f','#72ab92','#00703f','#00ff8f'
    bar1 = ax.bar(ind+width, dfM['WSF5'], width, color=WSF5c, edgecolor=WSF5e, linewidth=1, alpha=0.8)
    bar2 = ax.bar(ind, dfM['WSF2'], width, color = WSF2c, edgecolor=WSF2e, linewidth=1, alpha=0.6)
    line1 = ax.plot(ind+width, dfM['AWND'], color = AWNDc, linewidth=3.0, alpha=0.7)
    plt.ylabel('mph', fontsize=12)
    plt.xticks(ind+width/2,dfM['dayYear'])
    legend_elements = [Patch(facecolor=WSF5c, edgecolor=WSF5e, label='Max Wind Gust'),
        Patch(facecolor=WSF2c, edgecolor=WSF2e, label='Sustained Wind'),
        Line2D([0], [0], color=AWNDc, lw=3, label='Avg Daily Wind')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY WIND DATA - {month} {year}'), fontsize=20, color=txtC, pad=30, )
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    ax.set_ylim([0, 80])
    with col1:
        st.pyplot(fig)

    # plot for daily temperature
    fig, ax = plt.subplots(figsize=(12,6.1))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    mic, mie, mac, mae, lc = '#188bad','#0c303b','#fc6603','#662900','#4903fc' 
    bar1 = ax.bar(ind+width, dfM['TMAX'], width, color=mac, edgecolor=mae, linewidth=1, alpha=0.7)
    bar2 = ax.bar(ind, dfM['TMIN'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.7)
    line1 = ax.plot(ind+width, dfM['TAVG'], color = lc, linewidth=3.0, alpha=0.5)
    plt.ylabel('F',fontsize=12)
    plt.xticks(ind+width/2,dfM['dayYear'])
    legend_elements = [Patch(facecolor=mac, edgecolor=mae, label='Max Temperature'),
        Patch(facecolor=mic, edgecolor=mae, label='Min Temperature'),
        Line2D([0], [0], color=lc, lw=3, label='Avg Daily Temp')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY TEMP DATA - {month} {year}'), fontsize=20, color='#575757',pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    ax.set_ylim([-10, 120])
    with col2:
        st.pyplot(fig)
    
    # plot for daily precipitation
    fig, ax = plt.subplots(figsize=(12,6))
    N = len(dfM.index)
    ind = np.arange(N) 
    width = 0.4
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    bar1 = ax.bar(ind, dfM['PRCP'], width, color=Pc, edgecolor=Pe, linewidth=1, alpha=0.8)
    plt.ylabel('precip mm',fontsize=12)
    plt.xticks(ind+width/2,dfM['dayYear'])
    legend_elements = [Patch(facecolor=Pc, edgecolor=Pe, label='Precipitation', alpha=0.8),
        Patch(facecolor=Sc, edgecolor=Se, label='Snow',alpha=0.7)]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=8) 
    plt.title((f'{station} - DAILY PRECIP DATA - {month} {year}'), fontsize=20, color='#575757', pad=30)
    ax.set_ylim([0, 50])
    # make a plot with different y-axis using second axis object
    ax2 = ax.twinx() 
    ax2.bar(ind+width, dfM['SNOW'], width, color = Sc, edgecolor=Se, linewidth=1, alpha=0.7)
    ax2.set_ylabel("snow cm",fontsize=12)
    ax2.set_ylim([0, 50])
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    #ax2.set_axis_off()
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #ax.set_axis_off()
    #cl1,cl2, cl3 = st.columns([1,2.5,1])
    #st.pyplot(fig)
    #with cl2:
    #    st.pyplot(fig)
    # side by side layout for plot and table
    cl1, cl2 = st.columns([1,1])
    with cl1:
        st.pyplot(fig)
    with cl2:
        st.write(f'<p style="text-align:center;font-family:sans-serif;font-weight:bold">WEATHER DATA - {station} - {month} {year}</p>', unsafe_allow_html=True)
        st.write(dfM)
        
    
### MAIN APP SECTION
st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)
st.write(f'<h1 style="text-align:center">HISTORIC WEATHER SUITABILITY</h2>', unsafe_allow_html=True)
st.write(f'<p style="text-align:center">Data: NOAA Global Historical Climate Network (GHCN) - Daily land surface observations</p>', unsafe_allow_html=True)

station = st.sidebar.selectbox(
     'SELECT STATION',
     ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'))     
year = st.sidebar.selectbox(
     'SELECT YEAR',
     ('2021','2020','2019','2018','2017','2016','2015','2014'))
month = st.sidebar.select_slider(
     'SELECT MONTH',
     options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'])

noaa = getNOAAData(month, year, station)
getPlot(noaa, station, year, month)
st.markdown('---')
