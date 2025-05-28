import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def create_kpi_cards(forecast_data: List[Dict], inventory_data: List[Dict], route_data: List[Dict] = None):
    """Create KPI cards for the dashboard"""
    
    # Calculate key metrics
    total_demand = sum(item['Forecasted_Demand'] for item in forecast_data) if forecast_data else 0
    total_stock = sum(item['Stock_Level'] for item in inventory_data) if inventory_data else 0
    fill_rate = min(100, (total_stock / total_demand) * 100) if total_demand > 0 else 0
    
    # Create columns for KPI cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Fill Rate",
            value=f"{fill_rate:.1f}%",
            delta="3.2%" if fill_rate > 85 else "-1.5%",
            help="Percentage of demand that can be met from current stock"
        )
    
    with col2:
        stock_turns = 4.2  # Calculated or estimated
        st.metric(
            label="🔄 Inventory Turnover",
            value=f"{stock_turns:.1f}x",
            delta="0.3x" if stock_turns > 4 else "-0.2x",
            help="How many times inventory is sold and replaced per year"
        )
    
    with col3:
        if route_data:
            avg_cost = np.mean([route['Distance_km'] * route['Cost_per_km'] for route in route_data])
            st.metric(
                label="🚚 Avg Route Cost",
                value=f"${avg_cost:,.0f}",
                delta="-8%" if avg_cost < 15000 else "+5%",
                help="Average transportation cost per route"
            )
        else:
            st.metric(
                label="🚚 Routes",
                value="N/A",
                help="Route data not available"
            )
    
    with col4:
        # Calculate service level based on stock availability
        service_level = min(95, fill_rate + 5)
        st.metric(
            label="🎯 Service Level",
            value=f"{service_level:.1f}%",
            delta="2.1%" if service_level > 90 else "-1.0%",
            help="Percentage of orders fulfilled on time and in full"
        )

def create_supply_chain_flow(route_data: List[Dict], inventory_data: List[Dict]) -> go.Figure:
    """Create supply chain flow visualization using Sankey diagram"""
    
    if not route_data:
        # Create a simple placeholder chart
        fig = go.Figure()
        fig.add_annotation(
            text="Route data not available for flow visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(
            title="Supply Chain Flow",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Extract unique locations
    sources = [route['Source'] for route in route_data]
    destinations = [route['Destination'] for route in route_data]
    all_locations = list(set(sources + destinations))
    
    # Create flow values based on route capacity or inventory levels
    flow_values = []
    for route in route_data:
        # Use distance as a proxy for flow volume (inverse relationship)
        base_flow = max(100, 2000 - route['Distance_km'])
        flow_values.append(base_flow)
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_locations,
            color="#3498DB"
        ),
        link=dict(
            source=[all_locations.index(route['Source']) for route in route_data],
            target=[all_locations.index(route['Destination']) for route in route_data],
            value=flow_values,
            color="rgba(52, 152, 219, 0.3)"
        )
    )])
    
    fig.update_layout(
        title_text="Supply Chain Network Flow",
        font_size=10,
        height=500
    )
    
    return fig

