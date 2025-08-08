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
    """Create interactive circle chart showing opening popularity"""
    if opening_df.empty:
        return go.Figure()
    
    # Count openings
    opening_counts = opening_df['Opening'].value_counts()
    
    # Calculate win rates for color coding
    opening_stats = opening_df.groupby('Opening').agg({
        'Result': lambda x: (x.str.lower() == 'win').sum() / len(x) * 100
    }).rename(columns={'Result': 'Win_Rate'})
    
    # Create interactive bubble chart
    fig = go.Figure(data=[go.Scatter(
        x=opening_counts.values,
        y=opening_counts.index,
        mode='markers',
        marker=dict(
            size=opening_counts.values * 3,  # Larger bubbles
            color=opening_stats['Win_Rate'],
            colorscale='RdYlGn',  # Red to Green scale
            showscale=True,
            colorbar=dict(title="Win Rate (%)"),
            line=dict(width=2, color='white'),
            sizeref=2.0,
            sizemin=10
        ),
        text=opening_counts.values,
        customdata=opening_stats['Win_Rate'],
        hovertemplate='<b>%{y}</b><br>Games: %{text}<br>Win Rate: %{customdata:.1f}%<extra></extra>',
        name='Openings'
    )])
    
    fig.update_layout(
        title="Interactive Opening Popularity",
        xaxis_title="Number of Games",
        yaxis_title="Opening",
        height=500,
        template='plotly_white',
        hovermode='closest',
        dragmode='pan',
        showlegend=False
    )
    
    # Add interactive features
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig

