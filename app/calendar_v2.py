"""
Interactive Calendar V2 - Built with streamlit-calendar
Uses JSON endpoint from calendar-feed and existing DB functions for notes
Assumes authentication already handled in parent app (session state has user_email, org_id, org_name)
"""

import streamlit as st
import requests
from datetime import datetime, date
from streamlit_calendar import calendar
import pytz

# Import your existing DB functions
from db.query import (
    get_custom_bill_details_with_timestamp,
    save_custom_bill_details_with_timestamp
)

# Configuration
LOCAL_TZ = pytz.timezone("America/Los_Angeles")
API_BASE_URL = "http://10.0.0.218:5001"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_hearings_from_api(token: str, feed_type: str = "user", identifier: str = None) -> list:
    """
    Fetch hearings from your Flask JSON endpoint.
    
    Args:
        token: User's auth token for calendar-feed
        feed_type: One of "user", "org", "working_group"
        identifier: org_id, or token depending on feed_type
    
    Returns:
        List of hearing objects from the API
    """
    try:
        # Build URL based on feed type
        if feed_type == "org":
            url = f"{API_BASE_URL}/feed/org/{token}/json"
        else:
            url = f"{API_BASE_URL}/feed/user/{token}/json"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Return the hearings list (adjust based on your json_builder output)
        return data.get("hearings", [])
    
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch hearings: {str(e)}")
        return []


def hearings_to_calendar_events(hearings: list) -> list:
    """
    Convert hearing data to FullCalendar event format.
    Stores bill data and hearing metadata in extendedProps for the modal.
    """
    events = []
    
    for hearing in hearings:
        # Determine event color based on committee or priority (customize as needed)
        # You could add logic here like:
        # - Color by committee
        # - Color by number of bills
        # - Color by priority level
        color = "#3788d8"  # Default blue
        
        # Build event based on all-day or time-specific
        if hearing.get("is_allday", False):
            start_date = hearing.get("date")
            if not start_date:
                continue
                
            event = {
                "id": str(hearing["id"]),
                "title": hearing.get("name", f"Hearing {hearing['id']}"),
                "start": start_date,
                "allDay": True,
                "color": color,
            }
        else:
            # Time-specific hearing
            hearing_date = hearing.get("date")
            hearing_time = hearing.get("time")
            
            if not hearing_date or not hearing_time:
                continue
                
            # Combine date and time
            # Handle different time formats
            if "T" in str(hearing_time):
                start_datetime = str(hearing_time)
            else:
                # Assume time is in HH:MM:SS or HH:MM format
                start_datetime = f"{hearing_date}T{hearing_time}"
            
            event = {
                "id": str(hearing["id"]),
                "title": hearing.get("name", f"Hearing {hearing['id']}"),
                "start": start_datetime,
                "allDay": False,
                "color": color,
            }
        
        # Add extended props with all hearing data for the modal
        event["extendedProps"] = {
            "hearing_id": hearing["id"],
            "hearing_name": hearing.get("name"),
            "location": hearing.get("location"),
            "room": hearing.get("room"),
            "time_verbatim": hearing.get("time_verbatim"),
            "notes": hearing.get("notes"),
            "bills": hearing.get("bills", []),  # List of bill objects
        }
        
        events.append(event)
    
    return events


def get_bill_custom_details_with_org(bill_number: str, openstates_bill_id: str, org_id: int) -> dict:
    """
    Wrapper for get_custom_bill_details_with_timestamp that handles None returns.
    """
    result = get_custom_bill_details_with_timestamp(openstates_bill_id, org_id)
    if result is None:
        return {
            "org_position": "",
            "priority_tier": "",
            "community_sponsor": "",
            "coalition": "",
            "letter_of_support": "",
            "assigned_to": "",
            "action_taken": "",
            "last_updated_by": "",
            "last_updated_org_id": org_id,
            "last_updated_org_name": "",
            "last_updated_on": date.today(),
            "last_updated_at": datetime.now(),
        }
    return result


