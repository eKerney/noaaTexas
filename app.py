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
    
    def stationDataUnits(self, dataSetID, stationID, startDate, endDate, limit, units):
        req_type = 'data'
        params = {'datasetid': dataSetID, 'stationid': stationID, 'startdate': startDate, 'enddate': endDate, 'limit': limit, 'units':units}
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
    print('in getNOAA')
    #st = ['USW00013722','US1OKOK0087','US1OKOK0106','US1OKOK0098','US1OKOK0075','US1OKOK0056','US1OKOK0071','US1OKOK0069','US1OKOK0107','US1OKOK0060','US1OKOK0029','US1OKOK0070','US1OKOK0105','US1OKOK0111','US1OKOK0109','US1OKOK0077']
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    noaa = NOAAData()
    noaa.stationData('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000)
    return noaa

def getDailyData(m,y,s,d):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    # add 1 to day value, convert to int, then add leading zero if less than 10 for date format
    m2 = m
    if m=='FEB':
        d2 = (f'0{int(d)+1}') if (int(d)+1) < 10 else (f'{int(d)+1}')
        if d2 == '29':
            d2 = '01'
            m2 = 'MAR'    
    elif m=='APR' or m=='JUN' or m=='SEP' or m=='NOV':
        d2 = (f'0{int(d)+1}') if (int(d)+1) < 10 else (f'{int(d)+1}')
        if d2 == '31':
            d2 = '01'
            m2 = 'MAY' if m=='APR' else('JUL' if m=='JUN' else('OCT' if m=='SEP' else 'DEC'))
        d2 = '01' if d == int(30) else d2
    else:
        d2 = (f'0{int(d)+1}') if (int(d)+1) < 10 else (f'{int(d)+1}')
        if d2 == '32':
            d2 = '01'
            m2 = 'FEB' if m == 'JAN' else ('APR' if m == 'MAR' else ('JUN' if m == 'MAY' else ('AUG' if m == 'JUL' else ('SEP' if m == 'AUG' else ('NOV' if m=='OCT' else 'DEC')))))
    print(d, d2, m, m2)
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    #st.write('NORMAL_HLY', (f'GHCND:{sta[s]}'), (f'2010-{mon[m]}-{d}'), '2010-01-02', 1000, 'metric')
    noaa = NOAAData()
    # stan = noaa.stationData('NORMAL_HLY', 'GHCND:USW00024155', '2010-01-01', '2010-01-02', 1000, 'standard')
    noaa.stationDataUnits('NORMAL_HLY', (f'GHCND:{sta[s]}'), (f'2010-{mon[m]}-{d}'), (f'2010-{mon[m2]}-{d2}'), 1000, 'standard')
    #st.write(noaa.df)
    return noaa

def getDailyPlot(noaa, station, year, month, day):
    # functions to filter whole dataframe to retrive only records with specified parameter, and perfrom conversion 
    def getDF(df, param, expr):
        try:
            newDF = df[df.datatype == param]
            newDF[param] = newDF.apply(lambda d: eval(f'd["value"]{expr}'), axis=1)
            newDF = newDF.drop(['value','datatype'], axis=1)
        except:
            newDF = pd.DataFrame(columns = ['dayYear', param])
        return newDF
    
    def getMergedDF(sourceDF, dfList):
        dfFinal = pd.DataFrame(columns = ['dayYear'])
        for x in dfList:
            df = getDF(sourceDF, x['p'], x['e'])
            dfFinal = pd.merge(df, dfFinal, how='outer',on=['dayYear'])
        return dfFinal
    
    ### Primary function flow
    # format NOAA.df date attribute for hour and drop extraneous columns        
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][8:16]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    #st.write(noaa.df)
    # iterate through list of parameters and conversion expressions
    paramList = [{'p':'HLY-TEMP-NORMAL', 'e':''}, {'p':'HLY-HIDX-NORMAL', 'e':''}, {'p':'HLY-DEWP-NORMAL','e':''},
        {'p':'HLY-CLOD-PCTOVC','e':'*.10'}, {'p':'HLY-CLOD-PCTCLR','e':'*.10'}, {'p':'HLY-PRES-NORMAL','e':''},
        {'p':'HLY-WIND-AVGSPD','e':''}, {'p':'HLY-WIND-1STDIR','e':''}, {'p':'HLY-WIND-PCTCLM','e':'*.10'}, {'p':'HLY-WIND-VCTDIR','e':'*.10'},
        {'p':'HLY-TEMP-10PCTL','e':''},{'p':'HLY-TEMP-90PCTL','e':''}]
    dfClean = getMergedDF(noaa.df, paramList)
    #st.write(dfClean)
    dailyWeatherPlots(dfClean, station,year,month)

