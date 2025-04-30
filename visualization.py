import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_visualization(data, visualization_type='trend', chart_type='line', forecast_data=None):
    """
    Create visualization based on data and settings.
    
    Args:
        data (pd.DataFrame): Data to visualize
        visualization_type (str): Type of visualization (trend, comparison, distribution, composition)
        chart_type (str): Type of chart (line, bar, scatter, area, pie, heatmap)
        forecast_data (pd.DataFrame): Forecast data to include in visualization
        
    Returns:
        go.Figure: Plotly figure object
    """
    if data is None or len(data) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Select appropriate visualization based on type and chart
    if visualization_type == 'trend':
        fig = create_trend_visualization(data, chart_type, forecast_data)
    elif visualization_type == 'comparison':
        fig = create_comparison_visualization(data, chart_type)
    elif visualization_type == 'distribution':
        fig = create_distribution_visualization(data, chart_type)
    elif visualization_type == 'composition':
        fig = create_composition_visualization(data, chart_type)
    else:
        # Default to trend visualization
        fig = create_trend_visualization(data, chart_type, forecast_data)
    
    # Apply common styling
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    return fig

def create_trend_visualization(data, chart_type='line', forecast_data=None):
    """
    Create trend visualization.
    
    Args:
        data (pd.DataFrame): Data to visualize
        chart_type (str): Type of chart
        forecast_data (pd.DataFrame): Forecast data
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Determine which columns to use based on data
    x_col = 'date'
    y_col = 'value'
    
    if y_col not in data.columns:
        # Try to use the first numeric column
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            y_col = numeric_cols[0]
        else:
            # No suitable columns found
            fig = go.Figure()
            fig.add_annotation(
                text="No suitable numeric column found for visualization",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
    
    # Create figure based on chart type
    if chart_type == 'line':
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col,
            labels={x_col: 'Date', y_col: 'Value'},
            title='Trend Analysis'
        )
        
        # Add forecast if available
        if forecast_data is not None and len(forecast_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=forecast_data[x_col],
                    y=forecast_data['forecast'],
                    mode='lines',
                    name='Forecast',
                    line=dict(dash='dash', color='red')
                )
            )
            
            # Add confidence intervals if available
            if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=forecast_data[x_col],
                        y=forecast_data['upper'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=forecast_data[x_col],
                        y=forecast_data['lower'],
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(255, 0, 0, 0.2)',
                        fill='tonexty',
                        name='Confidence Interval'
                    )
                )
    
    elif chart_type == 'bar':
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col,
            labels={x_col: 'Date', y_col: 'Value'},
            title='Trend Analysis'
        )
        
        # Add forecast if available
        if forecast_data is not None and len(forecast_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=forecast_data[x_col],
                    y=forecast_data['forecast'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='red')
                )
            )
    
    elif chart_type == 'scatter':
        fig = px.scatter(
            data, 
            x=x_col, 
            y=y_col,
            labels={x_col: 'Date', y_col: 'Value'},
            title='Trend Analysis',
            trendline='ols'  # Add trend line
        )
        
        # Add forecast if available
        if forecast_data is not None and len(forecast_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=forecast_data[x_col],
                    y=forecast_data['forecast'],
                    mode='markers',
                    name='Forecast',
                    marker=dict(color='red', size=10)
                )
            )
    
    elif chart_type == 'area':
        fig = px.area(
            data, 
            x=x_col, 
            y=y_col,
            labels={x_col: 'Date', y_col: 'Value'},
            title='Trend Analysis'
        )
        
        # Add forecast if available
        if forecast_data is not None and len(forecast_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=forecast_data[x_col],
                    y=forecast_data['forecast'],
                    mode='lines',
                    name='Forecast',
                    line=dict(dash='dash', color='red')
                )
            )
    
    elif chart_type == 'pie':
        # For pie chart, we'll use aggregated data
        # Group by month and calculate sum
        data['month'] = pd.to_datetime(data[x_col]).dt.strftime('%Y-%m')
        agg_data = data.groupby('month')[y_col].sum().reset_index()
        
        fig = px.pie(
            agg_data, 
            names='month', 
            values=y_col,
            title='Monthly Distribution'
        )
    
    elif chart_type == 'heatmap':
        # For heatmap, we need to reshape data
        # Group by year and month
        data['year'] = pd.to_datetime(data[x_col]).dt.year
        data['month'] = pd.to_datetime(data[x_col]).dt.month
        
        # Create pivot table
        heatmap_data = data.pivot_table(
            index='month',
            columns='year',
            values=y_col,
            aggfunc='mean'
        )
        
        # Fill missing values with 0
        heatmap_data = heatmap_data.fillna(0)
        
        # Create heatmap
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Year", y="Month", color="Value"),
            x=heatmap_data.columns,
            y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            title='Monthly Trend Heatmap',
            color_continuous_scale='Viridis'
        )
    
    else:
        # Default to line chart
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col,
            labels={x_col: 'Date', y_col: 'Value'},
            title='Trend Analysis'
        )
    
    return fig

def create_comparison_visualization(data, chart_type='bar'):
    """
    Create comparison visualization.
    
    Args:
        data (pd.DataFrame): Data to visualize
        chart_type (str): Type of chart
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Find suitable columns for comparison
    x_col = 'date'
    
    # Try to find columns for comparison
    category_col = None
    for col in data.columns:
        if col not in ['date', 'value'] and data[col].nunique() <= 10:
            category_col = col
            break
    
    if category_col is None:
        # No suitable category column found, create artificial grouping
        # Group by month
        data['month'] = pd.to_datetime(data[x_col]).dt.strftime('%Y-%m')
        category_col = 'month'
    
    # Create figure based on chart type
    if chart_type == 'bar':
        fig = px.bar(
            data, 
            x=category_col, 
            y='value',
            labels={category_col: 'Category', 'value': 'Value'},
            title='Comparison Analysis',
            color=category_col
        )
    
    elif chart_type == 'line':
        if category_col != 'month' and x_col in data.columns:
            # Use date as x-axis and categories as different lines
            fig = px.line(
                data, 
                x=x_col, 
                y='value',
                color=category_col,
                labels={x_col: 'Date', 'value': 'Value', category_col: 'Category'},
                title='Comparison Analysis'
            )
        else:
            # Use categories as x-axis
            fig = px.line(
                data, 
                x=category_col, 
                y='value',
                labels={category_col: 'Category', 'value': 'Value'},
                title='Comparison Analysis',
                markers=True
            )
    
    elif chart_type == 'scatter':
        if category_col != 'month' and x_col in data.columns:
            # Use date as x-axis and categories as different points
            fig = px.scatter(
                data, 
                x=x_col, 
                y='value',
                color=category_col,
                labels={x_col: 'Date', 'value': 'Value', category_col: 'Category'},
                title='Comparison Analysis'
            )
        else:
            # Use categories as x-axis
            fig = px.scatter(
                data, 
                x=category_col, 
                y='value',
                labels={category_col: 'Category', 'value': 'Value'},
                title='Comparison Analysis',
                color=category_col
            )
    
    elif chart_type == 'area':
        if category_col != 'month' and x_col in data.columns:
            # Use date as x-axis and categories as stacked areas
            fig = px.area(
                data, 
                x=x_col, 
                y='value',
                color=category_col,
                labels={x_col: 'Date', 'value': 'Value', category_col: 'Category'},
                title='Comparison Analysis'
            )
        else:
            # Cannot create area chart with categories as x-axis, switch to bar
            fig = px.bar(
                data, 
                x=category_col, 
                y='value',
                labels={category_col: 'Category', 'value': 'Value'},
                title='Comparison Analysis',
                color=category_col
            )
    
    elif chart_type == 'pie':
        # Group by category and calculate sum
        agg_data = data.groupby(category_col)['value'].sum().reset_index()
        
        fig = px.pie(
            agg_data, 
            names=category_col, 
            values='value',
            title='Category Distribution'
        )
    
    elif chart_type == 'heatmap':
        # For heatmap, we need multiple categories
        second_category = None
        for col in data.columns:
            if col not in [x_col, 'value', category_col] and data[col].nunique() <= 10:
                second_category = col
                break
        
        if second_category is None:
            # No second category found, create artificial grouping
            # Group by month
            data['month'] = pd.to_datetime(data[x_col]).dt.month
            month_names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            data['month_name'] = data['month'].map(month_names)
            second_category = 'month_name'
        
        # Create pivot table
        heatmap_data = data.pivot_table(
            index=category_col,
            columns=second_category,
            values='value',
            aggfunc='mean'
        )
        
        # Fill missing values with 0
        heatmap_data = heatmap_data.fillna(0)
        
        # Create heatmap
        fig = px.imshow(
            heatmap_data,
            labels=dict(x=second_category, y=category_col, color="Value"),
            title='Comparison Heatmap',
            color_continuous_scale='Viridis'
        )
    
    else:
        # Default to bar chart
        fig = px.bar(
            data, 
            x=category_col, 
            y='value',
            labels={category_col: 'Category', 'value': 'Value'},
            title='Comparison Analysis',
            color=category_col
        )
    
    return fig

