"""
FingerVision Plotly Charts Library (ui/charts.py)
Interactive presentation charts adhering strictly to Emerald/Mint color palette.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

def create_radar_chart(normalized_scores: Dict[str, float]) -> go.Figure:
    """Renders 5-axis Radar chart comparing normalized metric achievements."""
    categories = ['Blur', 'Brightness', 'Glare Ratio', 'ROI Area', 'Ridge Clarity']
    values = [
        normalized_scores.get('n_blur', 0.0),
        normalized_scores.get('n_bright', 0.0),
        normalized_scores.get('n_glare', 0.0),
        normalized_scores.get('n_roi', 0.0),
        normalized_scores.get('n_ridge', 0.0)
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(44, 246, 195, 0.25)',
        line=dict(color='#2CF6C3', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(44,246,195,0.2)'),
            angularaxis=dict(gridcolor='rgba(44,246,195,0.2)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F7FFFB'),
        height=260,
        margin=dict(l=30, r=30, t=20, b=20)
    )
    return fig

def create_donut_chart(roi_fraction: float) -> go.Figure:
    """Renders Donut chart parsing ROI Foreground vs Background frame density."""
    roi_pct = roi_fraction * 100.0
    bg_pct = max(0.0, 100.0 - roi_pct)
    
    fig = go.Figure(data=[go.Pie(
        labels=['Fingerprint ROI', 'Background Area'],
        values=[roi_pct, bg_pct],
        hole=0.6,
        marker=dict(colors=['#2CF6C3', '#11211D'])
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F7FFFB'),
        height=260,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig

def create_latency_bar_chart(timing_ms: Dict[str, float]) -> go.Figure:
    """Renders Vertical Bar chart comparing per-metric latencies against budgets."""
    keys = ["blur", "brightness", "glare", "roi", "ridge"]
    names = ["Blur", "Bright", "Glare", "ROI", "Ridge"]
    vals = [timing_ms.get(k, 0.0) for k in keys]
    budgets = [10.0, 5.0, 10.0, 100.0, 150.0]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=vals, name="Actual (ms)", marker_color='#2CF6C3'
    ))
    fig.add_trace(go.Scatter(
        x=names, y=budgets, name="Budget SLA", mode='lines+markers', line=dict(color='#D7FF64', dash='dash')
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F7FFFB'),
        yaxis=dict(title="ms", gridcolor='rgba(44,246,195,0.1)'),
        legend=dict(orientation="h", y=1.1, x=0.2),
        height=260,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig

def create_trend_chart(history_scores: List[float]) -> go.Figure:
    """Renders Session History Composite Score Trend Line chart."""
    x_axis = [f"#{i+1}" for i in range(len(history_scores))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_axis, y=history_scores, mode='lines+markers',
        line=dict(color='#2CF6C3', width=3),
        marker=dict(size=8, color='#D7FF64')
    ))
    fig.add_hline(y=60.0, line_dash="dash", line_color="#FFC857", annotation_text="Pass Target (60.0)")
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F7FFFB'),
        yaxis=dict(title="Composite Score", gridcolor='rgba(44,246,195,0.1)', range=[0, 105]),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig
