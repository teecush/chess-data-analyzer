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

def get_win_rate_color(win_rate):
    """Get color based on win rate"""
    if win_rate <= 20:
        return 'red'
    elif win_rate <= 35:
        return 'pink'
    elif win_rate <= 65:
        return 'yellow'
    elif win_rate <= 80:
        return 'lightgreen'
    elif win_rate <= 95:
        return 'darkgreen'
    else:
        return 'blue'

def create_opening_statistics_table(opening_df):
    """Create detailed opening statistics table with color coding"""
    if opening_df.empty:
        return pd.DataFrame()
    
    # Calculate statistics for each opening
    stats = opening_df.groupby('Opening').agg({
        'Result': 'count',
        'Variation': 'nunique'
    }).rename(columns={'Result': 'Games', 'Variation': 'Variations'})
    
    # Calculate wins, losses, draws
    wins = opening_df.groupby('Opening').apply(
        lambda x: (x['Result'].str.lower() == 'win').sum()
    )
    losses = opening_df.groupby('Opening').apply(
        lambda x: (x['Result'].str.lower() == 'loss').sum()
    )
    draws = opening_df.groupby('Opening').apply(
        lambda x: (x['Result'].str.lower() == 'draw').sum()
    )
    
    # Calculate win rates
    win_rates = opening_df.groupby('Opening').apply(
        lambda x: (x['Result'].str.lower() == 'win').sum() / len(x) * 100
    )
    
    # Calculate side statistics
    white_games = opening_df.groupby('Opening').apply(
        lambda x: (x['Side'].str.upper().isin(['W', 'WHITE'])).sum()
    )
    black_games = opening_df.groupby('Opening').apply(
        lambda x: (x['Side'].str.upper().isin(['B', 'BLACK'])).sum()
    )
    
    # Combine all statistics
    stats['Wins'] = wins
    stats['Losses'] = losses
    stats['Draws'] = draws
    stats['Win_Rate'] = win_rates.round(1)
    stats['White'] = white_games
    stats['Black'] = black_games
    
    # Sort by total games
    stats = stats.sort_values('Games', ascending=False)
    
    return stats

def create_opening_sunburst(opening_df):
    """Create interactive sunburst chart"""
    if opening_df.empty:
        return go.Figure()
    
    # Group by opening and variation
    tree_data = opening_df.groupby(['Opening', 'Variation']).agg({
        'Result': 'count'
    }).reset_index()
    tree_data.columns = ['Opening', 'Variation', 'Games']
    
    # Calculate win rates separately
    win_rates = opening_df.groupby(['Opening', 'Variation']).apply(
        lambda x: (x['Result'].str.lower() == 'win').sum() / len(x) * 100
    ).reset_index()
    win_rates.columns = ['Opening', 'Variation', 'Win_Rate']
    
    # Merge the data
    tree_data = tree_data.merge(win_rates, on=['Opening', 'Variation'])
    
    # Create sunburst chart
    fig = go.Figure(data=[go.Sunburst(
        ids=tree_data['Opening'] + ' - ' + tree_data['Variation'],
        labels=tree_data['Variation'],
        parents=tree_data['Opening'],
        values=tree_data['Games'],
        branchvalues='total',
        hovertemplate='<b>%{label}</b><br>Games: %{value}<br>Win Rate: %{customdata:.1f}%<extra></extra>',
        customdata=tree_data['Win_Rate'],
        marker=dict(
            colors=tree_data['Win_Rate'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Win Rate (%)")
        )
    )])
    
    fig.update_layout(
        title="Opening Results (All Games)",
        height=600,
        template='plotly_white'
    )
    
    return fig

def create_opening_treemap(opening_df):
    """Create interactive treemap chart"""
    if opening_df.empty:
        return go.Figure()
    
    # Group by opening and variation
    tree_data = opening_df.groupby(['Opening', 'Variation']).agg({
        'Result': 'count'
    }).reset_index()
    tree_data.columns = ['Opening', 'Variation', 'Games']
    
    # Calculate win rates separately
    win_rates = opening_df.groupby(['Opening', 'Variation']).apply(
        lambda x: (x['Result'].str.lower() == 'win').sum() / len(x) * 100
    ).reset_index()
    win_rates.columns = ['Opening', 'Variation', 'Win_Rate']
    
    # Merge the data
    tree_data = tree_data.merge(win_rates, on=['Opening', 'Variation'])
    
    # Create treemap chart
    fig = go.Figure(data=[go.Treemap(
        ids=tree_data['Opening'] + ' - ' + tree_data['Variation'],
        labels=tree_data['Variation'],
        parents=tree_data['Opening'],
        values=tree_data['Games'],
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Games: %{value}<br>Win Rate: %{customdata:.1f}%<extra></extra>',
        customdata=tree_data['Win_Rate'],
        marker=dict(
            colors=tree_data['Win_Rate'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Win Rate (%)")
        )
    )])
    
    fig.update_layout(
        title="Opening Treemap (All Games)",
        height=600,
        template='plotly_white'
    )
    
    return fig

def create_opening_flow(opening_df):
    """Create Sankey-like flow diagram"""
    if opening_df.empty:
        return go.Figure()
    
    # This would be a more complex Sankey diagram
    # For now, return a placeholder
    fig = go.Figure()
    fig.add_annotation(
        text="Opening Flow Diagram - Coming Soon",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(
        title="Opening Flow Diagram",
        height=400,
        template='plotly_white'
    )
    return fig

def create_opening_explorer(df):
    """Create opening explorer interface with all chart types"""
    st.subheader("Opening Analysis")
    
    if df is None or df.empty:
        st.info("No data available for opening analysis")
        return
    
    # Extract opening data
    opening_df = extract_opening_data(df)
    
    if opening_df.empty:
        st.info("No opening data found in PGN. Opening analysis requires PGN data with opening tags.")
        return
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistics Table", "🌞 Sunburst", "🗺️ Treemap", "🌊 Flow"])
    
    with tab1:
        st.subheader("Opening Statistics")
        
        # Show color legend
        st.markdown("**Win Rate Color Legend:**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown("🔴 ≤20%")
        with col2:
            st.markdown("🟡 20-35%")
        with col3:
            st.markdown("🟡 35-65%")
        with col4:
            st.markdown("�� 65-80%")
        with col5:
            st.markdown("🟢 80-95%")
        with col6:
            st.markdown("🔵 >95%")
        
        # Create and display statistics table
        stats = create_opening_statistics_table(opening_df)
        if not stats.empty:
            st.dataframe(stats, use_container_width=True)
            
            # Add download button
            csv = stats.to_csv(index=True)
            st.download_button(
                label="📥 Download Opening Statistics",
                data=csv,
                file_name="opening_statistics.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Opening Sunburst")
        st.plotly_chart(create_opening_sunburst(opening_df), use_container_width=True)
        st.caption("Interactive hierarchical view of openings and variations")
    
    with tab3:
        st.subheader("Opening Treemap")
        st.plotly_chart(create_opening_treemap(opening_df), use_container_width=True)
        st.caption("Rectangular hierarchical view of opening performance")
    
    with tab4:
        st.subheader("Opening Flow")
        st.plotly_chart(create_opening_flow(opening_df), use_container_width=True)
        st.caption("Flow diagram showing opening transitions (coming soon)")
