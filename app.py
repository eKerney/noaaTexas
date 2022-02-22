import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt 
from functools import reduce
import matplotlib as mpl
import time
from NOAA import *
from NOAAdataView import *
import scipy
from scipy import interpolate
from scipy.interpolate import make_interp_spline
#import seaborn as sns
mpl.rcParams['text.color'] = '#575757'
mpl.rcParams['axes.edgecolor'] = '#575757'
pd.options.mode.chained_assignment = None  # default='warn'

st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

def changeStatus():
    sta = {'PENDLETON AIRPORT':0, 'OK CITY W ROGERS APT':1,'RALEIGH AIRPORT NC':2}
    yr = {'2021':0,'2020':1,'2019':2,'2018':3,'2017':4,'2016':5,'2015':6,'2014':7}
    st.session_state.active = True
    # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
        on_change=changeStation, key='station', index=sta[st.session_state.station])
    year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'), 
        on_change=changeStatus, key='year',)# index=yr[st.session_state.year])     
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], 
        on_change=changeStatus, key='month', value=st.session_state.month)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], 
        on_change=changeDay, key='day',)# value=st.session_state.day28)
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], 
            on_change=changeDay, key='day30',)# value=st.session_state.day30)
    else:
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30','31'], 
            on_change=changeDay, key='day31',)# value=st.session_state.day31)

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
    sta = {'PENDLETON AIRPORT':0, 'OK CITY W ROGERS APT':1,'RALEIGH AIRPORT NC':2}
    st.session_state.active = True
    # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
        on_change=changeStation, key='station', index=sta[st.session_state.station])
    year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'), 
        on_change=changeStatus, key='year',)# value=st.session_state.year)     
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], 
        on_change=changeStatus, key='month', value=st.session_state.month)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], 
        on_change=changeDay, key='day28', )
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], 
            on_change=changeDay, key='day30', )
    else:
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30','31'], 
        on_change=changeDay, key='day31', )

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
    sta = {'PENDLETON AIRPORT':0, 'OK CITY W ROGERS APT':1,'RALEIGH AIRPORT NC':2}
    st.session_state.active = True
    # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
        on_change=changeStation, key='station', index=sta[st.session_state.station])     
    month = st.sidebar.select_slider(
        'SELECT MONTH',
        options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], 
        on_change=changeStatus, key='month', value=st.session_state.month)
    if month == 'FEB':
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28'], 
        on_change=changeDay, key='day28', value=st.session_state.day28)
    elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
        day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28','29','30'], 
            on_change=changeDay, key='day30', value=st.session_state.day30)
    else:
        day = st.sidebar.select_slider(
        'SELECT DAY',
        options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23','24','25','26','27','28','29','30','31'], 
        on_change=changeDay, key='day31', value=st.session_state.day31)
    # show daily data for specific month/year 2021 - 2014 
    noaa = NOAAData()
    noaaMonthly = getMonthlyNormalsData(noaa, month, st.session_state.year, station)
    showMonthlyNormals(noaaMonthly, month, st.session_state.year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

def main():
    if 'active' not in st.session_state:
        viewState = 'BASE'
        st.session_state.active = False
        st.session_state.station = 'PENDLETON AIRPORT'
        st.session_state.year = '2010'
        #st.session_state.month = 'JAN'
        st.session_state.day28 = '01'
        st.session_state.day30 = '01'
        st.session_state.day31 = '01'
        # sliders and widgets
        station = st.sidebar.selectbox(
            'SELECT STATION',
            ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
            on_change=changeStation, key='station')     
        month = st.sidebar.select_slider(
            'SELECT MONTH',
            options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], 
            on_change=changeStatus, key='month')
        if month == 'FEB':
            day = st.sidebar.select_slider(
            'SELECT DAY',
            options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','25','26','27','28'], 
            on_change=changeDay, key='day28')
        elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
            day = st.sidebar.select_slider(
                'SELECT DAY',
                options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
                '20','21','22','23','24','25','26','27','28','29','30'],
                on_change=changeDay, key='day30')
        else:
            day = st.sidebar.select_slider(
                'SELECT DAY',
                options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
                '20','21','22','23','24','25','26','27','28','29','30','31'],
            on_change=changeDay, key='day31') 
        noaa = NOAAData()
        # Fetch monthly summary data and show plots    
        noaaMonthly = getMonthlyNormalsData(noaa, month, st.session_state.year, station)
        showMonthlyNormals(noaaMonthly, month, st.session_state.year, station)

        st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
        st.markdown('---')

main()
