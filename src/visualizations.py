"""
Visualizations Module for A/B Testing Campaign Analysis
Creates plots for data exploration, distributions, and segment analysis
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple

class Visualizations:
    """Create visualizations for A/B testing analysis."""
    
    @staticmethod
    def distribution_plot(
        control: np.ndarray,
        treatment: np.ndarray,
        title: str = "Distribution Comparison",
        xlabel: str = "Value"
    ) -> go.Figure:
        """Create overlapping distribution plot using plotly."""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=control,
            name='Control',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.add_trace(go.Histogram(
            x=treatment,
            name='Treatment',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title="Frequency",
            barmode='overlay',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def box_plot(
        data: pd.DataFrame,
        x: str = 'variant',
        y: str = 'metric',
        title: str = "Distribution by Variant"
    ) -> go.Figure:
        """Create box plot comparison."""
        fig = go.Figure()
        
        for variant in data[x].unique():
            subset = data[data[x] == variant][y]
            fig.add_trace(go.Box(y=subset, name=str(variant)))
        
        fig.update_layout(
            title=title,
            yaxis_title=y,
            xaxis_title=x,
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def kpi_cards(metrics: Dict[str, float]) -> Dict:
        """Generate KPI card data for dashboard."""
        return {
            'kpis': [
                {
                    'label': key,
                    'value': f"{value:.4f}" if isinstance(value, float) else str(value),
                    'delta': None
                }
                for key, value in metrics.items()
            ]
        }
    
    @staticmethod
    def funnel_chart(
        data: Dict[str, List[int]],
        stages: List[str],
        title: str = "Conversion Funnel"
    ) -> go.Figure:
        """Create funnel chart for conversion stages."""
        control_values = data.get('control', [])
        treatment_values = data.get('treatment', [])
        
        fig = go.Figure()
        
        fig.add_trace(go.Funnel(
            y=stages,
            x=control_values,
            name='Control'
        ))
        
        fig.add_trace(go.Funnel(
            y=stages,
            x=treatment_values,
            name='Treatment'
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @staticmethod
    def segment_heatmap(
        segment_results: pd.DataFrame,
        x_col: str = 'segment',
        y_col: str = 'metric',
        value_col: str = 'p_value',
        title: str = "Statistical Significance by Segment"
    ) -> go.Figure:
        """Create heatmap for segment analysis."""
        pivot_data = segment_results.pivot(index=y_col, columns=x_col, values=value_col)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlGn_r',
            colorbar=dict(title="P-Value")
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @staticmethod
    def time_series_plot(
        data: pd.DataFrame,
        date_col: str = 'date',
        value_col: str = 'metric',
        group_col: str = 'variant',
        title: str = "Metric Over Time"
    ) -> go.Figure:
        """Create time series plot."""
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            color=group_col,
            title=title,
            markers=True,
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def effect_size_plot(
        effect_sizes: Dict[str, float],
        title: str = "Effect Sizes by Segment"
    ) -> go.Figure:
        """Create bar plot for effect sizes."""
        fig = go.Figure(
            data=go.Bar(
                x=list(effect_sizes.keys()),
                y=list(effect_sizes.values()),
                marker_color='lightblue'
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Segment",
            yaxis_title="Cohen's d",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def summary_metrics_table(
        results: Dict,
        title: str = "Test Results Summary"
    ) -> pd.DataFrame:
        """Format results as summary table."""
        return pd.DataFrame({
            'Metric': list(results.keys()),
            'Value': list(results.values())
        })
