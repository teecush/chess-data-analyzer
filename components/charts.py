"""
Chart components for the Chess Analytics Dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_rating_progression(df, side_filter="Both"):
    """Create rating progression chart with side awareness"""
    # Filter out rows where New Rating is NaN for the chart
    rating_df = df[df['New Rating'].notna()].copy()

    # Create base figure
    fig = go.Figure()

    # Add main line
    fig.add_trace(go.Scatter(
        x=rating_df['Date'],
        y=rating_df['New Rating'],
        mode='lines+markers',
        name='Rating',
        line=dict(color='#4CAF50', shape='spline'),
        marker=dict(size=4)
    ))

    # Add linear trendline
    if len(rating_df) > 1:
        x_numeric = np.arange(len(rating_df))
        z = np.polyfit(x_numeric, rating_df['New Rating'], 1)
        p = np.poly1d(z)

        fig.add_trace(go.Scatter(
            x=rating_df['Date'],
            y=p(x_numeric),
            mode='lines',
            name='Trend',
            line=dict(color='#FF4B4B', width=2, dash='dash'),
            showlegend=True
        ))
    
    # Update title with side information
    title = 'Rating Progression Over Time'
    if side_filter != "Both":
        title = f'Rating Progression ({side_filter} Games)'

    fig.update_layout(
        title=title,
        template='plotly_white',
        hovermode='x unified',
        height=300,  # Reduced height for mobile
        margin=dict(l=10, r=10, t=60, b=10),  # Increased top margin to prevent toolbar overlap
        xaxis_title=None,  # Remove axis titles for cleaner mobile view
        yaxis_title=None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def create_win_loss_pie(df, side_filter="Both"):
    """Create win/loss distribution pie chart with side awareness"""
    # Count results with case-insensitive matching
    # Use 'RESULT' column instead of 'Result'
    result_counts = df['RESULT'].str.lower().value_counts()
    wins = result_counts.get('win', 0)
    losses = result_counts.get('loss', 0)
    draws = result_counts.get('draw', 0)
    
    total = sum([wins, losses, draws])
    
    # Calculate percentages
    win_pct = round((wins / total * 100), 1) if total > 0 else 0
    loss_pct = round((losses / total * 100), 1) if total > 0 else 0
    draw_pct = round((draws / total * 100), 1) if total > 0 else 0
    
    # Create custom labels with both count and percentage
    custom_labels = [
        f'Wins: {wins} ({win_pct}%)', 
        f'Losses: {losses} ({loss_pct}%)', 
        f'Draws: {draws} ({draw_pct}%)'
    ]
    
    values = [wins, losses, draws]
    colors = ['#4CAF50', '#f44336', '#2196F3']  # green, red, blue
    
    # Create a simpler pie chart with built-in labels
    fig = go.Figure(data=[go.Pie(
        labels=custom_labels,
        values=values,
        hole=0.4,  # Larger hole to make room for total count
        marker_colors=colors,
        textinfo='none',  # Don't show any text on the pie slices themselves
        hoverinfo='label+percent+value',
        hovertemplate='%{label}<br>Percentage: %{percent}<extra></extra>',
        showlegend=True,
        sort=False  # Keep the original order
    )])
    
    # Add center annotation for total count
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>Total<br>{total}</b>",
        font=dict(size=18, color='black', family='Arial'),
        showarrow=False
    )
    
    # Set title with side information
    title = 'Game Results Distribution'
    if side_filter != "Both":
        title = f'Results as {side_filter}'
    
    # Clean up the chart
    fig.update_layout(
        title=title,
        template='plotly_white',
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1.0
        ),
        # Hide axes completely
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig

def create_metric_over_time(df, metric_col, title, y_label, side_filter="Both"):
    """Create line chart for metrics over time with side awareness"""
    # Filter out rows where metric is NaN
    metric_df = df[df[metric_col].notna()].copy()

    # Create base line plot
    fig = go.Figure()

    # Add main line
    fig.add_trace(go.Scatter(
        x=metric_df['Date'],
        y=metric_df[metric_col],
        mode='lines+markers',
        name='Actual',
        line=dict(color='#4CAF50', shape='spline'),
        marker=dict(size=4)  # Smaller markers for mobile
    ))

    # Add linear trendline
    if len(metric_df) > 1:
        x_numeric = np.arange(len(metric_df))
        z = np.polyfit(x_numeric, metric_df[metric_col], 1)
        p = np.poly1d(z)

        fig.add_trace(go.Scatter(
            x=metric_df['Date'],
            y=p(x_numeric),
            mode='lines',
            name='Trend',
            line=dict(color='#FF4B4B', width=2, dash='dash'),
            showlegend=True
        ))
    
    # Update title with side information
    display_title = title
    if side_filter != "Both":
        display_title = f"{title} ({side_filter})"

    fig.update_layout(
        title=display_title,
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified',
        height=300,  # Reduced height for mobile
        margin=dict(l=10, r=10, t=60, b=10),  # Increased top margin to prevent toolbar overlap
        xaxis_title=None,  # Remove axis titles for cleaner mobile view
        yaxis_title=None
    )
    return fig

def create_performance_charts(df, side_filter="Both"):
    """Create all performance metric charts with side filter"""
    charts = {
        'acl': create_metric_over_time(
            df, 'ACL',
            'ACL Over Time',
            'ACL',
            side_filter
        ),
        'accuracy': create_metric_over_time(
            df, 'Accuracy %',
            'Accuracy % Over Time',
            'Accuracy %',
            side_filter
        ),
        'game_rating': create_metric_over_time(
            df, 'Game Rating',
            'Game Rating Over Time',
            'Game ELO',
            side_filter
        ),
        'performance_rating': create_metric_over_time(
            df, 'Performance Rating',
            'Performance Rating Over Time',
            'Performance Rating',
            side_filter
        )
    }
    return charts

def create_opening_bar(opening_stats):
    """Create opening statistics bar chart"""
    if not opening_stats.empty:
        fig = go.Figure(data=[
            go.Bar(
                x=opening_stats.index,
                y=opening_stats.values,
                marker_color='#4CAF50'
            )
        ])
        fig.update_layout(
            title='Most Played Openings',
            xaxis_tickangle=-45,
            template='plotly_white',
            showlegend=False,
            height=300,  # Reduced height for mobile
            margin=dict(l=10, r=10, t=60, b=10) # Increased top margin to prevent toolbar overlap
        )
        return fig
    else:
        # Return empty figure if no opening stats
        return go.Figure()
