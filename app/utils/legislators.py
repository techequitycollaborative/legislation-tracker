#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/bills.py
Created on Jul 7, 2025
@author: jessiclassy

Function for displaying legislator details on the Legislators Page.

"""
import streamlit as st
import pandas as pd
from db.query import get_custom_contact_details_with_timestamp, LEGISLATOR_COLUMNS

##### HELPER FUNCTIONS
# Styling the staffer contact rows
COLOR_SCHEME = {
    "office": {
        "background": "#FFFFFF",  # white
        "border": "#B8D9FF",
        "text": "#003366"
    },
    "committee": {
        "background": "#FFFFFF",  # White
        "border": "#ffe1e1",
        "text": "#9c0202"
    },
    "user": {
        "background": "#E6FFE6",  # Light green
        "border": "#B8FFB8",
        "text": "#006600"
    }
}

FILTER_SCHEME = {
    "Codex (automatic)": ["office", "committee"],
    "Office": ["office"],
    "Committee": ["committee"],
    "User-added": ["user"]
}
def apply_row_style(row):
    color = COLOR_SCHEME[row['staffer_type']]
    return [f"background-color: {color['background']}; color: {color['text']}"] * len(row)

def staffer_filter(df):
    # Create filter controls in columns at the top
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        issue_filter = st.multiselect(
            "Filter by Issue Area",
            options=sorted(df['issue_area'].unique()),
            default=None,
            placeholder="All issues"
        )
    
    with filter_col2:
        staffer_filter = st.text_input(
            "Filter by Staffer Name",
            placeholder="Type to search..."
        )
    
    with filter_col3:
        contact_type = st.selectbox(
            "Contact Type",
            options=["All", "Codex (automatic)", "Office", "Committee", "User-added"],
            index=0
        )

    # Apply filters
    filtered_df = df.copy()
    if issue_filter:
        filtered_df = filtered_df[filtered_df['issue_area'].isin(issue_filter)]
    if staffer_filter:
        filtered_df = filtered_df[
            filtered_df['staffer_contact'].str.contains(staffer_filter, case=False, na=False)
        ]
    if contact_type != "All":
        filtered_df = filtered_df[filtered_df['staffer_type'].isin(FILTER_SCHEME[contact_type])]
    return filtered_df

def staffer_directory_tab(df):
    # filtered_df = staffer_filter(df)
    # Display the filtered table
    st.dataframe(
        # filtered_df,
        df.style.apply(apply_row_style, axis=1),
        column_config={
            "issue_area": "Issue Area",
            "staffer_contact": "Primary Contact",
            "auto_email": "Default Email",
            "custom_contact": "Custom Contact",
            "custom_email": "Custom Email",
            "people_contact_id": None,
            "staffer_type": None
        },
        use_container_width=True,
        height=600,
        hide_index=True
    )

    # 5. Quick stats and export
    col1, col2, col3 = st.columns([4, 3, 1])
    with col1:
        st.caption(f"Showing {len(df)} of {len(st.session_state.contact_df)} records. Only visible records are exported.")
    with col2:
        st.markdown('')
    with col3:
        st.download_button(
            "Export Contacts to CSV",
            df.to_csv(index=False),
            "contacts.csv",
            "text/csv"
        )

def issue_editor_tab(df, openstates_people_id, org_id, org_name, user_email):
    with st.form("bulk_edit_form"):
        edited_df = st.data_editor(
            df.style.apply(apply_row_style, axis=1),
            disabled=["people_contact_id", "issue_area", "staffer_contact", "auto_email", "staffer_type"],
            column_config={
                "custom_contact": st.column_config.TextColumn("Custom Contact"),
                "custom_email": st.column_config.TextColumn("Custom Email"),
                "people_contact_id": None,
                "staffer_type": None,
                "issue_area": "Issue Area",
                "staffer_contact": "Codex Contact",
                "auto_email": "Auto-generated email"
            },
            use_container_width=True,
            hide_index=True,
            height=600
        )
        if st.form_submit_button("💾 Save All Changes"):

            # Get non-null rows for DB update
            changed_df = edited_df.loc[edited_df.custom_email.notnull() & edited_df.custom_contact.notnull()]
            changed_df.staffer_type = "user"
            st.session_state.contact_df.update(changed_df)

            # Update DB
            if save_custom_contact_details_with_timestamp(changed_df, openstates_people_id, user_email, org_id, org_name):
                st.success("Custom details updated")
                st.rerun()

##### CONTROLLER FUNCTION
def display_legislator_info_text(selected_rows):
    '''
    Displays legislator information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Ensure values align with expected order of LEGISLATOR_COLUMNS, which is necessary for proper db querying
    assert selected_rows.columns.tolist() == LEGISLATOR_COLUMNS 

    ## SELECTING DATA POINTS FROM STREAMLIT STATE
    openstates_people_id = selected_rows['openstates_people_id'].iloc[0] 
    name = selected_rows['name'].iloc[0]
    party = selected_rows['party'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    district = selected_rows['district'].iloc[0]
    other_names = selected_rows['other_names'].iloc[0]
    ext_sources = selected_rows['ext_sources'].iloc[0]
    office_details = selected_rows['office_details'].iloc[0]
    issue_contacts = selected_rows['issue_contacts'].iloc[0]
    last_updated = selected_rows['last_updated_on'].iloc[0]

    # Access user info from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']
    user_email = st.session_state['user_email']

    ## TRANSFORMING FOR DISPLAY
    #### Legislator name(s)
    display_name = " ".join(name.split(", ")[::-1]) # reorder name parts
    display_other_names = '- ' + other_names.replace("; ", "\n- ") # add newlines and hyphens for bullet formatting
    
    #### Office details
    distinct_offices = set([o for o in office_details.split("\\n")]) # get unique set of offices
    display_offices = [d.split('@@') for d in distinct_offices] # split unique offices by separator characters

     #### Last updated date
    # Format dates MM-DD-YYYY in the bill details
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'

    # # Display Legislator Info Below the Table
    st.markdown(f"#### {display_name} ({chamber[0]}D {district} - {party.title()})")

    # Display other names as a pop-over
    with st.popover(f"_Other names_"):
        if other_names is not None:
            st.markdown(display_other_names)
        else:
            st.markdown('_No other recognized names._')

    st.caption(f"Last updated on {last_updated}")

    # OFFICES
    with st.container(border=True):
        st.markdown("##### Office Details")
        # Create an expander for each office
        for i, contents in enumerate(display_offices):
            office_name = f"**{contents[0]}**" # Write office name
            st.markdown(office_name)
            expander = st.expander('Click to view')
            with st.container(key=f"office_text_{i}"):
                phone_address = "\n\n".join(contents[1:])
                expander.write(phone_address)

    #### Codex details
    # Codex extracted contacts

    codex_data = issue_contacts.split("\\n") # Split up aggregated data points

    # Transform into unified dataframe for display and editing
    contact_df = pd.DataFrame(columns=["people_contact_id", "issue_area", "staffer_type", "staffer_contact", "auto_email", "custom_contact", "custom_email"])
    # Loop over the codex data
    for cd in codex_data:
        # extract contents of each contact data point
        snapshot_data = cd.split("@@")
        # extract relevant custom details
        contact_df.loc[len(contact_df)] = snapshot_data + [None, None] # add dummy value for custom details to fill in later

    # If custom data is not None, merge by people_contact_id
    with st.spinner("Loading custom contacts..."):
        custom_contact_data = get_custom_contact_details_with_timestamp(openstates_people_id) # a list of dictionaries
    if custom_contact_data != None:
        for ccd in custom_contact_data:
            # Update existing rows if possible
            contact_df.loc[contact_df.people_contact_id == str(ccd["people_contact_id"]), ["staffer_type", "custom_contact", "custom_email"]] = ["user", ccd["custom_staffer_contact"], ccd["custom_staffer_email"]]
    
    # Update session state by selection
    if st.session_state.selected_person != openstates_people_id:
        st.session_state.selected_person = openstates_people_id
        st.session_state.contact_df = contact_df
        st.session_state.filtered_df = contact_df
        st.rerun()

    with st.container(border=True):
        st.markdown('##### Staffers by Issue Area')
        # Filter columns of directory before generating tab(s)
        st.session_state.filtered_df = staffer_filter(st.session_state.contact_df)
        if st.session_state['org_id'] == 1: # Contact editor only for TechEquity folks
            # Tab layout to view and edit
            tab1, tab2 = st.tabs(["Directory View", "Contact Editor"])
                
            with tab1:
                staffer_directory_tab(st.session_state.filtered_df)
            
            with tab2:
                issue_editor_tab(st.session_state.filtered_df, openstates_people_id, org_id, org_name, user_email)
        else: # If not TechEquity, only display (interim)
            st.subheader('Staffer Directory View')
            staffer_directory_tab(st.session_state.filtered_df)

    if ext_sources is not None:
        with st.popover("_External sources_"):
            for source_link in ext_sources.split("\\n"):
                # remove URL prefixes >> split on slashes >> build base URL
                source_name = '.'.join(source_link.replace("https://", "").replace("www.", "").split("/")[0].split(".")[-4:])
                st.link_button(source_name, str(source_link))
    else:
        st.markdown('#### ')
        st.markdown('')
    