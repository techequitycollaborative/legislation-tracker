#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advocacy Hub
Created on July 7, 2025
@author: danyasherbini

Page that features custom data from organizations using the Leg Tracker.
"""

import streamlit as st
import pandas as pd
from db.query import get_all_custom_bill_details
from utils.aggrid_styler import draw_advocacy_grid

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info from session state
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
user_email = st.session_state['user_email']

# Page title
st.title("📣 Advocacy Hub")

st.expander("About this page", icon="ℹ️", expanded=False).markdown(""" 
- This page displays custom advocacy information from organizations using the Legislation Tracker.
- Only organizations with access to the Legislation Tracker can view this data.
- You can filter the data by bill number and organization.
- You can edit or add custom advocacy details for bills from your organization's dashboard.                                                  
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")


records = get_all_custom_bill_details()

if records:
    df = pd.DataFrame(records)

    # Format dates
    df["last_updated_on"] = pd.to_datetime(df["last_updated_on"]).dt.date
    df["last_updated_at"] = pd.to_datetime(df["last_updated_at"]).dt.time

    col1, col2, col3 = st.columns([4.5,.25,3.25])

    with col1:
        with st.container(border=True):
            st.subheader("📣 Advocacy Details by Organization")
            st.markdown(" ")

            # Filters
            with st.container(border=True):
                    st.markdown("🔍 Filter")
                    
                    selected_bills = st.multiselect("Bill", sorted(df["bill_number"].dropna().unique()))
                    selected_orgs = st.multiselect("Organization", sorted(df["last_updated_org_name"].dropna().unique()))

                    if selected_bills:
                        df = df[df["bill_number"].isin(selected_bills)]
                    if selected_orgs:
                        df = df[df["last_updated_org_name"].isin(selected_orgs)]

            st.markdown(" ")

            # Configure AgGrid table -- using Streamlit data editor instead
            #draw_advocacy_grid(df)
            
            # Configure Streamlit dataframe
            desired_order = ["last_updated_on", "last_updated_org_name", "bill_number", "org_position", "priority_tier", "assigned_to",
                            "letter_of_support"]
            
            # Display only these columns in this order
            df_display = df[desired_order]

            # Sort by last_updated_on in descending order
            df = df.sort_values(by="last_updated_on", ascending=False)

            # Display table
            st.data_editor(
                df_display,
                use_container_width=True,
                column_config={
                    "last_updated_on": st.column_config.DateColumn("Last Updated", format="MM-DD-YYYY", help="Date when these details were last updated by the organization"),
                    "last_updated_org_name": st.column_config.Column("Organization", help="Organizations with access to the Legislation Tracker"),
                    "bill_number": st.column_config.Column("Bill Number"),
                    "org_position": st.column_config.Column("Position", help="Organization's position on the bill"),
                    "priority_tier": st.column_config.Column("Priority", help="Priority tier assigned to the bill by the organization"),
                    "assigned_to": st.column_config.Column("Point of Contact", help="Organization member assigned to this bill"),
                    "letter_of_support": st.column_config.LinkColumn("Letter of Support", display_text="Letter of Support", help="Letter of Support provided by the organization"),
                },
                hide_index=True,
                disabled=True  # Table is not editable
            )

    # Second column for vertical space between the two main sections
    with col2:
        st.markdown(" ")

    with col3:
        with st.container(border=True):
            
            st.subheader("📄 Letters of Support")
            st.markdown(" ")
            
            # Group letters by bill
            grouped = df[pd.notna(df["letter_of_support"])].groupby("bill_number")

            for bill_number, group in grouped:
                st.markdown(f"**{bill_number}**")
                for _, row in group.iterrows():
                    org_name = row["last_updated_org_name"]
                    letter_link = row["letter_of_support"]
                    st.markdown(f"- [{org_name}'s Letter of Support]({letter_link})")
                st.markdown("---")  # horizontal divider between bills



else:
    st.info("No custom details found.")