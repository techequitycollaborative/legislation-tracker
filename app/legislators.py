#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legislator Page
Created on Oct 2, 2024
@author: danyasherbini

This page of the app contains legislator information.
"""

import numpy as np
import streamlit as st
from db.query import query_table
from utils import aggrid_styler
from utils.utils import to_csv


# Show the page title and description
st.title('Legislators')
st.write(
    '''
    This page shows California legislators for the 2023-2024 legislative session. 
    '''
)

# Query data
legislators = query_table('ca_dev', 'legislator')

# Clean data
legislators['chamber'] = np.where(legislators['chamber_id']==1,'Assembly','Senate') # change chamber id to actual chamber values
legislators = legislators.drop(['legislator_id','chamber_id'],axis=1) # drop these two columns
   
# Make the aggrid dataframe
data = aggrid_styler.draw_leg_grid(legislators)

# Button to download data as csv file       
st.download_button(key='legislators_download',
                   label='Download Full Data as CSV',
                   data=to_csv(data['data']),
                   file_name='output.csv',
                   mime='text/csv'
                   )

