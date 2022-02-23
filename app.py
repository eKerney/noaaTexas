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

def addMonths():
    noaa = NOAAData()
    st.session_state.active = True
    # Fetch monthly summary data and show plots    
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

    #show daily data for specific month/year 2021 - 2014 
    noaaDaily = getDailyData(noaa, month, year, station)
    showDaily(noaaDaily, station, year, month)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
    st.markdown('---')

def addDays():
    noaa = NOAAData()
    st.session_state.active = True
    # Fetch monthly summary data and show plots    
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

def showYears():
    noaa = NOAAData()
    st.session_state.active = True
    # Fetch monthly summary data and show plots    
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, st.session_state.station)
    showMonthlyNormals(noaaMonthly, month, year, st.session_state.station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')
    
    #show daily data for specific month/year 2021 - 2014 
    noaaDaily = getDailyData(noaa, month, st.session_state.year, st.session_state.station)
    showDaily(noaaDaily, st.session_state.station, st.session_state.year, month)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
    st.markdown('---')

def showStations():
    noaa = NOAAData()
    st.session_state.active = True
    # Fetch monthly summary data and show plots    
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, st.session_state.station)
    showMonthlyNormals(noaaMonthly, month, year, st.session_state.station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')
    
    #show daily data for specific month/year 2021 - 2014 
    noaaDaily = getDailyData(noaa, month, st.session_state.year, st.session_state.station)
    showDaily(noaaDaily, st.session_state.station, st.session_state.year, month)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - Daily Land Surface Observations </p>', unsafe_allow_html=True)
    st.markdown('---')

# sliders and widgets
station = st.sidebar.selectbox(
    'SELECT STATION',
    ('PENDLETON AIRPORT','OK CITY W ROGERS APT','RALEIGH AIRPORT NC'), 
    on_change=showStations, key='station')     
year = st.sidebar.selectbox(
        'SELECT YEAR',
        ('2021','2020','2019','2018','2017','2016','2015','2014'), 
        on_change=showStations, key='year',)# index=yr[st.session_state.year])     
month = st.sidebar.select_slider(
    'SELECT MONTH',
    options=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG','SEP','OCT','NOV','DEC'], 
    on_change=addMonths, key='month')
if month == 'FEB':
    day = st.sidebar.select_slider(
    'SELECT DAY',
    options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24','25','26','27','28'], 
    on_change=addDays, key='day28')
elif month=='APR' or month=='JUN' or month=='SEP' or month=='NOV':
    day = st.sidebar.select_slider(
    'SELECT DAY',
    options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24','25','26','27','28','29','30'],
    on_change=addDays, key='day30')
else:
    day = st.sidebar.select_slider(
    'SELECT DAY',
    options=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24','25','26','27','28','29','30','31'],
    on_change=addDays, key='day31') 

if 'active' not in st.session_state:
    noaa = NOAAData()
    # Fetch monthly summary data and show plots    
    noaaMonthly = getMonthlyNormalsData(noaa, month, year, station)
    showMonthlyNormals(noaaMonthly, month, year, station)
    st.write(f'<p style="text-align:center;margin-bottom:0px">Data: NOAA Global Historical Climate Network (GHCN) - U.S. Monthly Climate Normals 1981-2010 </p>', unsafe_allow_html=True)
    st.markdown('---')