def show_bill_notes_form(bill: dict, hearing_id: int, org_id: int, user_email: str, org_name: str):
    """
    Display a compact form for editing a single bill's custom details.
    """
    # Determine openstates_bill_id
    openstates_bill_id = bill.get('openstates_bill_id', bill.get('number'))
    
    # Fetch existing custom details
    existing_details = get_bill_custom_details_with_org(
        bill['number'], 
        openstates_bill_id, 
        org_id
    )
    
    # Create a more compact form with 2-column layout
    with st.form(key=f"bill_form_{bill['number']}_{hearing_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            org_position = st.selectbox(
                "Position",
                options=["", "Support", "Oppose", "Neutral", "Watch"],
                index=["", "Support", "Oppose", "Neutral", "Watch"].index(
                    existing_details.get("org_position", "")
                ) if existing_details.get("org_position") in ["", "Support", "Oppose", "Neutral", "Watch"] else 0,
                key=f"org_pos_{bill['number']}_{hearing_id}"
            )
            
            priority_tier = st.selectbox(
                "Priority",
                options=["", "Tier 1", "Tier 2", "Tier 3"],
                index=["", "Tier 1", "Tier 2", "Tier 3"].index(
                    existing_details.get("priority_tier", "")
                ) if existing_details.get("priority_tier") in ["", "Tier 1", "Tier 2", "Tier 3"] else 0,
                key=f"priority_{bill['number']}_{hearing_id}"
            )
            
            assigned_to = st.text_input(
                "Assigned To",
                value=existing_details.get("assigned_to", ""),
                key=f"assigned_{bill['number']}_{hearing_id}"
            )
        
        with col2:
            community_sponsor = st.text_input(
                "Sponsor",
                value=existing_details.get("community_sponsor", ""),
                key=f"sponsor_{bill['number']}_{hearing_id}"
            )
            
            coalition = st.text_input(
                "Coalition",
                value=existing_details.get("coalition", ""),
                key=f"coalition_{bill['number']}_{hearing_id}"
            )
            
            letter_of_support = st.text_input(
                "Letter URL",
                value=existing_details.get("letter_of_support", ""),
                placeholder="https://...",
                key=f"letter_{bill['number']}_{hearing_id}"
            )
        
        # Full width action taken
        action_taken = st.text_area(
            "Action Taken / Notes",
            value=existing_details.get("action_taken", ""),
            height=80,
            key=f"action_{bill['number']}_{hearing_id}"
        )
        
        # Last updated info in small text
        if existing_details.get("last_updated_by"):
            st.caption(
                f"🕐 Last updated by {existing_details['last_updated_by']} on {existing_details['last_updated_on']}"
            )
        
        # Submit button row
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("💾 Save Notes", type="primary", use_container_width=True)
        
        if submitted:
            try:
                save_custom_bill_details_with_timestamp(
                    bill_number=bill['number'],
                    org_position=org_position,
                    priority_tier=priority_tier,
                    community_sponsor=community_sponsor,
                    coalition=coalition,
                    openstates_bill_id=openstates_bill_id,
                    assigned_to=assigned_to,
                    action_taken=action_taken,
                    user_email=user_email,
                    org_id=org_id,
                    org_name=org_name
                )
                st.success(f"✅ Saved!", icon="✅")
                
                # Clear cache and refresh
                st.cache_data.clear()
                import time
                time.sleep(0.5)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_hearing_modal(hearing_data: dict, org_id: int, user_email: str, org_name: str):
    """
    Display a modal showing all bills in a hearing with their note forms.
    """
    hearing_id = hearing_data["hearing_id"]
    hearing_name = hearing_data["hearing_name"]
    bills = hearing_data.get("bills", [])
    
    @st.dialog(f"📋 {hearing_name}", width="large")
    def hearing_modal_content():
        # Add a unique key to prevent duplicate rendering
        modal_key = f"modal_{hearing_id}_{datetime.now().timestamp()}"
        
        # Hearing metadata in expandable section (saves space)
        with st.expander("📌 Hearing Details", expanded=False):
            st.caption(f"🆔 ID: {hearing_id}")
            
            location_parts = []
            if hearing_data.get("location"):
                location_parts.append(hearing_data["location"])
            if hearing_data.get("room"):
                location_parts.append(hearing_data["room"])
            if location_parts:
                st.info(f"📍 {', '.join(location_parts)}")
            
            if hearing_data.get("time_verbatim"):
                st.info(f"⏰ {hearing_data['time_verbatim']}")
            
            if hearing_data.get("notes"):
                st.markdown(f"**📝 Notes:** {hearing_data['notes']}")
        
        if not bills:
            st.warning("No bills found for this hearing.")
            if st.button("Close", type="primary", use_container_width=True):
                st.session_state["show_hearing_modal"] = False
                st.rerun()
            return
        
        # Better interface for many bills - add search/filter
        st.subheader(f"📜 Bills ({len(bills)})")
        
        # Add search box for bills
        search_term = st.text_input("🔍 Filter bills", placeholder="Search by bill number or name...", key=f"search_{hearing_id}")
        
        # Filter bills based on search
        filtered_bills = bills
        if search_term:
            search_lower = search_term.lower()
            filtered_bills = [
                b for b in bills 
                if search_lower in b['number'].lower() or 
                (b.get('name') and search_lower in b['name'].lower())
            ]
            st.caption(f"Showing {len(filtered_bills)} of {len(bills)} bills")
        
        # Option 1: Use accordion/expandable sections instead of tabs (better for many bills)
        st.info("💡 Tip: Expand each bill below to add notes")
        
        for idx, bill in enumerate(filtered_bills):
            bill_number = bill['number']
            bill_name = bill.get('name', '')
            display_title = f"{bill_number}"
            if bill_name:
                # Truncate long names
                short_name = bill_name[:60] + "..." if len(bill_name) > 60 else bill_name
                display_title = f"{bill_number} - {short_name}"
            
            with st.expander(f"📄 {display_title}", expanded=False):
                show_bill_notes_form(bill, hearing_id, org_id, user_email, org_name)
        
        # Close button at bottom
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✓ Done", type="primary", use_container_width=True):
                st.session_state["show_hearing_modal"] = False
                st.rerun()
    
    # Call the dialog function
    hearing_modal_content()
    
    # CRITICAL: Clear the modal trigger after showing
    # This prevents the modal from reopening immediately
    st.session_state["modal_just_closed"] = True


