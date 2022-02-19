import streamlit as st
import requests
import pandas as pd
import getpass

@st.cache(allow_output_mutation=True)
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

   # @st.cache(suppress_st_warning=True)
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

    def stationDataParams(self, dataSetID, stationID, startDate, endDate, limit, units, datatypeid):
        req_type = 'data'
        params = {'datasetid': dataSetID, 'stationid': stationID, 'startdate': startDate, 'enddate': endDate, 'limit': limit, 'units': units, 'datatypeid': datatypeid}
        data = self.poll_api(req_type, params)
        self.df = pd.DataFrame(data)
        return self.df

    def filterDF(self, param):
        dfFiltered = self.df[self.df.datatype == param ]
        return dfFiltered
