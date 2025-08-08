import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="♟️ Chess Analytics Dashboard",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
.chess-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    color: white;
}
.chess-header h1 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.chess-header p {
    font-size: 1.1rem;
    opacity: 0.9;
}
.chess-links {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}
.chess-links a {
    color: #667eea;
    text-decoration: none;
    font-weight: bold;
    margin: 0 0.5rem;
}
.chess-links a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
    <div class='chess-header'>
        <h1>♟️ Chess Analytics Dashboard</h1>
        <p>Track and analyze your chess performance</p>
    </div>
""", unsafe_allow_html=True)

# Add links
st.markdown("""
    <div class='chess-links'>
        <a href="https://lichess.org/study/aatGfpd6/C8WS6Cy8" target="_blank">Lichess Study</a> | 
        <a href="https://www.chess.com/library/collections/tonyc-annex-chess-club-games-H8SCFdtS" target="_blank">Chess.com Library</a> | 
        <a href="https://docs.google.com/spreadsheets/d/1Z1zFDzVF0_zxEuH3AwBNy8or2SYmpulRnKn2OYvSo5Q/edit?gid=0#gid=0" target="_blank">Google Sheet</a> | 
        <a href="https://www.chess.ca/en/ratings/p/?id=184535" target="_blank">CFC Ranking</a>
    </div>
""", unsafe_allow_html=True)

# Generate sample data for demonstration
@st.cache_data
def generate_sample_data():
    """Generate sample chess data for demonstration"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    
    data = {
        'Date': dates,
        'Side': np.random.choice(['W', 'B'], 50),
        'Result': np.random.choice(['WIN', 'LOSS', 'DRAW'], 50, p=[0.4, 0.35, 0.25]),
        'ACL': np.random.normal(45, 15, 50).clip(10, 100),
        'Accuracy %': np.random.normal(85, 10, 50).clip(60, 98),
        'Opponent Name': [f'Player {i+1}' for i in range(50)],
        'Opp. ELO': np.random.normal(1500, 100, 50).clip(1300, 1700).astype(int),
        'New Rating': np.random.normal(1520, 50, 50).clip(1400, 1600).astype(int)
    }
    
    return pd.DataFrame(data)

# Load data
with st.spinner('Loading chess data...'):
    df = generate_sample_data()

# Calculate statistics
total_games = len(df)
current_rating = df['New Rating'].iloc[-1]
wins = len(df[df['Result'] == 'WIN'])
win_percentage = (wins / total_games * 100) if total_games > 0 else 0

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Games", total_games)
with col2:
    st.metric("Current Rating", f"{current_rating}")
with col3:
    st.metric("Win Percentage", f"{win_percentage:.1f}%")
with col4:
    st.metric("Avg Accuracy", f"{df['Accuracy %'].mean():.1f}%")

# Performance Charts
st.subheader("📊 Performance Metrics")

# Rating progression
fig_rating = go.Figure()
fig_rating.add_trace(go.Scatter(
    x=df['Date'],
    y=df['New Rating'],
    mode='lines+markers',
    name='Rating',
    line=dict(color='#4CAF50', shape='spline'),
    marker=dict(size=4)
))
fig_rating.update_layout(
    title="Rating Progression Over Time",
    xaxis_title="Date",
    yaxis_title="Rating",
    height=400
)
st.plotly_chart(fig_rating, use_container_width=True)

# Win/Loss distribution
col1, col2 = st.columns(2)

with col1:
    result_counts = df['Result'].value_counts()
    fig_results = px.pie(
        values=result_counts.values,
        names=result_counts.index,
        title="Game Results Distribution",
        color_discrete_map={'WIN': '#4CAF50', 'LOSS': '#f44336', 'DRAW': '#2196F3'}
    )
    st.plotly_chart(fig_results, use_container_width=True)

with col2:
    # Accuracy over time
    fig_accuracy = go.Figure()
    fig_accuracy.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Accuracy %'],
        mode='lines+markers',
        name='Accuracy %',
        line=dict(color='#FF9800', shape='spline'),
        marker=dict(size=4)
    ))
    fig_accuracy.update_layout(
        title="Accuracy % Over Time",
        xaxis_title="Date",
        yaxis_title="Accuracy %",
        height=400
    )
    st.plotly_chart(fig_accuracy, use_container_width=True)

# Side performance analysis
st.subheader("♟️ Performance by Side")

side_stats = df.groupby('Side').agg({
    'Result': lambda x: (x == 'WIN').sum() / len(x) * 100,
    'Accuracy %': 'mean',
    'ACL': 'mean'
}).round(1)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("White Win %", f"{side_stats.loc['W', 'Result']:.1f}%")
with col2:
    st.metric("Black Win %", f"{side_stats.loc['B', 'Result']:.1f}%")
with col3:
    st.metric("Overall Win %", f"{win_percentage:.1f}%")

# Game history table
st.subheader("📋 Recent Games")

# Format the display dataframe
display_df = df.copy()
display_df['Date'] = display_df['Date'].dt.date
display_df = display_df.sort_values('Date', ascending=False)

# Show last 10 games
st.dataframe(
    display_df[['Date', 'Side', 'Result', 'Accuracy %', 'ACL', 'Opponent Name', 'Opp. ELO']].head(10),
    use_container_width=True
)

# AI Insights section
st.subheader("🤖 AI Performance Insights")

insights = [
    "📈 Your rating shows a positive trend over the last 50 games",
    "🎯 Your average accuracy of 85.2% indicates strong tactical play",
    "⚖️ You perform slightly better with White pieces (42% vs 38% win rate)",
    "📊 Your ACL of 45.2 shows good positional understanding",
    "🔍 Focus on endgame technique - 25% of your losses occur in the final phase"
]

for insight in insights:
    st.info(insight)

# Future features preview
with st.expander("🚀 Upcoming Features"):
    st.write("""
    - **Opening Analysis**: Hierarchical tree visualization of your opening repertoire
    - **PGN Game Analysis**: Detailed move-by-move analysis with mistake detection
    - **Machine Learning**: AI-powered performance predictions and improvement recommendations
    - **Google Sheets Integration**: Automatic data synchronization from your chess spreadsheet
    - **Mobile Optimization**: Enhanced mobile experience for on-the-go analysis
    """)

st.success("🎉 Welcome to your Chess Analytics Dashboard! This is a demonstration with sample data. Connect your real chess data to see your actual performance metrics.")
