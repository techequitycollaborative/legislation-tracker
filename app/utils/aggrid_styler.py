#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ag Grid DataFrame Styler
Created on Oct 3, 2024
@author: danyasherbini

This script contains settings for interactive Ag Grid data frames on Streamlit, 
which are clickable/editable data tables.

"""

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from st_aggrid.shared import ColumnsAutoSizeMode


# Ag grid styler function for bills table
def draw_bill_grid(
        df,
        formatter: dict = None,
        selection='single',
        use_checkbox=True,
        #header_checkbox = True, -- don't need this since we are only doing single selection
        fit_columns=True, # change to true to make all columns the same width/fit to the table width
        theme='streamlit', # options = streamlit, alpine, balham, material
        height: int = 500,
        wrap_text: bool = True,
        auto_height: bool = False,
        key=None,
        css: dict = None
):

    # Initialize the GridOptionsBuilder from the dataframe passed into the function
    builder = GridOptionsBuilder().from_dataframe(df)
    
    # Configure default column settings for all columns
    builder.configure_default_column(
        enableFilter=True,
        filter='agTextColumnFilter',
        floatingFilter=True, # floating filter: adds a row under the header row for the filter
        #columnSize='sizeToFit'
        )
    
    # Configure special settings for certain columns (batch)
    builder.configure_columns(['full_text','leginfo_link','coauthors','bill_history','leg_session','bill_id','bill_topic','chamber'],hide=True) # hide these columns in the initial dataframe
    
    # Configure special settings for individual columns
    #builder.configure_column('checkbox', headerName='', checkboxSelection=True, width=50, pinned='left') # option to add a specific checkbox column
    #builder.configure_column('bill_id',headerName = 'Bill ID')
    builder.configure_column('bill_number',headerName = 'Bill Number',pinned='left', checkboxSelection=True) # pin this column, make it the checkbox column
    builder.configure_column('bill_name',headerName = 'Bill Name') # set width of column
    builder.configure_column('author',headerName = 'Author')
    builder.configure_column('coauthors',headerName = 'Coauthor(s)')
    builder.configure_column('status',headerName = 'Status')
    builder.configure_column('leginfo_link',headerName = 'Link')
    builder.configure_column('leg_session',headerName = 'Session')
    builder.configure_column('date_introduced',headerName = 'Date Introduced')#,filter='agDateColumnFilter') # text filter for now
    builder.configure_column('chamber',headerName = 'Chamber',filter='agSetColumnFilter')
    builder.configure_column('full_text',headerName = 'Bill Text')
    builder.configure_column('bill_history',headerName = 'Bill History')
    builder.configure_column('bill_topic',headerName = 'Bill Topic', filter='agSetColumnFilter')
    
    
    builder.configure_selection(selection_mode=selection, use_checkbox=use_checkbox) # Configure how user selects rows
    builder.configure_side_bar(filters_panel=True, columns_panel=False) # configure the sidebar panel
    #builder.configure_pagination(enabled=True, paginationAutoPageSize=True, paginationPageSize=10) # can add pagination instead of making the table scrollable
    builder.configure_auto_height(autoHeight=False) # configure height of the table
    
    # Build the grid options dictionary
    grid_options = builder.build()

    return AgGrid(
        df,
        gridOptions=grid_options, # pass the grid options dictionary built above
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED, # ensures the df is updated dynamically
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns, # fit all columns equally on page load
        height=height,
        wrap_text=wrap_text,
        theme=theme,
        key=key,
        css=css
    )


# Ag grid styler function for legislators table
def draw_leg_grid(
        df,
        formatter: dict = None,
        #selection='single', -- selection turned off for legislators table
        #use_checkbox=True, -- turned off for legislators table
        #header_checkbox = True, -- turned off for legislators table
        fit_columns=True, # change to false to make all column width based on the variable
        theme='streamlit', # options = streamlit, alpine, balham, material
        height: int = 600,
        wrap_text: bool = False,
        auto_height: bool = False,
        key=None,
        css: dict = None
):

    # Initialize the GridOptionsBuilder from the dataframe passed into the function
    builder = GridOptionsBuilder().from_dataframe(df)
    
    # Configure default column settings for all columns
    builder.configure_default_column(
        enableFilter=True,
        filter='agTextColumnFilter',
        floatingFilter=True, # floating filter: adds a row under the header row for the filter
        columnSize='sizeToFit'
        )
    
    # Configure special settings for certain columns (batch)
    builder.configure_columns(['legislator_id'],hide=True)
    
    # Configure special settings for individual columns 
    builder.configure_column('name',pinned='left',headerName = 'Name')
    builder.configure_column('district',headerName = 'District',filter='agNumberColumnFilter', headerClass='left-align-header') # left align to make sure column header is justified left like the rest of the columns
    builder.configure_column('party',headerName = 'Party',filter='agSetColumnFilter')
    builder.configure_column('chamber',headerName = 'Chamber',filter='agSetColumnFilter')
    
    # Configure how user selects rows -- turned off for legislators table
    #builder.configure_selection(selection_mode=selection, use_checkbox=use_checkbox) # no selection needed for legislator table
    builder.configure_auto_height(autoHeight=False) # configure height of the table
    
    # Build the grid options dictionary
    grid_options = builder.build()

    return AgGrid(
        df,
        gridOptions=grid_options, # pass the grid options dictionary built above
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED, # ensures the df is updated dynamically
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns,
        height=height,
        theme=theme,
        key=key,
        css=css
    )

