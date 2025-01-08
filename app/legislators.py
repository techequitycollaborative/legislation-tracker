#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page
Created on Oct 2, 2024
@author: danyasherbini

This page of the app contains bill information.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
from utils import aggrid_styler
from utils.utils import to_csv



PATH = '/Users/danyasherbini/Documents/GitHub/lt-streamlit'
os.chdir(PATH)
os.getcwd()


# Show the page title and description
#st.set_page_config(page_title='Legislation Tracker', layout='wide') #can add page_icon argument
st.title('Legislators')
st.write(
    '''
    This page shows California legislators for the 2023-2024 legislative session. 
    '''
)

############################ LOAD AND SET UP DATA #############################

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_leg_data():
    legislators = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/legislators.csv')
    legislators['chamber'] = np.where(legislators['chamber_id']==1,'Assembly','Senate')
    legislators = legislators.drop(['chamber_id'],axis=1)
    return legislators

legislators = load_leg_data()

   
# Make the aggrid dataframe
data = aggrid_styler.draw_leg_grid(legislators)

# Button to download data as csv file       
st.download_button(key='legislators_download',
                   label='Download Full Data as CSV',
                   data=to_csv(data['data']),
                   file_name='output.csv',
                   mime='text/csv'
                   )

