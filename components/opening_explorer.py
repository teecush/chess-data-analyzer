"""
Opening explorer component for Chess Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import re

def extract_opening_data(df):
    """Extract opening information from PGN data"""
    if df is None or 'PGN' not in df.columns:
        return pd.DataFrame()
    
    openings = []
    variations = []
    results = []
    sides = []
    
    # Regular expressions to extract opening and variation info from PGN
    opening_pattern = r'\[Opening\s+"([^"]+)"\]'
    variation_pattern = r'\[Variation\s+"([^"]+)"\]'
    
    for idx, row in df.iterrows():
        pgn = row.get('PGN', '')
        if pd.isna(pgn) or not pgn:
            continue
            
        # Extract opening
        opening_match = re.search(opening_pattern, pgn)
        opening = opening_match.group(1) if opening_match else "Unknown Opening"
        
        # Extract variation if present
        variation_match = re.search(variation_pattern, pgn)
        variation = variation_match.group(1) if variation_match else "Main Line"
        
        # Get result and side
        result = row.get('Result', 'Unknown')
        side = row.get('Side', 'Unknown')
        
        openings.append(opening)
        variations.append(variation)
        results.append(result)
        sides.append(side)
    
    # Create dataframe with opening data
    opening_df = pd.DataFrame({
        'Opening': openings,
        'Variation': variations,
        'Result': results,
        'Side': sides
    })
    
    return opening_df

def create_opening_circle_chart(opening_df):
    """Create circle chart showing opening popularity"""
    if opening_df.empty:
        return go.Figure()
    
    # Count openings
    opening_counts = opening_df['Opening'].value_counts()
    
    # Create circle chart
    fig = go.Figure(data=[go.Scatter(
        x=opening_counts.values,
        y=opening_counts.index,
        mode='markers',
        marker=dict(
            size=opening_counts.values * 2,  # Size based on frequency
            color=opening_counts.values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Frequency")
        ),
        text=opening_counts.values,
        hovertemplate='<b>%{y}</b><br>Games: %{text}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Opening Popularity (Circle Chart)",
        xaxis_title="Number of Games",
        yaxis_title="Opening",
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_opening_rectangle_chart(opening_df):
    """Create rectangle chart showing opening performance"""
    if opening_df.empty:
        return go.Figure()
    
    # Calculate win rates for each opening
    opening_stats = opening_df.groupby('Opening').agg({
        'Result': lambda x: (x.str.lower() == 'win').sum() / len(x) * 100,
        'Result': 'count'
    }).rename(columns={'Result': 'Win_Rate'})
    opening_stats['Game_Count'] = opening_df.groupby('Opening').size()
    
    # Filter openings with at least 2 games
    opening_stats = opening_stats[opening_stats['Game_Count'] >= 2]
    
    if opening_stats.empty:
        return go.Figure()
    
    # Create rectangle chart
    fig = go.Figure(data=[go.Bar(
        x=opening_stats.index,
        y=opening_stats['Win_Rate'],
        marker_color=opening_stats['Game_Count'],
        text=opening_stats['Win_Rate'].round(1).astype(str) + '%',
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<br>Games: %{marker.color}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Opening Performance (Win Rate)",
        xaxis_title="Opening",
        yaxis_title="Win Rate (%)",
        height=400,
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    return fig

def create_opening_tree_diagram(opening_df):
    """Create tree diagram showing opening variations"""
    if opening_df.empty:
        return go.Figure()
    
    # Group by opening and variation
    tree_data = opening_df.groupby(['Opening', 'Variation']).size().reset_index(name='Count')
    
    # Create hierarchical structure
    fig = go.Figure(data=[go.Treemap(
        ids=tree_data['Opening'] + ' - ' + tree_data['Variation'],
        labels=tree_data['Variation'],
        parents=tree_data['Opening'],
        values=tree_data['Count'],
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Games: %{value}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Opening Tree Diagram",
        height=500,
        template='plotly_white'
    )
    
    return fig

def create_opening_explorer(df):
    """Create opening explorer interface with all three chart types"""
    st.subheader("Opening Analysis")
    
    if df is None or df.empty:
        st.info("No data available for opening analysis")
        return
    
    # Extract opening data
    opening_df = extract_opening_data(df)
    
    if opening_df.empty:
        st.info("No opening data found in PGN. Opening analysis requires PGN data with opening tags.")
        return
    
    # Create tabs for different chart types
    tab1, tab2, tab3 = st.tabs(["Circle Chart", "Performance Chart", "Tree Diagram"])
    
    with tab1:
        st.plotly_chart(create_opening_circle_chart(opening_df), use_container_width=True)
        st.caption("Circle size indicates opening popularity")
    
    with tab2:
        st.plotly_chart(create_opening_rectangle_chart(opening_df), use_container_width=True)
        st.caption("Bar height shows win rate, color intensity shows number of games")
    
    with tab3:
        st.plotly_chart(create_opening_tree_diagram(opening_df), use_container_width=True)
        st.caption("Hierarchical view of openings and their variations")
    
    # Show opening statistics table
    with st.expander("Opening Statistics Table"):
        if not opening_df.empty:
            stats = opening_df.groupby('Opening').agg({
                'Result': 'count',
                'Variation': 'nunique'
            }).rename(columns={'Result': 'Total Games', 'Variation': 'Variations'})
            
            # Add win rate
            win_rates = opening_df.groupby('Opening').apply(
                lambda x: (x['Result'].str.lower() == 'win').sum() / len(x) * 100
            )
            stats['Win Rate (%)'] = win_rates.round(1)
            
            st.dataframe(stats, use_container_width=True)
