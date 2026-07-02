# All columns in the bill table
BILL_COLUMNS = [
    'openstates_bill_id', 
    'bill_number', 
    'bill_name', 
    'status', 
    'date_introduced', 
    'leg_session',
    'author', 
    'coauthors', 
    'chamber', 
    'leginfo_link', 
    'bill_text', 
    'bill_history',
    'bill_event', 
    'event_text',
    'assigned_topics',
    'last_updated_on'
]

# All columns in the committee table
COMMITTEE_COLUMNS = [
    "committee_id",
    "committee_name",
    "chamber",
    "next_hearing",
    "committee_chair",
    "committee_vice_chair",
    "total_members",
    "webpage_link", 
    "chamber_id", 
    "committee_members",
    "member_count"
]

# All columns in the legislator view
LEGISLATOR_COLUMNS = [
    "openstates_people_id",
    "name",
    "party",
    "chamber",
    "district",
    "other_names",
    "ext_sources",
    "office_details",
    "issue_contacts",
    "last_updated_on"
]
# All columns for org dashboard (bill details + custom org details)
BILL_COLUMNS_WITH_DETAILS = [
    'openstates_bill_id',
    'bill_number',
    'bill_name',
    'status',
    'date_introduced',
    'leg_session',
    'author',
    'coauthors',
    'chamber',
    'leginfo_link',
    'bill_text',
    'bill_history',
    'bill_event',
    'event_text',
    'assigned_topics',
    'last_updated_on',
    'org_id',
    'org_position',
    'assigned_to',
    'changed_on',
]