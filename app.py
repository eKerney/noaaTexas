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
from NOAA import *
import scipy
from scipy import interpolate
from scipy.interpolate import make_interp_spline
#import seaborn as sns
mpl.rcParams['text.color'] = '#575757'
mpl.rcParams['axes.edgecolor'] = '#575757'
pd.options.mode.chained_assignment = None  # default='warn'


# helper dataframe cleaning functions
def getDF(df, param, expr):
    try:
        #st.write(param, expr)
        newDF = df[df.datatype == param]
        df['value'] = df['value'].replace(-777.7, 0)
        newDF[param] = newDF.apply(lambda d: eval(f'd["value"]{expr}'), axis=1)
        newDF = newDF.drop(['value','datatype'], axis=1)
    except:
         #st.write('EXCEPT: ',param)
         newDF = pd.DataFrame(columns = ['dayYear', param])
    return newDF
    
def getMergedDF(sourceDF, dfList):
    dfFinal = pd.DataFrame(columns = ['dayYear'])

    for x in dfList: 
        #st.write(x)
        df = getDF(sourceDF, x['p'], x['e'])
        dfFinal = pd.merge(df, dfFinal, how='outer',on=['dayYear'])
    return dfFinal

### MONTHLY NORMALS SECTION    
def getMonthlyNormalsData(noaa, m, y, s):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    paramList = ['MLY-PRCP-NORMAL', 'MLY-PRCP-AVGNDS-GE001HI', 'MLY-PRCP-AVGNDS-GE010HI',
        'MLY-SNOW-NORMAL', 'MLY-SNOW-AVGNDS-GE001TI', 'MLY-SNOW-AVGNDS-GE010TI',
        'MLY-TAVG-NORMAL', 'MLY-TAVG-STDDEV', 'MLY-TMAX-NORMAL', 'MLY-TMAX-STDDEV',
        'MLY-TMIN-NORMAL', 'MLY-TMIN-STDDEV', 'MLY-DUTR-NORMAL']
    noaa.stationDataParams('NORMAL_MLY', (f'GHCND:{sta[s]}'), (f'2010-01-01') , (f'2010-12-01'), 1000, 'standard', [])
    return noaa

def showMonthlyNormals(noaa, month, year, station):
    # functions to filter whole dataframe to retrive only records with specified parameter, and perfrom conversion 
    # format NOAA.df date attribute for hour and drop extraneous columns        
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][5:7]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    
    # iterate through list of parameters and conversion expressions
    paramList = [{'p':'MLY-PRCP-NORMAL','e':'*2.54'}, {'p':'MLY-PRCP-AVGNDS-GE001HI','e':'*10'}, {'p':'MLY-PRCP-AVGNDS-GE010HI','e':'*10'},
        {'p':'MLY-SNOW-NORMAL','e':'*2.54'}, {'p':'MLY-SNOW-AVGNDS-GE001TI','e':''}, {'p':'MLY-SNOW-AVGNDS-GE010TI','e':''},
        {'p':'MLY-TAVG-NORMAL','e':''}, {'p':'MLY-TAVG-STDDEV','e':''}, {'p':'MLY-TMAX-NORMAL','e':''}, {'p':'MLY-TMAX-STDDEV','e':''},
        {'p':'MLY-TMIN-NORMAL','e':''}, {'p':'MLY-TMIN-STDDEV','e':''}, {'p':'MLY-DUTR-NORMAL','e':''}]
    dfClean = getMergedDF(noaa.df, paramList)

    dfClean['TEMP-ADD-STD-POS'] = dfClean.apply(lambda d: (d['MLY-TAVG-NORMAL']+d['MLY-TAVG-STDDEV']), axis=1 )
    dfClean['TEMP-ADD-STD-NEG'] = dfClean.apply(lambda d: (d['MLY-TAVG-NORMAL']-d['MLY-TAVG-STDDEV']), axis=1 )
    
    windAVG = getDailyWind(noaa, month, year, station)
    
    monthlyNormalsPlots(dfClean, station , year, month, windAVG[0], windAVG[1])
  