def dailyWeatherPlots(df, station, year, month):
    # Final dataframe cleaning before plotting
    df['dayYear'] = df.apply(lambda d: (d['dayYear'][3:16]), axis=1)
    df.drop(df.tail(1).index,inplace = True)
    #st.write(f'<h1 style="text-align:center;margin-top:-50px;">{station}</h1>', unsafe_allow_html=True)
    st.write(f'<h4 style="text-align:center;margin-top:-30px;">Hourly Average Weather Data</h4>', unsafe_allow_html=True)
    WSF5c,WSF5e,WSF2c,WSF2e,AWNDc = '#1bab6b','#00542f','#72ab92','#00703f','#00ff8f'
    txtC = '#575757'
    # plot for hourly windspeed 
    fig, ax = plt.subplots(figsize=(12,6.3))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    bar1 = ax.bar(ind, df['HLY-WIND-AVGSPD'], width, color=WSF5c, edgecolor=WSF5e, linewidth=1, alpha=0.8)
    #line1 = ax.plot(ind+width, df['HLY-WIND-1STDIR'], color = AWNDc, linewidth=3.0, alpha=0.9)
    plt.ylabel('windSpeed mph',fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [Patch(facecolor=WSF5c, edgecolor=WSF5e, label='Avg Hour Wind Speed'),
        Patch(facecolor=WSF2c, edgecolor=WSF2e, label='% Calm Winds'),
        Line2D([0], [0], color=AWNDc, lw=3, label='Wind Dir Degrees * 10')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'{station} - HOURLY WIND DATA - {month} {day} {year}'), fontsize=20, color='#575757', pad=30)
    ax.set_ylim([2, 16])
    # make a plot with different y-axis using second axis object
    ax2 = ax.twinx() 
    ax2.bar(ind+width, df['HLY-WIND-PCTCLM'], width, color = WSF2c, edgecolor=WSF2e, linewidth=1, alpha=0.2)
    line2 = ax2.plot(ind+width, df['HLY-WIND-VCTDIR'], color = AWNDc, linewidth=3.0, alpha=0.9)
    ax2.set_ylabel("% calm - wind dir deg * 10",fontsize=12)
    ax2.set_ylim([0, 40])
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    #ax2.set_axis_off()
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #st.pyplot(fig)
    col1, col2 = st.columns([1,1])
    with col1:
        st.pyplot(fig)
    
    # plot for hourly cloud coverage
    fig, ax = plt.subplots(figsize=(12,6))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    bar1 = ax.bar(ind+width, df['HLY-CLOD-PCTOVC'], width, color=Pc, edgecolor=Pe, linewidth=1, alpha=0.6)
    bar2 = ax.bar(ind, df['HLY-CLOD-PCTCLR'], width, width, color=Sc, edgecolor=Se, linewidth=1, alpha=0.6)
    #line1 = ax.plot(ind+width, df['HLY-CLOD-PCTOVC'], color = AWNDc, linewidth=3.0, alpha=0.7)
    plt.ylabel('%', fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [Patch(facecolor=Pc, edgecolor=Pe, label='Hourly Overcast %', alpha=0.8),
        Patch(facecolor=Sc, edgecolor=Se, label='Hourly Clear %',alpha=0.7)]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'{station} - HOURLY CLOUD DATA - {month} {day} {year}'), fontsize=20, color=txtC, pad=30, )
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    ax.set_ylim([0, 100])
    with col2:
        st.pyplot(fig)
    
    # plot for hourly Temperature, Heat Index & Dew Point
    fig, ax = plt.subplots(figsize=(12,6.1))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    mic, mie, mac, mae, lc = '#188bad','#0c303b','#fc6603','#662900','#4903fc' 
    #bar1 = ax.bar(ind+width, df['HLY-TEMP-NORMAL'], width, color=mac, edgecolor=mae, linewidth=1, alpha=0.7)
    bar1 = ax.bar(ind, df['HLY-TEMP-90PCTL'], width, color=mac, edgecolor=mae, linewidth=1, alpha=0.5)
    bar2 = ax.bar(ind+width, df['HLY-TEMP-10PCTL'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.5)
    #bar2 = ax.bar(ind, df['HLY-DEWP-NORMAL'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.7)
    line2 = ax.plot(ind+width, df['HLY-HIDX-NORMAL'], color = 'red', linewidth=3.0, alpha=0.5)
    line1 = ax.plot(ind+width, df['HLY-TEMP-NORMAL'], color = lc, linewidth=3.0, alpha=0.7)
    line1 = ax.plot(ind+width, df['HLY-DEWP-NORMAL'], color = 'green', linewidth=3.0, alpha=0.6)
    
    plt.ylabel('F',fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [Patch(facecolor=mac, edgecolor=mae, label='Hourly 90th percentile'),
        Patch(facecolor=mic, edgecolor=mae, label='Hourly 10th percentile'),
        Line2D([0], [0], color=lc, lw=3, label='Hourly Temp Avg'),
        Line2D([0], [0], color='red', lw=3, label='Hourly Heat Index Avg'),
        Line2D([0], [0], color='red', lw=3, label='Hourly Dew Point Avg')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'{station} - HOURLY TEMP DATA - {month} {day} {year}'), fontsize=20, color='#575757',pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    ax.set_ylim([10, 100])
    cl1, cl2 = st.columns([1,1])
    with cl1:
        st.pyplot(fig)
    with cl2:
        st.write(f'<p style="text-align:center;font-family:sans-serif;margin-bottom:3px;">HOURLY WEATHER DATA - {month} {day} </p>', unsafe_allow_html=True)
        st.dataframe(df, None, 210)

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
    st.write(f'<h1 style="text-align:center;margin-top:-100px;">{station}</h1>', unsafe_allow_html=True)
    st.write(f'<h4 style="text-align:center;margin:-40px;">Daily Weather Data</h4>', unsafe_allow_html=True)
    #st.markdown('Pendleton')
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
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # side by side layout for plot and table
    cl1, cl2 = st.columns([1,1])
    with cl1:
        st.pyplot(fig)
    with cl2:
        st.write(f'<p style="text-align:center;font-family:sans-serif;margin-bottom:3px;">WEATHER DATA - {month} {year}</p>', unsafe_allow_html=True)
        st.dataframe(dfM, None,210)
    st.write(f'<p style="text-align:center;margin-top:0px;margin-bottom:-30px">Data: NOAA Global Historical Climate Network (GHCN) - Daily land surface observations</p>', unsafe_allow_html=True)
    st.markdown('---')
    
### MAIN APP SECTION
st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)
print('start')
station = st.sidebar.selectbox(
     'SELECT STATION',
     ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'))     
year = st.sidebar.selectbox(
     'SELECT YEAR',
     ('2021','2020','2019','2018','2017','2016','2015','2014'))
month = st.sidebar.select_slider(
     'SELECT MONTH',
     options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'])

if month == 'FEB':
    day = st.sidebar.select_slider(
    'SELECT DAY',
    options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24','25','26','27','28'])
elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
    day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30'])
else:
    day = st.sidebar.select_slider(
    'SELECT DAY',
    options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24','25','26','27','28','29','30','31'])

noaa = getNOAAData(month, year, station)
getPlot(noaa, station, year, month)
noaaDaily = getDailyData(month, year, station, day)
getDailyPlot(noaaDaily, station, year, month, day)
#st.write(f'<h1 style="text-align:center">HISTORIC WEATHER SUITABILITY</h2>', unsafe_allow_html=True)
st.write(f'<p style="text-align:center">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Hourly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)

st.markdown('---')