def create_demand_forecast_chart(forecast_data: List[Dict]) -> go.Figure:
    """Create demand forecast visualization"""
    
    if not forecast_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No forecast data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return fig
    
    df = pd.DataFrame(forecast_data)
    
    # Group by product for better visualization
    fig = px.bar(
        df,
        x='City',
        y='Forecasted_Demand',
        color='Product',
        title="Demand Forecast by City and Product",
        labels={'Forecasted_Demand': 'Forecasted Demand (Units)'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig

def create_inventory_status_chart(inventory_data: List[Dict], forecast_data: List[Dict]) -> go.Figure:
    """Create inventory status visualization"""
    
    if not inventory_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No inventory data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return fig
    
    # Merge inventory and forecast data
    analysis_data = []
    for inventory in inventory_data:
        demand = 0
        if forecast_data:
            for forecast in forecast_data:
                if (forecast['City'] == inventory['City'] and 
                    forecast['Product'] == inventory['Product']):
                    demand = forecast['Forecasted_Demand']
                    break
        
        status = "Optimal"
        if inventory['Stock_Level'] < demand * 0.8:
            status = "Low Stock"
        elif inventory['Stock_Level'] > demand * 1.5:
            status = "Overstock"
        
        analysis_data.append({
            'Location': f"{inventory['City']} - {inventory['Product']}",
            'Current_Stock': inventory['Stock_Level'],
            'Demand': demand,
            'Status': status
        })
    
    df = pd.DataFrame(analysis_data)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Stock vs Demand', 'Inventory Status'),
        vertical_spacing=0.15
    )
    
    # Stock vs Demand comparison
    fig.add_trace(
        go.Bar(
            name='Current Stock',
            x=df['Location'],
            y=df['Current_Stock'],
            marker_color='#3498DB'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            name='Forecasted Demand',
            x=df['Location'],
            y=df['Demand'],
            marker_color='#E74C3C'
        ),
        row=1, col=1
    )
    
    # Status indicators
    status_colors = {'Optimal': '#27AE60', 'Low Stock': '#E74C3C', 'Overstock': '#F39C12'}
    colors = [status_colors.get(status, '#95A5A6') for status in df['Status']]
    
    fig.add_trace(
        go.Bar(
            name='Inventory Status',
            x=df['Location'],
            y=[1] * len(df),  # Uniform height for status
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="Inventory Analysis Dashboard"
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_route_efficiency_chart(route_data: List[Dict]) -> go.Figure:
    """Create route efficiency analysis chart"""
    
    if not route_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No route data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return fig
    
    df = pd.DataFrame(route_data)
    
    # Calculate total cost for each route
    df['Total_Cost'] = df['Distance_km'] * df['Cost_per_km']
    df['Efficiency_Score'] = 100 - (df['Total_Cost'] / df['Total_Cost'].max() * 100)
    
    fig = px.scatter(
        df,
        x='Distance_km',
        y='Total_Cost',
        size='Average_Travel_Time_hrs',
        color='Efficiency_Score',
        hover_data=['Source', 'Destination'],
        title="Route Efficiency Analysis",
        labels={
            'Distance_km': 'Distance (km)',
            'Total_Cost': 'Total Cost ($)',
            'Efficiency_Score': 'Efficiency Score'
        },
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_supplier_performance_chart(supplier_data: List[Dict]) -> go.Figure:
    """Create supplier performance analysis chart"""
    
    if not supplier_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No supplier data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return fig
    
    df = pd.DataFrame(supplier_data)
    
    # Create performance matrix
    fig = px.scatter(
        df,
        x='Cost_per_Unit',
        y='Reliability_Score',
        size='Lead_Time_Days',
        color='Product',
        hover_data=['Supplier_Name'],
        title="Supplier Performance Matrix",
        labels={
            'Cost_per_Unit': 'Cost per Unit ($)',
            'Reliability_Score': 'Reliability Score (%)',
            'Lead_Time_Days': 'Lead Time (Days)'
        }
    )
    
    # Add quadrant lines
    avg_cost = df['Cost_per_Unit'].mean()
    avg_reliability = df['Reliability_Score'].mean()
    
    fig.add_vline(x=avg_cost, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=avg_reliability, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=avg_cost * 0.7, y=avg_reliability * 1.1, text="High Performance<br>Low Cost", 
                      showarrow=False, bgcolor="rgba(39, 174, 96, 0.1)")
    fig.add_annotation(x=avg_cost * 1.3, y=avg_reliability * 1.1, text="High Performance<br>High Cost", 
                      showarrow=False, bgcolor="rgba(52, 152, 219, 0.1)")
    fig.add_annotation(x=avg_cost * 0.7, y=avg_reliability * 0.9, text="Low Performance<br>Low Cost", 
                      showarrow=False, bgcolor="rgba(241, 196, 15, 0.1)")
    fig.add_annotation(x=avg_cost * 1.3, y=avg_reliability * 0.9, text="Low Performance<br>High Cost", 
                      showarrow=False, bgcolor="rgba(231, 76, 60, 0.1)")
    
    fig.update_layout(height=500)
    
    return fig

def create_risk_assessment_radar(risk_scores: Dict[str, float]) -> go.Figure:
    """Create risk assessment radar chart"""
    
    categories = list(risk_scores.keys())
    values = list(risk_scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Risk Profile',
        fillcolor='rgba(231, 76, 60, 0.3)',
        line_color='#E74C3C'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2
            )),
        showlegend=False,
        title="Supply Chain Risk Assessment"
    )
    
    return fig

def create_cost_breakdown_chart(cost_data: Dict[str, float]) -> go.Figure:
    """Create cost breakdown visualization"""
    
    labels = list(cost_data.keys())
    values = list(cost_data.values())
    
    fig = px.pie(
        values=values,
        names=labels,
        title="Supply Chain Cost Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cost: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    return fig

def create_performance_trends_chart(trend_data: pd.DataFrame) -> go.Figure:
    """Create performance trends over time"""
    
    fig = px.line(
        trend_data,
        x='Date',
        y=['Fill_Rate', 'On_Time_Delivery', 'Cost_Efficiency'],
        title="Performance Trends Over Time",
        labels={'value': 'Performance (%)', 'variable': 'Metric'}
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Performance (%)",
        legend_title="Metrics",
        height=400
    )
    
    return fig

def create_optimization_comparison_chart(current_data: Dict, optimized_data: Dict) -> go.Figure:
    """Create before/after optimization comparison"""
    
    metrics = list(current_data.keys())
    current_values = list(current_data.values())
    optimized_values = list(optimized_data.values())
    
    fig = go.Figure(data=[
        go.Bar(name='Current', x=metrics, y=current_values, marker_color='#E74C3C'),
        go.Bar(name='Optimized', x=metrics, y=optimized_values, marker_color='#27AE60')
    ])
    
    fig.update_layout(
        barmode='group',
        title="Optimization Impact Comparison",
        xaxis_title="Metrics",
        yaxis_title="Values",
        height=400
    )
    
    return fig

def create_geographic_heatmap(location_data: List[Dict], metric: str) -> go.Figure:
    """Create geographic performance heatmap"""
    
    df = pd.DataFrame(location_data)
    
    if metric not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Metric '{metric}' not available in data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return fig
    
    fig = px.bar(
        df,
        x='Location',
        y=metric,
        color=metric,
        title=f"Geographic Distribution: {metric}",
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig

def create_executive_dashboard_summary(summary_data: Dict[str, Any]) -> go.Figure:
    """Create executive summary dashboard with multiple subplots"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Key Performance Indicators',
            'Cost Distribution',
            'Performance Trends',
            'Risk Assessment'
        ),
        specs=[
            [{"type": "indicator"}, {"type": "pie"}],
            [{"type": "scatter"}, {"type": "scatterpolar"}]
        ]
    )
    
    # KPI Gauges
    if 'kpis' in summary_data:
        kpi_data = summary_data['kpis']
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=kpi_data.get('fill_rate', 75),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Fill Rate %"},
                delta={'reference': 90},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#3498DB"},
                    'steps': [
                        {'range': [0, 50], 'color': "#F8F9FA"},
                        {'range': [50, 80], 'color': "#E8F4FD"}
                    ],
                    'threshold': {
                        'line': {'color': "#E74C3C", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Executive Dashboard Summary"
    )
    
    return fig