def monthlyNormalsPlots(df, station, year, month, wind, windGust):
    st.write(f'<h1 style="text-align:center;margin-top:-100px;">{station}</h1>', unsafe_allow_html=True)
    st.write(f'<h3 style="text-align:center;margin-top:-30px;">Monthly Weather Suitability</h3>', unsafe_allow_html=True)
    
    mic, mie, mac, mae, lc = '#188bad','#0c303b','#fc6603','#662900','#4903fc' 
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    WSF5c,WSF5e,WSF2c,WSF2e,AWNDc = '#1bab6b','#00542f','#72ab92','#00703f','#00d477'
    txtC = '#575757'

    fig, ax = plt.subplots(figsize=(10,6))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.2

    TMAXnp,TAVGnp,TMINnp = df['MLY-TMAX-NORMAL'].to_numpy(), df['MLY-TAVG-NORMAL'].to_numpy(), df['MLY-TMIN-NORMAL'].to_numpy(),
    PRCP_01np,TPOSnp,TNEGnp = df['MLY-PRCP-AVGNDS-GE010HI'].to_numpy(), df['TEMP-ADD-STD-POS'].to_numpy(),df['TEMP-ADD-STD-NEG'].to_numpy()
    npX = (df.index).to_numpy()
    
    X_Y_Spline = make_interp_spline(npX, TMAXnp)
    X_ = np.linspace(npX.min(), npX.max(), 500)
    TMAX = X_Y_Spline(X_)

    X_Y_Spline = make_interp_spline(npX, TAVGnp)
    TAVG = X_Y_Spline(X_)

    X_Y_Spline = make_interp_spline(npX, TMINnp)
    TMIN = X_Y_Spline(X_)

    X_Y_Spline = make_interp_spline(npX, PRCP_01np)
    PRCP_01 = X_Y_Spline(X_)

    X_Y_Spline = make_interp_spline(npX, TPOSnp)
    TPOS = X_Y_Spline(X_)

    X_Y_Spline = make_interp_spline(npX, TNEGnp)
    TNEG = X_Y_Spline(X_)

    line1 = ax.plot(X_+width, TMAX, color = mac, linewidth=2.5, alpha=0.7,dashes=[3, 1, 3, 1, 2, 1])
    line2 = ax.plot(X_+width, TAVG, color = lc, linewidth=4.0, alpha=0.6)
    line3 = ax.plot(X_+width, TMIN, color = mic, linewidth=2.5, alpha=0.8, dashes=[2.5, 1, 2.5, 1, 2, 1])
    line4 = ax.plot(X_+width, PRCP_01, color = AWNDc, linewidth=2.5, alpha=1.0,linestyle='dotted')
    line5 = ax.plot(X_+width, TPOS, color = '#a380ff', linewidth=1.0, alpha=0.8, linestyle='dotted')
    line6 = ax.plot(X_+width, TNEG, color = '#a380ff', linewidth=1.0, alpha=0.8, linestyle='dotted')
    ax.set_ylim([10, 100])
    plt.ylabel('Temp F',fontsize=12, color=txtC)

    ax2 = ax.twinx() 
    bar1 = ax2.bar(ind-(width-0), df['MLY-PRCP-NORMAL'], width, color=Pc, edgecolor=Pe, linewidth=1, alpha=0.5)
    bar2 = ax2.bar(ind, df['MLY-SNOW-NORMAL'], width, color = Sc, edgecolor=Se, linewidth=1, alpha=0.5)
    bar3 = ax2.bar(ind+width, wind['AWND_MEAN'], width, color = WSF2c, edgecolor=WSF2e, linewidth=1, alpha=0.3)
    bar4 = ax2.bar(ind+width+.2, windGust['WSF5_MEAN'], width, color = WSF5c, edgecolor=WSF5e, linewidth=1, alpha=0.4)
    ax2.set_ylim([0, 60])
   
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [
        Line2D([0], [0], color=mac, lw=2, label='Avg Mon Max Temp', dashes=[3, 1, 3, 1, 2, 1]),
        Line2D([0], [0], color=lc, lw=3, label='Avg Mon Temp'),
        Line2D([0], [0], color=mic, lw=2, label='Avg Mon Min Temp', dashes=[2.5, 1, 2.5, 1, 2, 1]),
        Line2D([0], [0], color=AWNDc, lw=2, label='# days precip>0.10 in (10X)',linestyle='dotted'),
        Patch(facecolor=Pc, edgecolor=Pe, label='Avg Mon Precip cm'),
        Patch(facecolor=Sc, edgecolor=Se, label='Avg Mon Snow cm'),
        Patch(facecolor=WSF2c, edgecolor=WSF2e, label='Avg Mon Wind Spd mph'),
        Patch(facecolor=WSF5c, edgecolor=WSF5e, label='Avg Mon Wind Gust mph'),
        ]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.5, loc='upper left', fontsize=8)
    plt.xticks(rotation = 90, fontsize=12) 
    plt.title((f'{station} - Monthly Climate Normals'), fontsize=20, color=txtC, pad=30, )
    ax.set_facecolor('#f7f7f7')
    fig.patch.set_facecolor('#f7f7f7')

    ax.tick_params(axis='y', colors=txtC)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x', colors=txtC)

    ax2.set_ylabel("Precip/Wind",fontsize=12, color=txtC)
    ax2.tick_params(axis='y', colors=txtC)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    col1, col2,col3 = st.columns([1,10,1])
    with col2:
        st.pyplot(fig)
    
    #st.pyplot(fig)
       

@st.cache()
def getDailyWind(noaa, m, y, s):
    dfAWND = pd.DataFrame(columns = ['month','AWND_MEAN'])
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    paramList = ['AWND']
    paramsVals = [{'p':'AWND', 'e':'*.223694'}]
    #noaa.stationData('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000)
    for month in mon:
        #st.write(month)
        noaa.stationDataParams('GHCND', (f'GHCND:{sta[s]}'), (f'2021-{mon[month]}-{day[month][0:2]}'),(f'2021-{mon[month]}-{day[month][3:5]}'), 1000, '', paramList)
        noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][5:10]), axis=1)
        noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
        mean = noaa.df.mean()
        dfAWND.loc[len(dfAWND)]=[mon[month], (noaa.df.mean())[0]*.223694]
    
    dfWSF5 = pd.DataFrame(columns = ['month','WSF5_MEAN'])
    paramList = ['WSF5']
    for month in mon:
        #st.write(month)
        noaa.stationDataParams('GHCND', (f'GHCND:{sta[s]}'), (f'2021-{mon[month]}-{day[month][0:2]}'),(f'2021-{mon[month]}-{day[month][3:5]}'), 1000, '', paramList)
        noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][5:10]), axis=1)
        noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
        mean = noaa.df.mean()
        dfWSF5.loc[len(dfWSF5)]=[mon[month], (noaa.df.mean())[0]*.223694]
        #st.write(dfFinal)
    return [dfAWND, dfWSF5]   

### DAILY NORMALS SECTION     
def getDailyNormalsData(noaa, m, y, s):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    paramList = ['DLY-DUTR-NORMAL', 'DLY-DUTR-STDDEV',
        'DLY-PRCP-PCTALL-GE001HI','DLY-PRCP-PCTALL-GE010HI','DLY-PRCP-PCTALL-GE050HI','DLY-PRCP-PCTALL-GE100HI',
        'DLY-SNOW-PCTALL-GE001TI','DLY-SNOW-PCTALL-GE010TI','DLY-SNOW-PCTALL-GE030TI','DLY-SNOW-PCTALL-GE050TI','DLY-SNOW-PCTALL-GE100TI',
        'DLY-SNWD-PCTALL-GE001WI','DLY-SNWD-PCTALL-GE003WI','DLY-SNWD-PCTALL-GE005WI','DLY-SNWD-PCTALL-GE010WI',
        'DLY-TAVG-NORMAL','DLY-TAVG-STDDEV','DLY-TMAX-NORMAL','DLY-TMIN-NORMAL',
        'MTD-PRCP-NORMAL','MTD-SNOW-NORMAL','YTD-PRCP-NORMAL','YTD-SNOW-NORMAL' ]
    noaa.stationDataParams('NORMAL_DLY', (f'GHCND:{sta[s]}'), (f'{2010}-{mon[m]}-{day[m][0:2]}') , (f'{2010}-{mon[m]}-{day[m][3:5]}'), 
        1000, 'standard', paramList)
    return noaa

def showDailyNormals(noaa, month, year, station):
    # functions to filter whole dataframe to retrive only records with specified parameter, and perfrom conversion 
    # format NOAA.df date attribute for hour and drop extraneous columns        
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][8:16]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    # iterate through list of parameters and conversion expressions
    paramList = [{'p':'DLY-DUTR-NORMAL', 'e':''},{'p':'DLY-DUTR-STDDEV', 'e':''},
        {'p':'DLY-PRCP-PCTALL-GE001HI', 'e':''},{'p':'DLY-PRCP-PCTALL-GE010HI', 'e':''},{'p':'DLY-PRCP-PCTALL-GE050HI', 'e':''},{'p':'DLY-PRCP-PCTALL-GE100HI', 'e':''},
        {'p':'DLY-SNOW-PCTALL-GE001TI', 'e':''},{'p':'DLY-SNOW-PCTALL-GE010TI', 'e':''},{'p':'DLY-SNOW-PCTALL-GE030TI', 'e':''},{'p':'DLY-SNOW-PCTALL-GE050TI', 'e':''},{'p':'DLY-SNOW-PCTALL-GE100TI','e':''},
        {'p':'DLY-SNWD-PCTALL-GE001WI', 'e':''},{'p':'DLY-SNWD-PCTALL-GE003WI', 'e':''},{'p':'DLY-SNWD-PCTALL-GE005WI', 'e':''},{'p':'DLY-SNWD-PCTALL-GE010WI', 'e':''},
        {'p':'DLY-TAVG-NORMAL', 'e':''},{'p':'DLY-TAVG-STDDEV', 'e':'*5'},{'p':'DLY-TMAX-NORMAL', 'e':''},{'p':'DLY-TMIN-NORMAL', 'e':''},
        {'p':'MTD-PRCP-NORMAL', 'e':''},{'p':'MTD-SNOW-NORMAL', 'e':''},{'p':'YTD-PRCP-NORMAL', 'e':''},{'p':'YTD-SNOW-NORMAL', 'e':''}]
    dfClean = getMergedDF(noaa.df, paramList)
    dailyNormalsPlots(dfClean, station , year, month)


def dailyNormalsPlots(df, station, year, month):
    # Final dataframe cleaning before plotting
    df['dayYear'] = df.apply(lambda d: (d['dayYear'][0:2]), axis=1)
    #df['dayYear'] = noaa.df.apply(lambda d: (d['dayYear'][8:10]), axis=1)
    df.drop(df.tail(1).index,inplace = True)
    st.write(f'<h4 style="text-align:center;margin-top:-30px;">Daily Normals Weather Data</h4>', unsafe_allow_html=True)
    WSF5c,WSF5e,WSF2c,WSF2e,AWNDc = '#1bab6b','#00542f','#72ab92','#00703f','#00ff8f'
    txtC = '#575757'
    # plot for daily precip percentiles
    # plot for hourly cloud coverage
    fig, ax = plt.subplots(figsize=(12,6))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    line1 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE001HI'], color = 'red', linewidth=3.0, alpha=0.7)
    line2 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE010HI'], color = 'orange', linewidth=3.0, alpha=0.7)
    line3 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE050HI'], color = 'yellow', linewidth=3.0, alpha=0.7)
    line4 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE100HI'], color = 'green', linewidth=3.0, alpha=0.7)
    plt.ylabel('%', fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [
        Line2D([0], [0], color='red', lw=3, label='DLY-PRCP-PCTALL-GE001HI'),
        Line2D([0], [0], color='orange', lw=3, label='DLY-PRCP-PCTALL-GE010HI'),
        Line2D([0], [0], color='yellow', lw=3, label='DLY-PRCP-PCTALL-GE050HI'),
        Line2D([0], [0], color='green', lw=3, label='DLY-PRCP-PCTALL-GE100HI'),
        ]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'Probability of Precip >= 0.01 in for 29-day windows - {month}'), fontsize=20, color=txtC, pad=30, )
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    #ax.set_ylim([0, 100])
    col1, col2 = st.columns([1,1])
    with col1:
        st.pyplot(fig)
    
    # plot for hourly cloud coverage
    fig, ax = plt.subplots(figsize=(12,6))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    Pc, Pe, Sc, Se = '#006be6','#001a38','#5d6875','#22262b'
    line1 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE001HI'], color = 'red', linewidth=3.0, alpha=0.7)
    line2 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE010HI'], color = 'orange', linewidth=3.0, alpha=0.7)
    line3 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE050HI'], color = 'yellow', linewidth=3.0, alpha=0.7)
    line4 = ax.plot(ind+width, df['DLY-PRCP-PCTALL-GE100HI'], color = 'green', linewidth=3.0, alpha=0.7)
    plt.ylabel('%', fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [
        Line2D([0], [0], color='red', lw=3, label='DLY-PRCP-PCTALL-GE001HI'),
        Line2D([0], [0], color='orange', lw=3, label='DLY-PRCP-PCTALL-GE010HI'),
        Line2D([0], [0], color='yellow', lw=3, label='DLY-PRCP-PCTALL-GE050HI'),
        Line2D([0], [0], color='green', lw=3, label='DLY-PRCP-PCTALL-GE100HI'),
        ]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'Probability of Precip >= 0.01 in for 29-day windows - {month}'), fontsize=20, color=txtC, pad=30, )
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    #ax.set_ylim([0, 100])
    with col2:
        st.pyplot(fig)
    
    # plot daily temperature normals
    fig, ax = plt.subplots(figsize=(12,6.1))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    mic, mie, mac, mae, lc = '#188bad','#0c303b','#fc6603','#662900','#4903fc' 
    bar1 = ax.bar(ind, df['DLY-TMAX-NORMAL'], width, color=mac, edgecolor=mae, linewidth=1, alpha=0.5)
    bar2 = ax.bar(ind+width, df['DLY-TMIN-NORMAL'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.5)
    #bar2 = ax.bar(ind, df['DLY-TAVG-STDDEV'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.7)
    line2 = ax.plot(ind+width, df['DLY-TAVG-NORMAL'], color = 'red', linewidth=3.0, alpha=0.5)
    line1 = ax.plot(ind+width, df['DLY-TAVG-STDDEV'], color = lc, linewidth=3.0, alpha=0.7)
    plt.ylabel('F',fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [Patch(facecolor=mac, edgecolor=mae, label='Daily Avg Temp Max'),
        Patch(facecolor=mic, edgecolor=mae, label='Daily Avg Temp Min'),
        Line2D([0], [0], color='red', lw=3, label='Daily Avg Temp '),
        Line2D([0], [0], color=lc, lw=3, label='Daily Avg Temp Standard Dev.(x * 0.5)')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'{station} - DAILY-TEMPERATURE-NORMALS - {month}'), fontsize=20, color='#575757',pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    ax.set_ylim([0, 100])
    cl1, cl2 = st.columns([1,1])
    with cl1:
        st.pyplot(fig)
    
    # plot daily temperature normals
    fig, ax = plt.subplots(figsize=(12,6.1))
    N = len(df.index)
    ind = np.arange(N) 
    width = 0.4
    mic, mie, mac, mae, lc = '#188bad','#0c303b','#fc6603','#662900','#4903fc' 
    #bar1 = ax.bar(ind, df['DLY-TMAX-NORMAL'], width, color=mac, edgecolor=mae, linewidth=1, alpha=0.5)
    #bar2 = ax.bar(ind+width, df['DLY-TMIN-NORMAL'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.5)
    #bar2 = ax.bar(ind, df['DLY-TAVG-STDDEV'], width, color = mic, edgecolor=mie, linewidth=1, alpha=0.7)
    line2 = ax.plot(ind+width, df['DLY-DUTR-NORMAL'], color = 'red', linewidth=3.0, alpha=0.5)
    line1 = ax.plot(ind+width, df['DLY-DUTR-STDDEV'], color = lc, linewidth=3.0, alpha=0.7)
    plt.ylabel('F',fontsize=12)
    plt.xticks(ind+width/2,df['dayYear'])
    legend_elements = [
        Line2D([0], [0], color='red', lw=3, label='Avg Daily Temp Range Std Dev.'),
        Line2D([0], [0], color=lc, lw=3, label='Daily Avg Temp Standard Dev.')]
    plt.legend(handles=legend_elements, fancybox=True, borderpad=0.7, framealpha=0.4, loc='upper right')
    plt.xticks(rotation = 90, fontsize=10) 
    plt.title((f'{station} - DAILY DIURNAL TEMPERATURE RANGE - {month}'), fontsize=20, color='#575757',pad=30)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    #ax.set_ylim([0, 100])
    with cl2:
        st.pyplot(fig)


### DAILY DATA SECTION

def getDailyData(noaa, m, y, s):
    mon = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    day = {'JAN':'01-31','FEB':'01-28','MAR':'01-31','APR':'01-30','MAY':'01-31','JUN':'01-30','JUL':'01-31','AUG':'01-31','SEP':'01-30','OCT':'01-31','NOV':'01-30','DEC':'01-31'}
    sta = {'OK CITY W ROGERS APT':'USW00013967','PENDLETON AIRPORT':'USW00024155','RALEIGH AIRPORT NC':'USW00013722'}                                         
    
    paramList = ['AWND','PRCP','SNOW','TAVG','TMAX','TMIN','WSF5','WSF2']
    noaa.stationDataParams('GHCND', (f'GHCND:{sta[s]}'), (f'{y}-{mon[m]}-{day[m][0:2]}') , (f'{y}-{mon[m]}-{day[m][3:5]}'), 1000, '', paramList)
    return noaa

def showDaily(noaa, station, year, month):
    noaa.df['dayYear'] = noaa.df.apply(lambda d: (d['date'][8:10]), axis=1)
    noaa.df = noaa.df.drop(['station','attributes','date'], axis=1)
    # iterate through list of parameters and conversion expressions
    paramList = [{'p':'AWND', 'e':'*.223694'},{'p':'PRCP', 'e':'*0.1'},
        {'p':'SNOW', 'e':'*0.1'},{'p':'TAVG', 'e':'*.18+32'},{'p':'TMAX', 'e':'*.18+32'},{'p':'TMIN', 'e':'*.18+32'},
        {'p':'WSF5', 'e':'*.223694'},{'p':'WSF2', 'e':'*.223694'},]
    dfClean = getMergedDF(noaa.df, paramList)
    dailyPlots(station, year,month, dfClean)

def dailyPlots(station, year, month, dfM):
    #st.write(f'<h1 style="text-align:center;margin-top:-100px;">{station}</h1>', unsafe_allow_html=True)
    st.write(f'<h4 style="text-align:center;margin:-40px;">Daily Weather Data</h4>', unsafe_allow_html=True)
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
  
### HOURLY NORMALS SECTION    
def getHourlyNormals(noaa,m,y,s,d):
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
    noaa.stationDataUnits('NORMAL_HLY', (f'GHCND:{sta[s]}'), (f'2010-{mon[m]}-{d}'), (f'2010-{mon[m2]}-{d2}'), 1000, 'standard')
    return noaa

def showHourlyNormals(noaa, station, year, month, day):
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
    hourlyNormalsPlots(dfClean, station,year,month)

def hourlyNormalsPlots(df, station, year, month):
    # Final dataframe cleaning before plotting
    df['dayYear'] = df.apply(lambda d: (d['dayYear'][3:16]), axis=1)
    df.drop(df.tail(1).index,inplace = True)
    #st.write(f'<h1 style="text-align:center;margin-top:-50px;">{station}</h1>', unsafe_allow_html=True)
    st.write(f'<h4 style="text-align:center;margin-top:-30px;">Hourly Normals Weather Data</h4>', unsafe_allow_html=True)
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
    plt.title((f'{station} - HOURLY WIND AVG - {month} 1981 - 2010'), fontsize=20, color='#575757', pad=30)
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
    plt.title((f'{station} - HOURLY CLOUD AVG - {month} 1981 - 2010'), fontsize=20, color=txtC, pad=30, )
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
    plt.title((f'{station} - HOURLY TEMP AVG - {month} 1981 - 2010'), fontsize=20, color='#575757',pad=30)
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


def changeStatus():
    #st.write(f'<h1 style="text-align:center;margin-top:-70px;">CHANGE STATUS</h1>', unsafe_allow_html=True)
    global viewState 
    viewState = 'MONTH'
    st.session_state.active = True

     # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), on_change=changeStation)     
    year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'), on_change=changeStatus)
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], on_change=changeStatus)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], on_change=changeDay)
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], on_change=changeDay)
    else:
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30','31'], on_change=changeDay)

    # show daily data for specific month/year 2021 - 2014
    noaa = NOAAData() 
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

    #show daily data for specific month/year 2021 - 2014 
    noaaDaily = getDailyData(noaa, month, year, station)
    showDaily(noaaDaily, station, year, month)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
    st.markdown('---')

def changeDay():
    #st.write(f'<h1 style="text-align:center;margin-top:-70px;">CHANGE STATUS</h1>', unsafe_allow_html=True)
    global viewState 
    viewState = 'DAY'
    st.session_state.active = True

     # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), on_change=changeStation)     
    year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'),on_change=changeStatus)
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], on_change=changeStatus)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], on_change=changeDay)
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], on_change=changeDay)
    else:
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30','31'], on_change=changeDay)

    # show daily data for specific month/year 2021 - 2014
    noaa = NOAAData() 
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

    #show daily data for specific month/year 2021 - 2014 
    noaaDaily = getDailyData(noaa, month, year, station)
    showDaily(noaaDaily, station, year, month)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
    st.markdown('---')

    # show hourly normals data
    noaaHourly = getHourlyNormals(noaa, month, year, station, day)
    showHourlyNormals(noaaHourly, station, year, month, day)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Hourly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

def changeStation():
    #st.write(f'<h1 style="text-align:center;margin-top:-70px;">CHANGE STATUS</h1>', unsafe_allow_html=True)
    global viewState 
    viewState = 'MONTH'
    st.session_state.active = True

     # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), on_change=changeStation)     
    # year = st.sidebar.selectbox(
    #     'SELECT YEAR',
    #     ('2021','2020','2019','2018','2017','2016','2015','2014'), on_change=changeStatus)
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], on_change=changeStatus)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], on_change=changeDay)
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], on_change=changeDay)
    else:
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30','31'], on_change=changeDay)
    year = 2010
    # show daily data for specific month/year 2021 - 2014 
    noaa = NOAAData()
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')


### MAIN APP FLOW
# page config
st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

if 'active' not in st.session_state:
    #st.write(f'<h1 style="text-align:center;margin-top:-70px;">DATAMINR SUPERBOWL ALERTS NOT ACTIVE</h1>', unsafe_allow_html=True)
    viewState = 'BASE'
    st.session_state.active = False

    # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), on_change=changeStation)     
    # year = st.sidebar.selectbox(
    #     'SELECT YEAR',
    #     ('2021','2020','2019','2018','2017','2016','2015','2014'), on_change=changeStatus)
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], on_change=changeStatus)
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
    year = 2010    
    noaa = NOAAData()
    # show daily data for specific month/year 2021 - 2014 
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')


### Data Function Workflow
# get NOAAData() class object auth
#noaa = NOAAData()

# show daily data for specific month/year 2021 - 2014 
# noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
# showMonthlyNormals(noaaMonthly, month, year, station)
# st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
# st.markdown('---')

# show daily data for specific month/year 2021 - 2014 
# noaaDaily = getDailyData(noaa, month, year, station)
# showDaily(noaa, station, year, month)
# st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
# st.markdown('---')

# show daily normals data
#noaaDailyNorms = getDailyNormalsData(noaa, month, year, station)
#showDailyNormals(noaa, month, year, station)
#st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Daily Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
#st.markdown('---')

# show hourly normals data
#noaaHourly = getHourlyNormals(noaa, month, year, station, day)
#showHourlyNormals(noaaHourly, station, year, month, day)
# st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Hourly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
# st.markdown('---')

