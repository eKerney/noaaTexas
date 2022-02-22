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
    #st.write(f'<h1 style="text-align:center;margin-top:-70px;">CHANGE STATUS</h1>', unsafe_allow_html=True)
    global viewState 
    viewState = 'MONTH'
    st.session_state.active = True

     # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
        on_change=changeStation, key='station')     
    year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'), 
        on_change=changeStatus, key='year')
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
    viewState = 'STATION'
    st.session_state.active = True

     # sliders and widgets
    station = st.sidebar.selectbox(
        'SELECT STATION',
        ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), on_change=changeStation)     

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

def main():
    if 'active' not in st.session_state:
        viewState = 'BASE'
        st.session_state.active = False

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
        year = 2010    
        noaa = NOAAData()
        # show daily data for specific month/year 2021 - 2014 
        
        noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    
        
        showMonthlyNormals(noaaMonthly, month, year, station)

        st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
        st.markdown('---')

main()