def create_distribution_visualization(data, chart_type='histogram'):
    """
    Create distribution visualization.
    
    Args:
        data (pd.DataFrame): Data to visualize
        chart_type (str): Type of chart
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Always use 'value' column for distribution
    y_col = 'value'
    
    if y_col not in data.columns:
        # Try to use the first numeric column
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            y_col = numeric_cols[0]
        else:
            # No suitable columns found
            fig = go.Figure()
            fig.add_annotation(
                text="No suitable numeric column found for visualization",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            return fig
    
    # Create figure based on chart type
    if chart_type == 'bar' or chart_type == 'histogram':
        fig = px.histogram(
            data, 
            x=y_col,
            nbins=30,
            labels={y_col: 'Value'},
            title='Distribution Analysis',
            opacity=0.8
        )
        
        # Add KDE (kernel density estimation) curve
        hist_data = [data[y_col].dropna()]
        
        x_range = np.linspace(min(hist_data[0]), max(hist_data[0]), 100)
        kde = get_kde(hist_data[0], x_range)
        
        # Scale KDE to match histogram
        hist_max = max(fig.data[0].y)
        kde_max = max(kde)
        scaled_kde = [k * (hist_max / kde_max) for k in kde]
        
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=scaled_kde,
                mode='lines',
                name='Density',
                line=dict(color='red', width=2)
            )
        )
    
    elif chart_type == 'scatter':
        # For scatter, we'll create a Q-Q plot
        fig = go.Figure()
        
        values = data[y_col].dropna().values
        values.sort()
        
        # Calculate theoretical quantiles
        n = len(values)
        p = np.arange(1, n + 1) / (n + 1)
        theoretical_quantiles = np.quantile(np.random.normal(0, 1, 10000), p)
        
        # Standardize actual values
        mean = np.mean(values)
        std = np.std(values)
        standardized_values = (values - mean) / std
        
        fig.add_trace(
            go.Scatter(
                x=theoretical_quantiles,
                y=standardized_values,
                mode='markers',
                name='Q-Q Plot',
                marker=dict(
                    color='blue',
                    size=8,
                    opacity=0.6
                )
            )
        )
        
        # Add reference line
        min_val = min(theoretical_quantiles)
        max_val = max(theoretical_quantiles)
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Reference Line',
                line=dict(
                    color='red',
                    dash='dash'
                )
            )
        )
        
        fig.update_layout(
            title='Q-Q Plot (Normal Distribution)',
            xaxis_title='Theoretical Quantiles',
            yaxis_title='Standardized Values'
        )
    
    elif chart_type == 'line':
        # For line chart, we'll create a CDF
        values = data[y_col].dropna().values
        values.sort()
        
        # Calculate CDF
        n = len(values)
        cdf = np.arange(1, n + 1) / n
        
        fig = go.Figure(
            go.Scatter(
                x=values,
                y=cdf,
                mode='lines',
                name='CDF',
                line=dict(color='blue', width=2)
            )
        )
        
        fig.update_layout(
            title='Cumulative Distribution Function',
            xaxis_title='Value',
            yaxis_title='Cumulative Probability'
        )
    
    elif chart_type == 'area':
        # For area chart, we'll create a PDF
        values = data[y_col].dropna().values
        
        # Generate points for PDF
        x_range = np.linspace(min(values), max(values), 100)
        kde = get_kde(values, x_range)
        
        fig = go.Figure(
            go.Scatter(
                x=x_range,
                y=kde,
                mode='lines',
                name='PDF',
                fill='tozeroy',
                line=dict(color='blue', width=2)
            )
        )
        
        fig.update_layout(
            title='Probability Density Function',
            xaxis_title='Value',
            yaxis_title='Density'
        )
    
    elif chart_type == 'pie':
        # For pie chart, we'll create bins and show distribution
        values = data[y_col].dropna().values
        
        # Create bins
        bins = pd.cut(values, bins=5)
        bin_counts = bins.value_counts().sort_index()
        
        # Convert bins to strings for pie chart
        bin_labels = [str(b) for b in bin_counts.index]
        
        fig = px.pie(
            values=bin_counts.values,
            names=bin_labels,
            title='Value Distribution by Range'
        )
    
    elif chart_type == 'heatmap':
        # For heatmap, we'll create a 2D histogram if there's another numeric column
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            x_col = numeric_cols[0] if numeric_cols[0] != y_col else numeric_cols[1]
            
            fig = px.density_heatmap(
                data,
                x=x_col,
                y=y_col,
                nbinsx=20,
                nbinsy=20,
                title=f'2D Distribution: {x_col} vs {y_col}',
                color_continuous_scale='Viridis'
            )
        else:
            # Create a 2D histogram of value vs month
            data['month'] = pd.to_datetime(data['date']).dt.month
            
            fig = px.density_heatmap(
                data,
                x='month',
                y=y_col,
                nbinsx=12,
                nbinsy=20,
                title='Distribution by Month',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(1, 13)),
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                )
            )
    
    else:
        # Default to histogram
        fig = px.histogram(
            data, 
            x=y_col,
            nbins=30,
            labels={y_col: 'Value'},
            title='Distribution Analysis'
        )
    
    return fig

def create_composition_visualization(data, chart_type='pie'):
    """
    Create composition visualization.
    
    Args:
        data (pd.DataFrame): Data to visualize
        chart_type (str): Type of chart
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Find suitable category column for composition
    category_col = None
    for col in data.columns:
        if col not in ['date', 'value'] and data[col].nunique() <= 10:
            category_col = col
            break
    
    if category_col is None:
        # No suitable category column found, create artificial grouping
        # Group by month
        data['month'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m')
        category_col = 'month'
    
    # Always use 'value' column for values
    value_col = 'value'
    
    # Group data by category
    agg_data = data.groupby(category_col)[value_col].sum().reset_index()
    
    # Create figure based on chart type
    if chart_type == 'pie':
        fig = px.pie(
            agg_data, 
            names=category_col, 
            values=value_col,
            title='Composition Analysis',
            hole=0.3  # Make it a donut chart
        )
    
    elif chart_type == 'bar':
        # Stacked bar chart by year and quarter
        if 'date' in data.columns:
            data['year'] = pd.to_datetime(data['date']).dt.year
            data['quarter'] = 'Q' + pd.to_datetime(data['date']).dt.quarter.astype(str)
            
            fig = px.bar(
                data,
                x='year',
                y=value_col,
                color=category_col,
                title='Composition by Year',
                labels={'year': 'Year', value_col: 'Value', category_col: 'Category'}
            )
        else:
            # Simple bar chart
            fig = px.bar(
                agg_data,
                x=category_col,
                y=value_col,
                title='Composition Analysis',
                labels={category_col: 'Category', value_col: 'Value'}
            )
    
    elif chart_type == 'line':
        # Area chart showing composition over time
        if 'date' in data.columns:
            fig = px.area(
                data, 
                x='date', 
                y=value_col,
                color=category_col,
                title='Composition Over Time',
                labels={'date': 'Date', value_col: 'Value', category_col: 'Category'}
            )
        else:
            # Cannot create meaningful time-based chart, switch to bar
            fig = px.bar(
                agg_data,
                x=category_col,
                y=value_col,
                title='Composition Analysis',
                labels={category_col: 'Category', value_col: 'Value'}
            )
    
    elif chart_type == 'area':
        # Area chart showing composition
        if 'date' in data.columns:
            fig = px.area(
                data, 
                x='date', 
                y=value_col,
                color=category_col,
                title='Composition Over Time',
                labels={'date': 'Date', value_col: 'Value', category_col: 'Category'}
            )
        else:
            # Cannot create meaningful area chart, switch to bar
            fig = px.bar(
                agg_data,
                x=category_col,
                y=value_col,
                title='Composition Analysis',
                labels={category_col: 'Category', value_col: 'Value'}
            )
    
    elif chart_type == 'scatter':
        # Create a bubble chart where size represents value
        if len(agg_data) > 1:
            # Add a size column based on percentage of total
            total = agg_data[value_col].sum()
            agg_data['percent'] = (agg_data[value_col] / total) * 100
            
            # Create artificial x-coordinate
            agg_data['x'] = range(len(agg_data))
            
            fig = px.scatter(
                agg_data,
                x='x',
                y='percent',
                size='percent',
                color=category_col,
                text=category_col,
                title='Composition Analysis',
                labels={'percent': 'Percentage (%)', category_col: 'Category'}
            )
            
            # Remove x-axis labels
            fig.update_xaxes(showticklabels=False, title='')
            
            # Add percentage labels
            fig.update_traces(textposition='top center')
        else:
            # Too few categories, switch to pie
            fig = px.pie(
                agg_data, 
                names=category_col, 
                values=value_col,
                title='Composition Analysis'
            )
    
    elif chart_type == 'heatmap':
        # Create a treemap
        fig = px.treemap(
            agg_data,
            path=[category_col],
            values=value_col,
            title='Composition Analysis',
            color=value_col,
            color_continuous_scale='Viridis'
        )
    
    else:
        # Default to pie chart
        fig = px.pie(
            agg_data, 
            names=category_col, 
            values=value_col,
            title='Composition Analysis'
        )
    
    return fig

def get_kde(data, x_range):
    """
    Calculate Kernel Density Estimation for data.
    
    Args:
        data (array-like): Data points
        x_range (array-like): Range of x values to evaluate KDE
        
    Returns:
        array: KDE values
    """
    from scipy.stats import gaussian_kde
    
    # Remove NaN values
    data = np.array(data)
    data = data[~np.isnan(data)]
    
    # Check if we have enough data points
    if len(data) < 2:
        return np.zeros_like(x_range)
    
    # Compute KDE
    kde = gaussian_kde(data)
    return kde(x_range)
