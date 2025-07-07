#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/bill_history.py
Created on Oct 15, 2024
@author: danyasherbini

Utility function for reformatting Bill History.

"""
import re


def format_bill_history(bill_history):
    '''
    Reformats bill_history variable into a descending chronological list for the bill history section of the bill details page.
    '''
    if not bill_history:
        return ""

    # Split entries using ", " (assuming this is how they are separated)
    entries = bill_history.split(", ")

    # Process entries into tuples (date, event)
    formatted_entries = []
    for entry in entries:
        # Ensure the format is `YYYY-MM-DD >> Event`
        match = re.match(r"^(\d{4}-\d{2}-\d{2})\s*>>\s*(.+)", entry)
        if match:
            date, event = match.groups()
            formatted_entries.append((date, event))

    # Sort by date in descending order
    formatted_entries.sort(reverse=True, key=lambda x: x[0])

    # Format back into readable Markdown-style text
    return "\n\n".join([f"**{date}:** {event}" for date, event in formatted_entries])


##########################################################################################################################################

def format_bill_history_dashboard(bill_history):
    '''
    Reformats bill_history variable into a descending chronological list for the bill history section of the DASHBOARD bill details page.
    '''
    if not bill_history:
        return ""

    # Split entries by new lines
    entries = bill_history.strip().split("\n")

    formatted_entries = []
    for entry in entries:
        # Match date and event in the format: YYYY-MM-DD: Event
        match = re.match(r"^(\d{4}-\d{2}-\d{2}):\s*(.+)", entry)
        if match:
            date, event = match.groups()
            formatted_entries.append((date, event))

    # Sort entries by date in descending order
    formatted_entries.sort(reverse=True, key=lambda x: x[0])

    # Format back into readable Markdown-style text
    return "\n\n".join([f"**{date}:** {event}" for date, event in formatted_entries])