def calendar_page():
    """
    Main calendar page with eventClick handling.
    Assumes authentication already handled - reads from session state.
    """
    
    # Read authentication from session state (already set by parent app)
    user_email = st.session_state.get('user_email')
    org_id = st.session_state.get('org_id')
    org_name = st.session_state.get('org_name')
    
    # Validate session state
    if not user_email:
        st.error("❌ User email not found in session. Please log in again.")
        return
    
    if not org_id:
        st.error("❌ Organization ID not found in session. Please log in again.")
        return
    
    # Page config (only needed if this is the main page)
    # If this is embedded, you might want to skip this
    try:
        st.set_page_config(
            page_title="Legislative Hearing Calendar",
            page_icon="📅",
            layout="wide"
        )
    except:
        pass  # set_page_config can only be called once
    
    st.title("📅 Legislative Hearing Calendar")
    st.caption("Click on any hearing to add or edit bill notes")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Calendar Settings")
        
        # Calendar feed token (you'll need to get this from your auth system)
        # You might store this in session state as well
        token = st.text_input(
            "Calendar Feed Token", 
            type="password", 
            key="calendar_token",
            help="Enter your calendar feed access token"
        )
        
        # Feed type selector
        feed_type = st.selectbox(
            "Feed Type",
            options=["user", "org", "committee", "working_group"],
            key="feed_type",
            help="Select which feed to display"
        )
        
        # Identifier based on feed type
        identifier = None
        if feed_type == "org":
            identifier = org_id
        
        st.divider()
        
        # Calendar view options
        st.subheader("📆 Display Options")
        initial_view = st.selectbox(
            "Default View",
            options=["dayGridMonth", "dayGridWeek", "listMonth"],
            index=0,
            key="initial_view"
        )
        
        show_weekends = st.checkbox("Show Weekends", value=True, key="show_weekends")
        
        st.divider()
        
        # Refresh button
        if st.button("🔄 Refresh Calendar", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Show session info (debug)
        with st.expander("ℹ️ Session Info"):
            st.caption(f"User: {user_email}")
            st.caption(f"Org ID: {org_id}")
            st.caption(f"Org Name: {org_name}")
    
    # Validate required fields
    if not token:
        st.warning("⚠️ Please enter your calendar feed token in the sidebar to view hearings.")
        st.info("💡 Your calendar feed token can be obtained from your account settings.")
        return
    
    # Fetch hearings
    with st.spinner("📅 Loading hearings..."):
        hearings = fetch_hearings_from_api(token, feed_type, identifier if identifier else None)
    
    if not hearings:
        st.info("ℹ️ No hearings found for this feed. Try a different feed type or check your token.")
        return
    
    # Convert to calendar events
    events = hearings_to_calendar_events(hearings)
    
    # Calendar configuration
    calendar_options = {
        "editable": False,  # Users cannot add/edit hearings
        "selectable": False,  # No date range selection
        "initialView": initial_view,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek,listMonth"
        },
        "height": "auto",
        "weekends": show_weekends,
        "slotMinTime": "08:00:00",
        "slotMaxTime": "20:00:00",
        "eventDisplay": "block",
        "eventTimeFormat": {
            "hour": "numeric",
            "minute": "2-digit",
            "meridiem": "short"
        },
        "nowIndicator": True,  # Shows current time line in week/day view
    }
    
    # Custom CSS for better event styling
    custom_css = """
    .fc-event {
        cursor: pointer;
        transition: transform 0.1s ease;
    }
    .fc-event:hover {
        transform: scale(1.02);
        filter: brightness(0.95);
    }
    .fc-event-title {
        font-weight: 500;
    }
    """
    
    # Render calendar
    calendar_data = calendar(
        events=events,
        options=calendar_options,
        key="hearing_calendar",
        custom_css=custom_css
    )
    
    # Handle event clicks
    if calendar_data and calendar_data.get("callback") == "eventClick":
        # Only open modal if we're not just coming from a close
        if not st.session_state.get("modal_just_closed", False):
            clicked_event = calendar_data["eventClick"]["event"]
            extended_props = clicked_event.get("extendedProps", {})
            
            # Store in session state and show modal
            st.session_state["selected_hearing"] = extended_props
            st.session_state["show_hearing_modal"] = True
    
    # Reset the modal_just_closed flag after a short delay
    if st.session_state.get("modal_just_closed", False):
        # Use a small delay to reset the flag
        import time
        time.sleep(0.1)
        st.session_state["modal_just_closed"] = False
    
    # Show modal if needed
    if st.session_state.get("show_hearing_modal", False):
        show_hearing_modal(
            hearing_data=st.session_state["selected_hearing"],
            org_id=org_id,
            user_email=user_email,
            org_name=org_name
        )
        # Clear the trigger after showing
        st.session_state["show_hearing_modal"] = False


# Entry point for when this file is run directly
if __name__ == "__main__":
    calendar_page()