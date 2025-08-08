"""
Debug utilities for Chess Analytics Dashboard
"""

import streamlit as st
import pandas as pd

def debug_data_loading(df):
    """Debug data loading issues"""
    st.write("### Debug Information")
    
    if df is None:
        st.error("Data is None")
        return
    
    st.write(f"**DataFrame Shape:** {df.shape}")
    st.write(f"**Columns:** {list(df.columns)}")
    
    # Check for PGN column
    if 'PGN' in df.columns:
        pgn_count = df['PGN'].notna().sum()
        st.write(f"**PGN entries:** {pgn_count}")
        
        # Show sample PGN data
        if pgn_count > 0:
            st.write("**Sample PGN data:**")
            sample_pgn = df[df['PGN'].notna()]['PGN'].iloc[0]
            st.code(sample_pgn[:200] + "..." if len(sample_pgn) > 200 else sample_pgn)
    else:
        st.warning("No PGN column found")
    
    # Check for other important columns
    important_cols = ['Result', 'Side', 'Date']
    for col in important_cols:
        if col in df.columns:
            st.write(f"**{col} values:** {df[col].value_counts().to_dict()}")
        else:
            st.write(f"**Missing column:** {col}")
