#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/css_utils.py
Utility functions for loading and managing CSS styles in Streamlit
"""

import streamlit as st
import os
from pathlib import Path

def load_css(file_path):
    """
    Load CSS file and inject it into Streamlit app
    
    Params:
        file_path (str): Path to the CSS file relative to the project root
        
    Returns:
        bool: True if CSS loaded successfully, False otherwise
    """
    try:
        # Handle both absolute and relative paths
        if not os.path.isabs(file_path):
            # Get the directory of the current script
            current_dir = Path(__file__).parent.parent
            css_path = current_dir / file_path
        else:
            css_path = Path(file_path)
        
        # Read and inject CSS
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        
        return True
        
    except FileNotFoundError:
        st.warning(f"⚠️ CSS file '{file_path}' not found. Using default styling.")
        return False
    except Exception as e:
        st.error(f"❌ Error loading CSS file: {str(e)}")
        return False

def load_multiple_css(file_paths):
    """
    Load multiple CSS files
    
    Args:
        file_paths (list): List of CSS file paths
        
    Returns:
        dict: Dictionary with file paths as keys and success status as values
    """
    results = {}
    for file_path in file_paths:
        results[file_path] = load_css(file_path)
    return results


def inject_css_string(css_string):
    """
    Inject CSS string directly into Streamlit app
    
    Args:
        css_string (str): CSS code as string
    """
    st.markdown(f'<style>{css_string}</style>', unsafe_allow_html=True)


def load_css_with_fallback(primary_css, fallback_css=None):
    """
    Load CSS with fallback option
    
    Args:
        primary_css (str): Primary CSS file path
        fallback_css (str, optional): Fallback CSS file path or CSS string
        
    Returns:
        bool: True if any CSS was loaded successfully
    """
    if load_css(primary_css):
        return True
    
    if fallback_css:
        if fallback_css.endswith('.css'):
            return load_css(fallback_css)
        else:
            # Assume it's a CSS string
            inject_css_string(fallback_css)
            return True
    
    return False


# Default fallback CSS for basic styling
DEFAULT_FALLBACK_CSS = """
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}

.info-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
}

.success-card {
    background: #d4edda;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}

.warning-card {
    background: #fff3cd;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 1rem 0;
}

.section-header {
    color: #4a4a4a;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
"""