def create_opening_rectangle_chart(opening_df):
    """Create interactive rectangle chart showing opening performance"""
    if opening_df.empty:
        return go.Figure()
    
    # Calculate comprehensive stats for each opening
    opening_stats = opening_df.groupby('Opening').agg({
        'Result': lambda x: (x.str.lower() == 'win').sum() / len(x) * 100,
        'Result': 'count'
    }).rename(columns={'Result': 'Win_Rate'})
    opening_stats['Game_Count'] = opening_df.groupby('Opening').size()
    opening_stats['Total_Games'] = opening_stats['Game_Count']
    
    # Filter openings with at least 2 games
    opening_stats = opening_stats[opening_stats['Game_Count'] >= 2]
    
    if opening_stats.empty:
        return go.Figure()
    
    # Create interactive rectangle chart with multiple metrics
    fig = go.Figure()
    
    # Add bars with interactive features
    fig.add_trace(go.Bar(
        x=opening_stats.index,
        y=opening_stats['Win_Rate'],
        marker=dict(
            color=opening_stats['Win_Rate'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Win Rate (%)")
        ),
        text=opening_stats['Win_Rate'].round(1).astype(str) + '%',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<br>Games: %{customdata}<extra></extra>',
        customdata=opening_stats['Game_Count'],
        name='Win Rate'
    ))
    
    # Add game count as secondary metric
    fig.add_trace(go.Scatter(
        x=opening_stats.index,
        y=opening_stats['Game_Count'],
        mode='markers',
        marker=dict(size=opening_stats['Game_Count'], color='blue', opacity=0.6),
        yaxis='y2',
        name='Game Count',
        hovertemplate='<b>%{x}</b><br>Games: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Interactive Opening Performance Analysis",
        xaxis_title="Opening",
        yaxis_title="Win Rate (%)",
        yaxis2=dict(title="Number of Games", overlaying='y', side='right'),
        height=500,
        template='plotly_white',
        xaxis_tickangle=-45,
        hovermode='x unified',
        showlegend=True,
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig

def create_opening_tree_diagram(opening_df):
    """Create interactive tree diagram showing opening variations"""
    if opening_df.empty:
        return go.Figure()
    
    # Group by opening and variation with more detailed stats
    tree_data = opening_df.groupby(['Opening', 'Variation']).agg({
        'Result': 'count',
        'Result': lambda x: (x.str.lower() == 'win').sum() / len(x) * 100
    }).reset_index()
    tree_data.columns = ['Opening', 'Variation', 'Games', 'Win_Rate']
    
    # Create interactive sunburst chart instead of treemap
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
        title="Interactive Opening Tree Structure",
        height=600,
        template='plotly_white',
        sunburstcolorway=['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a'],
        extendsunburstcolors=True
    )
    
    return fig

def create_opening_explorer(df):
    """Create opening explorer interface with all three interactive chart types"""
    st.subheader("Opening Analysis")
    
    if df is None or df.empty:
        st.info("No data available for opening analysis")
        return
    
    # Extract opening data
    opening_df = extract_opening_data(df)
    
    if opening_df.empty:
        st.info("No opening data found in PGN. Opening analysis requires PGN data with opening tags.")
        return
    
    # Add interactive controls
    st.sidebar.subheader("Opening Analysis Controls")
    
    # Filter by minimum games
    min_games = st.sidebar.slider("Minimum games per opening", 1, 10, 2)
    
    # Filter openings with minimum games
    opening_counts = opening_df['Opening'].value_counts()
    valid_openings = opening_counts[opening_counts >= min_games].index
    filtered_opening_df = opening_df[opening_df['Opening'].isin(valid_openings)]
    
    if filtered_opening_df.empty:
        st.warning(f"No openings with at least {min_games} games found.")
        return
    
    # Create tabs for different chart types
    tab1, tab2, tab3 = st.tabs(["🎯 Interactive Circle Chart", "📊 Performance Analysis", "🌳 Tree Structure"])
    
    with tab1:
        st.markdown("**Interactive Bubble Chart** - Circle size shows popularity, color shows win rate")
        st.plotly_chart(create_opening_circle_chart(filtered_opening_df), use_container_width=True)
        st.caption("💡 **Interactive Features**: Hover for details, drag to pan, zoom to explore")
    
    with tab2:
        st.markdown("**Performance Analysis** - Win rates with game count overlay")
        st.plotly_chart(create_opening_rectangle_chart(filtered_opening_df), use_container_width=True)
        st.caption("💡 **Interactive Features**: Dual-axis chart showing win rate (bars) and game count (dots)")
    
    with tab3:
        st.markdown("**Hierarchical Tree Structure** - Interactive sunburst visualization")
        st.plotly_chart(create_opening_tree_diagram(filtered_opening_df), use_container_width=True)
        st.caption("💡 **Interactive Features**: Click to drill down, hover for detailed stats")
    
    # Show interactive opening statistics table
    with st.expander("📋 Detailed Opening Statistics", expanded=False):
        if not filtered_opening_df.empty:
            stats = filtered_opening_df.groupby('Opening').agg({
                'Result': 'count',
                'Variation': 'nunique'
            }).rename(columns={'Result': 'Total Games', 'Variation': 'Variations'})
            
            # Add win rate
            win_rates = filtered_opening_df.groupby('Opening').apply(
                lambda x: (x['Result'].str.lower() == 'win').sum() / len(x) * 100
            )
            stats['Win Rate (%)'] = win_rates.round(1)
            
            # Add average accuracy if available
            if 'Accuracy %' in df.columns:
                # Merge with original df to get accuracy data
                merged_df = df.merge(filtered_opening_df[['Opening']], left_index=True, right_index=True)
                avg_accuracy = merged_df.groupby('Opening')['Accuracy %'].mean()
                stats['Avg Accuracy (%)'] = avg_accuracy.round(1)
            
            # Sort by total games
            stats = stats.sort_values('Total Games', ascending=False)
            
            st.dataframe(stats, use_container_width=True)
            
            # Add download button
            csv = stats.to_csv(index=True)
            st.download_button(
                label="📥 Download Opening Statistics",
                data=csv,
                file_name="opening_statistics.csv",
                mime="text/csv"
            )
