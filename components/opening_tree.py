"""
Opening tree visualization component for Chess Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re

def create_opening_tree_visualization(df):
    """Create opening tree visualization"""
    st.subheader("Opening Tree Visualization")
    
    if df is None or df.empty:
        st.info("No data available for opening tree visualization")
        return
    
    # Extract opening data from PGN
    if 'PGN' not in df.columns:
        st.info("PGN data required for opening tree visualization")
        return
    
    openings = []
    variations = []
    
    # Extract opening information from PGN
    opening_pattern = r'\[Opening\s+"([^"]+)"\]'
    variation_pattern = r'\[Variation\s+"([^"]+)"\]'
    
    for pgn in df['PGN']:
        if pd.isna(pgn) or not pgn:
            continue
            
        opening_match = re.search(opening_pattern, pgn)
        opening = opening_match.group(1) if opening_match else "Unknown"
        
        variation_match = re.search(variation_pattern, pgn)
        variation = variation_match.group(1) if variation_match else "Main Line"
        
        openings.append(opening)
        variations.append(variation)
    
    # Create opening tree data
    opening_df = pd.DataFrame({'Opening': openings, 'Variation': variations})
    
    if opening_df.empty:
        st.info("No opening data found in PGN")
        return
    
    # Create tree visualization
    tree_data = opening_df.groupby(['Opening', 'Variation']).size().reset_index(name='Count')
    
    fig = go.Figure(data=[go.Treemap(
        ids=tree_data['Opening'] + ' - ' + tree_data['Variation'],
        labels=tree_data['Variation'],
        parents=tree_data['Opening'],
        values=tree_data['Count'],
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Games: %{value}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Opening Tree Structure",
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show opening statistics
    with st.expander("Opening Statistics"):
        opening_stats = opening_df.groupby('Opening').size().sort_values(ascending=False)
        st.dataframe(opening_stats.reset_index().rename(columns={0: 'Games'}), use_container_width=True)
