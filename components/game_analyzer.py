"""
Game analyzer component for Chess Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def create_game_analyzer(df):
    """Create game analysis interface"""
    st.subheader("Game Analysis")
    
    if df is None or df.empty:
        st.info("No data available for game analysis")
        return
    
    # Game analysis features
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Game Statistics")
        if 'Result' in df.columns:
            result_counts = df['Result'].value_counts()
            fig = px.pie(values=result_counts.values, names=result_counts.index, title="Game Results")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Performance by Side")
        if 'Side' in df.columns and 'Result' in df.columns:
            side_stats = df.groupby('Side')['Result'].apply(
                lambda x: (x.str.lower() == 'win').sum() / len(x) * 100
            )
            fig = px.bar(x=side_stats.index, y=side_stats.values, title="Win Rate by Side")
            st.plotly_chart(fig, use_container_width=True)
    
    # Game history table
    st.subheader("Recent Games")
    if len(df) > 0:
        display_cols = ['Date', 'Side', 'Result', 'Accuracy %', 'ACL', 'Opponent Name']
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols].head(10), use_container_width=True)
