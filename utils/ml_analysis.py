"""
Machine Learning analysis for Chess Analytics Dashboard
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def generate_performance_insights(df):
    """Generate AI-powered performance insights"""
    if df is None or len(df) < 5:
        return {
            'text_insights': ["Need at least 5 games for analysis"],
            'performance_clusters': pd.DataFrame()
        }
    
    insights = []
    
    # Basic statistics
    total_games = len(df)
    wins = len(df[df['RESULT'].str.lower() == 'win'])
    losses = len(df[df['RESULT'].str.lower() == 'loss'])
    draws = len(df[df['RESULT'].str.lower() == 'draw'])
    
    win_rate = (wins / total_games * 100) if total_games > 0 else 0
    
    # Rating analysis
    if 'New Rating' in df.columns and not df['New Rating'].isna().all():
        recent_rating = df['New Rating'].iloc[-1]
        if len(df) >= 10:
            early_rating = df['New Rating'].iloc[0]
            rating_change = recent_rating - early_rating
            if rating_change > 0:
                insights.append("📈 Your rating has improved by {} points over your last {} games".format(
                    abs(rating_change), min(10, len(df))))
            elif rating_change < 0:
                insights.append("📉 Your rating has decreased by {} points over your last {} games".format(
                    abs(rating_change), min(10, len(df))))
            else:
                insights.append("📊 Your rating has remained stable over your last {} games".format(min(10, len(df))))
    
    # Accuracy analysis
    if 'Accuracy %' in df.columns and not df['Accuracy %'].isna().all():
        avg_accuracy = df['Accuracy %'].mean()
        if avg_accuracy > 85:
            insights.append("🎯 Excellent accuracy! Your average of {:.1f}% shows strong tactical play".format(avg_accuracy))
        elif avg_accuracy > 75:
            insights.append("🎯 Good accuracy! Your average of {:.1f}% indicates solid tactical understanding".format(avg_accuracy))
        else:
            insights.append("🎯 Focus on tactical training - your accuracy of {:.1f}% has room for improvement".format(avg_accuracy))
    
    # ACL analysis
    if 'ACL' in df.columns and not df['ACL'].isna().all():
        avg_acl = df['ACL'].mean()
        if avg_acl < 50:
            insights.append("⚖️ Strong positional play! Your ACL of {:.1f} shows good decision-making".format(avg_acl))
        elif avg_acl < 75:
            insights.append("⚖️ Decent positional understanding with ACL of {:.1f}".format(avg_acl))
        else:
            insights.append("⚖️ Focus on positional play - your ACL of {:.1f} indicates room for improvement".format(avg_acl))
    
    # Side performance analysis
    if 'Side' in df.columns:
        white_games = df[df['Side'].str.upper().isin(['W', 'WHITE'])]
        black_games = df[df['Side'].str.upper().isin(['B', 'BLACK'])]
        
        if len(white_games) > 0 and len(black_games) > 0:
            white_wins = len(white_games[white_games['RESULT'].str.lower() == 'win'])
            black_wins = len(black_games[black_games['RESULT'].str.lower() == 'win'])
            
            white_win_rate = (white_wins / len(white_games) * 100) if len(white_games) > 0 else 0
            black_win_rate = (black_wins / len(black_games) * 100) if len(black_games) > 0 else 0
            
            if abs(white_win_rate - black_win_rate) > 10:
                if white_win_rate > black_win_rate:
                    insights.append("⚔️ You perform better with White pieces ({:.1f}% vs {:.1f}% win rate)".format(
                        white_win_rate, black_win_rate))
                else:
                    insights.append("⚔️ You perform better with Black pieces ({:.1f}% vs {:.1f}% win rate)".format(
                        black_win_rate, white_win_rate))
    
    # Performance clustering
    performance_clusters = pd.DataFrame()
    if len(df) >= 5 and 'Accuracy %' in df.columns and 'ACL' in df.columns:
        # Prepare data for clustering
        cluster_data = df[['Accuracy %', 'ACL']].dropna()
        if len(cluster_data) >= 3:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(cluster_data)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=min(3, len(cluster_data)), random_state=42)
            cluster_data['Cluster'] = kmeans.fit_predict(scaled_data)
            
            # Analyze clusters
            cluster_stats = cluster_data.groupby('Cluster').agg({
                'Accuracy %': ['mean', 'count'],
                'ACL': 'mean'
            }).round(2)
            
            performance_clusters = cluster_stats
    
    # Add general insights
    insights.append("📊 Overall win rate: {:.1f}% ({}/{})".format(win_rate, wins, total_games))
    
    if len(insights) < 3:
        insights.extend([
            "🧮 Consider analyzing your opening repertoire",
            "🏰 Focus on endgame technique",
            "��‍♂️ Maintain consistent time management",
            "⏰ Review games with high ACL values",
            "🌟 Practice tactical puzzles regularly"
        ])
    
    return {
        'text_insights': insights,
        'performance_clusters': performance_clusters
    }
