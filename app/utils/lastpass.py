"""
lastpass.py
date: March 3, 2026

Utility function to disable lastpass auto-fill on all input fields in the Streamlit app. 
This is necessary to prevent LastPass from interfering with the user experience, especially on dashboards / when filtering data.
"""


import streamlit as st

def disable_lastpass():
    st.markdown("""
        <script>
        const observer = new MutationObserver(() => {
            document.querySelectorAll('input').forEach(el => {
                el.setAttribute('data-lpignore', 'true');
                el.setAttribute('autocomplete', 'off');
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """, unsafe_allow_html=True)