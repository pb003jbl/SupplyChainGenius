import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_handler import DataHandler
from utils.visualizations import create_kpi_cards, create_supply_chain_flow

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def main():
    st.title("📊 Supply Chain Dashboard")
    st.markdown("Real-time overview of your supply chain performance")
    
    # Initialize data handler
    data_handler = DataHandler()
    
    # Load sample data or user data
    try:
        # Try to load user uploaded data first, fallback to samples
        forecast_data = data_handler.get_forecast_data()
        inventory_data = data_handler.get_inventory_data()
        route_data = data_handler.get_route_data()
        supplier_data = data_handler.get_supplier_data()
        
        if forecast_data is None or inventory_data is None:
            st.warning("No data available. Please upload data in the Data Upload section or use sample data.")
            if st.button("Load Sample Data"):
                data_handler.load_sample_data()
                st.rerun()
            return
        
        # KPI Cards
        st.markdown("### Key Performance Indicators")
        create_kpi_cards(forecast_data, inventory_data, route_data)
        
        st.markdown("---")
        
        # Main dashboard content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Demand vs Inventory Chart
            st.markdown("### 📈 Demand vs Inventory Analysis")
            
            # Merge forecast and inventory data
            merged_data = []
            for forecast in forecast_data:
                for inventory in inventory_data:
                    if (forecast['City'] == inventory['City'] and 
                        forecast['Product'] == inventory['Product']):
                        merged_data.append({
                            'City': forecast['City'],
                            'Product': forecast['Product'],
                            'Forecasted_Demand': forecast['Forecasted_Demand'],
                            'Stock_Level': inventory['Stock_Level'],
                            'Gap': inventory['Stock_Level'] - forecast['Forecasted_Demand']
                        })
            
            if merged_data:
                df_merged = pd.DataFrame(merged_data)
                
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Demand vs Stock Levels', 'Inventory Gap Analysis'),
                    vertical_spacing=0.1
                )
                
                # Demand vs Stock
                fig.add_trace(
                    go.Bar(
                        name='Forecasted Demand',
                        x=df_merged['City'] + ' - ' + df_merged['Product'],
                        y=df_merged['Forecasted_Demand'],
                        marker_color='#3498DB'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        name='Current Stock',
                        x=df_merged['City'] + ' - ' + df_merged['Product'],
                        y=df_merged['Stock_Level'],
                        marker_color='#2C3E50'
                    ),
                    row=1, col=1
                )
                
                # Gap Analysis
                colors = ['#E74C3C' if gap < 0 else '#27AE60' for gap in df_merged['Gap']]
                fig.add_trace(
                    go.Bar(
                        name='Inventory Gap',
                        x=df_merged['City'] + ' - ' + df_merged['Product'],
                        y=df_merged['Gap'],
                        marker_color=colors,
                        showlegend=False
                    ),
                    row=2, col=1
                )
                
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    barmode='group'
                )
                
                fig.update_xaxes(tickangle=45)
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Supply Chain Health Score
            st.markdown("### 🎯 Supply Chain Health")
            
            # Calculate health metrics
            total_demand = sum(item['Forecasted_Demand'] for item in forecast_data)
            total_stock = sum(item['Stock_Level'] for item in inventory_data)
            fill_rate = min(100, (total_stock / total_demand) * 100) if total_demand > 0 else 0
            
            # Health score gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = fill_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Fill Rate %"},
                delta = {'reference': 95},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#3498DB"},
                    'steps': [
                        {'range': [0, 50], 'color': "#F8F9FA"},
                        {'range': [50, 80], 'color': "#E8F4FD"},
                        {'range': [80, 100], 'color': "#D6EAF8"}
                    ],
                    'threshold': {
                        'line': {'color': "#E74C3C", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Recent Alerts
            st.markdown("### 🚨 Recent Alerts")
            
            alerts = []
            for item in merged_data:
                if item['Gap'] < 0:
                    alerts.append({
                        'Type': 'Stock Shortage',
                        'Location': item['City'],
                        'Product': item['Product'],
                        'Severity': 'High' if item['Gap'] < -500 else 'Medium'
                    })
            
            if alerts:
                for alert in alerts[:5]:  # Show top 5 alerts
                    severity_color = "#E74C3C" if alert['Severity'] == 'High' else "#F39C12"
                    st.markdown(f"""
                    <div style="background-color: {severity_color}20; padding: 10px; border-left: 4px solid {severity_color}; margin: 5px 0;">
                        <strong>{alert['Type']}</strong><br>
                        {alert['Location']} - {alert['Product']}<br>
                        <small>Severity: {alert['Severity']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No critical alerts")
        
        # Supply Chain Flow Visualization
        st.markdown("---")
        st.markdown("### 🌐 Supply Chain Flow")
        
        if route_data:
            flow_fig = create_supply_chain_flow(route_data, inventory_data)
            st.plotly_chart(flow_fig, use_container_width=True)
        
        # Performance Trends
        st.markdown("---")
        st.markdown("### 📈 Performance Trends")
        
        # Generate trend data (simulated historical data)
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        trend_data = {
            'Date': dates,
            'Fill_Rate': [85 + np.random.normal(0, 5) for _ in dates],
            'On_Time_Delivery': [90 + np.random.normal(0, 3) for _ in dates],
            'Cost_Efficiency': [75 + np.random.normal(0, 4) for _ in dates]
        }
        
        df_trends = pd.DataFrame(trend_data)
        
        fig_trends = px.line(
            df_trends, 
            x='Date', 
            y=['Fill_Rate', 'On_Time_Delivery', 'Cost_Efficiency'],
            title="30-Day Performance Trends",
            color_discrete_map={
                'Fill_Rate': '#3498DB',
                'On_Time_Delivery': '#27AE60',
                'Cost_Efficiency': '#F39C12'
            }
        )
        
        fig_trends.update_layout(
            yaxis_title="Performance %",
            legend_title="Metrics"
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        st.info("Please check your data uploads or API configuration.")

if __name__ == "__main__":
    main()
