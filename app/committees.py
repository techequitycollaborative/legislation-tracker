#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Committees Page
Created on May 5, 2025
@author: jessiclassy

Bills page with:
    - Committee table
    - Committee details with text
"""

import numpy as np
import pandas as pd
import streamlit as st
from db.query import query_table
from utils import aggrid_styler
from utils.utils import to_csv
from utils.display_utils import display_committee_info_text

# Page title and description
st.title('Committees')
st.write(
    '''
    This page shows California assembly and senate committee information. 
    Please note that the page may take a few moments to load.
    '''
)

############################ LOAD AND PROCESS COMMITTEE DATA #############################
# Load committee membership data
def get_and_clean_committee_data():
    """
    Use query_table to load, clean, and cache committee data, which requires membership and legislator data is pre-loaded
    """
    # Cache the function that retrieves the data
    @st.cache_data
    def get_legislators():
        # Query the database for legislators
        legislators = query_table('ca_dev', 'legislator')
        legislators = legislators.drop(columns=["openstates_people_id"])
        return legislators
    
    # Cache the function that retrieves the data
    @st.cache_data
    def get_memberships(legislators):
        # Query the database for memberships and apply legislator names
        memberships = query_table('ca_dev', 'committee_assignment')
        memberships = memberships.drop(['committee_assignment_id', 'session'],axis=1) # drop the unneeded ID columns
        legislators = legislators.rename(columns={"name": "legislator_name"})
        memberships = memberships.merge(legislators, on='legislator_id')
        return memberships
    
    @st.cache_data
    def get_committees(memberships):
        # Query the database for committee table
        committees = query_table('ca_dev', 'committee')
        # join membership data points on committee names
        memberships = memberships.merge(committees, on='committee_id')

        # prepare empty columns
        committees["chair_name"] = ""
        committees["next_hearing"] = ""
        committees["size"] = 0

        # fill columns
        for committee_name, group in memberships.groupby("name"):
            curr_idx = committees.loc[committees.name==committee_name].index[0]
            # fill in committee size
            committee_size = len(group)
            committees.loc[curr_idx, ["size"]] = committee_size

            # fill in Chairperson name iff exists
            has_chair = group.assignment_type == "Chair"
            if any(has_chair):
                chairperson_idx = group[has_chair].index[0]
                chairperson_name = memberships.loc[chairperson_idx, ["legislator_name"]]
                committees.loc[curr_idx, ["chair_name"]] = chairperson_name.legislator_name
        
        committees['chamber'] = np.where(committees['chamber_id']==1,'Assembly','Senate') # change chamber id to actual chamber values
        committees = committees.drop(['chamber_id'],axis=1) # drop chamber ID column
        return committees
    
    # Call the cached function to get the data
    legislators = get_legislators()
    memberships = get_memberships(legislators)
    committees = get_committees(memberships)

    return committees

committees = get_and_clean_committee_data()

# # Initialize session state for selected bills
if 'selected_committees' not in st.session_state:
    st.session_state.selected_committees = []
    
# # Create a two-column layout
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("")

with col2:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(committees),
            file_name='selected_committees.csv',
            mime='text/csv',
            use_container_width=True
        )

# # Display the aggrid table
data = aggrid_styler.draw_committee_grid(committees)
    
selected_rows = data.selected_rows

if selected_rows is not None and len(selected_rows) != 0:
        display_committee_info_text(selected_rows)


