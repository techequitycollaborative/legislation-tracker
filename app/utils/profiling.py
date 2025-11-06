import time
import logging
import traceback
import streamlit as st
from functools import wraps
from contextlib import contextmanager

# Globals - turn off in production
PROFILING_ENABLED = True # TODO: add this to credentials/config?
MAX_TIMINGS = 50

# Set up logging for console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s'
)
logger = logging.getLogger(__name__)

def init_profiling():
    """Initialize profiling session state. Call this once at app startup."""
    if 'timings' not in st.session_state:
        st.session_state.timings = []
    if 'rerun_count' not in st.session_state:
        st.session_state.rerun_count = {}
    if 'event_count' not in st.session_state:
        st.session_state.event_count = {}


def track_rerun(page_name):
    """
    Track page reruns. Call this at the top of each page function.
    
    Args:
        page_name: Name of the page (e.g., "Info", "Dashboard", "Login")
    """
    if not PROFILING_ENABLED:
        return
    
    # Initialize rerun counter
    if 'rerun_count' not in st.session_state:
        st.session_state.rerun_count = {}
    
    # Increment counter for this page
    if page_name not in st.session_state.rerun_count:
        st.session_state.rerun_count[page_name] = 0
    st.session_state.rerun_count[page_name] += 1
    
    count = st.session_state.rerun_count[page_name]
    logger.info(f"🔄 PAGE RERUN: {page_name} (rerun #{count})")
    
    # Display rerun counter in UI
    st.caption(f"🔄 {page_name} page - Rerun #{count}")

def track_event(label):
    """
    Track specific user interactions or events that may trigger reruns.
    Useful for debugging row selection or callbacks.
    """
    if not PROFILING_ENABLED:
        return
    
    if 'event_count' not in st.session_state:
        st.session_state.event_count = {}
    
    if label not in st.session_state.event_count:
        st.session_state.event_count[label] = 0
    st.session_state.event_count[label] += 1
    
    count = st.session_state.event_count[label]
    logger.info(f"🔹 EVENT: {label} (trigger #{count})")
    
    # Display in UI
    st.caption(f"🔹 {label} - Trigger #{count}")

@contextmanager
def timer(label):
    """Context manager for timing code blocks with optional stack trace logging"""
    if not PROFILING_ENABLED:
        yield
        return

    start = time.time()
    logger.info(f"START: {label}")
    
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"END: {label} - {duration:.3f}s")
        
        if 'timings' not in st.session_state:
            st.session_state.timings = []
        st.session_state.timings.append((label, duration, time.time()))
        
        # Cap timings to MAX_TIMINGS
        if len(st.session_state.timings) > MAX_TIMINGS:
            st.session_state.timings = st.session_state.timings[-MAX_TIMINGS:]
        
        # Optional stack trace for debugging
        stack_summary = traceback.format_stack(limit=3)
        logger.debug(f"Stack for {label}:\n{''.join(stack_summary)}")


def profile(label):
    """Decorator for timing functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not PROFILING_ENABLED:
                return func(*args, **kwargs)
            
            start = time.time()
            logger.info(f"START: {label}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"END: {label} - {duration:.3f}s")
                
                if 'timings' not in st.session_state:
                    st.session_state.timings = []
                st.session_state.timings.append((label, duration, time.time()))
                
                # Cap timings
                if len(st.session_state.timings) > MAX_TIMINGS:
                    st.session_state.timings = st.session_state.timings[-MAX_TIMINGS:]
                
                return result
            except Exception as e:
                logger.error(f"ERROR: {label} - {str(e)}")
                raise
        return wrapper
    return decorator

def show_performance_metrics():
    """Display performance metrics in a collapsible expander"""
    if not PROFILING_ENABLED:
        return
    
    if 'timings' in st.session_state and st.session_state.timings:
        with st.expander("⏱️ Performance Metrics", expanded=False):
            # Show rerun counts
            if 'rerun_count' in st.session_state:
                st.subheader("Page Reruns")
                for page, count in st.session_state.rerun_count.items():
                    st.text(f"🔄 {page}: {count} reruns")
                st.divider()
            
            # Show event triggers
            if 'event_count' in st.session_state and st.session_state.event_count:
                st.subheader("Event Triggers")
                for event, count in st.session_state.event_count.items():
                    st.text(f"🔹 {event}: {count} triggers")
                st.divider()
            
            # Show last 15 timing operations
            st.subheader("Recent Timings")
            recent = st.session_state.timings[-15:]
            for label, duration, _ in recent:
                # Color code by duration
                if duration < 0.5:
                    color = "🟢"
                elif duration < 2:
                    color = "🟡"
                else:
                    color = "🔴"
                st.text(f"{color} {label}: {duration:.3f}s")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear metrics"):
                    st.session_state.timings = []
                    st.session_state.rerun_count = {}
                    st.session_state.event_count = {}
                    st.rerun()
            with col2:
                total_time = sum(d for _, d, _ in recent)
                st.metric("Total Time", f"{total_time:.2f}s")