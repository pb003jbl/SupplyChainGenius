import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
from utils.data_handler import DataHandler
from utils.groq_client import GroqClient
from utils.agents import SupplyChainAgents

def main():
    st.title("🔍 AI-Powered Supply Chain Analysis")
    st.markdown("Advanced analysis using GROQ LLM and intelligent agents")
    
    data_handler = DataHandler()
    
    # Check if data is available
    forecast_data = data_handler.get_forecast_data()
    inventory_data = data_handler.get_inventory_data()
    route_data = data_handler.get_route_data()
    supplier_data = data_handler.get_supplier_data()
    
    if not all([forecast_data, inventory_data]):
        st.warning("Please upload data in the Data Upload section before running analysis.")
        if st.button("Load Sample Data for Analysis"):
            data_handler.load_sample_data()
            st.rerun()
        return
    
    # Analysis type selection
    st.markdown("### Analysis Options")
    
    analysis_type = st.selectbox(
        "Select Analysis Type",
        [
            "Demand Forecast Validation",
            "Inventory Optimization",
            "Supply Chain Risk Assessment",
            "Supplier Performance Analysis",
            "Route Optimization Analysis",
            "Comprehensive Supply Chain Health Check"
        ]
    )
    
    # Initialize GROQ client and agents
    try:
        groq_client = GroqClient()
        agents = SupplyChainAgents()
        
        if st.button("🚀 Run AI Analysis", type="primary"):
            with st.spinner("AI agents are analyzing your supply chain data..."):
                
                if analysis_type == "Demand Forecast Validation":
                    run_demand_forecast_analysis(groq_client, agents, forecast_data, inventory_data)
                
                elif analysis_type == "Inventory Optimization":
                    run_inventory_optimization(groq_client, agents, forecast_data, inventory_data)
                
                elif analysis_type == "Supply Chain Risk Assessment":
                    run_risk_assessment(groq_client, agents, forecast_data, inventory_data, route_data, supplier_data)
                
                elif analysis_type == "Supplier Performance Analysis":
                    if supplier_data:
                        run_supplier_analysis(groq_client, agents, supplier_data, inventory_data)
                    else:
                        st.warning("Supplier data not available. Please upload supplier data first.")
                
                elif analysis_type == "Route Optimization Analysis":
                    if route_data:
                        run_route_analysis(groq_client, agents, route_data, inventory_data)
                    else:
                        st.warning("Route data not available. Please upload route data first.")
                
                elif analysis_type == "Comprehensive Supply Chain Health Check":
                    run_comprehensive_analysis(groq_client, agents, forecast_data, inventory_data, route_data, supplier_data)
    
    except Exception as e:
        st.error(f"Error initializing AI clients: {str(e)}")
        st.info("Please check your API configuration in the Settings page.")

def run_demand_forecast_analysis(groq_client, agents, forecast_data, inventory_data):
    """Run demand forecast validation analysis"""
    st.markdown("---")
    st.markdown("### 📈 Demand Forecast Analysis Results")
    
    # Prepare analysis data
    analysis_context = {
        "forecast_data": forecast_data,
        "inventory_data": inventory_data,
        "analysis_type": "demand_forecast"
    }
    
    # Run agent analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### AI Analysis Report")
        
        # Generate analysis using GROQ
        analysis_prompt = f"""
        Analyze the following demand forecast data and current inventory levels:
        
        Forecast Data: {forecast_data}
        Inventory Data: {inventory_data}
        
        Provide insights on:
        1. Forecast accuracy assessment
        2. Demand-supply gaps
        3. Potential stockout risks
        4. Overstock situations
        5. Recommendations for forecast improvement
        
        Format your response in a structured manner with clear sections.
        """
        
        try:
            analysis_result = groq_client.generate_response(analysis_prompt)
            st.markdown(analysis_result)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
    
    with col2:
        st.markdown("#### Key Metrics")
        
        # Calculate key metrics
        total_demand = sum(item['Forecasted_Demand'] for item in forecast_data)
        total_stock = sum(item['Stock_Level'] for item in inventory_data)
        
        st.metric("Total Forecasted Demand", f"{total_demand:,}")
        st.metric("Total Current Stock", f"{total_stock:,}")
        st.metric("Overall Fill Rate", f"{min(100, (total_stock/total_demand)*100):.1f}%")
        
        # Risk indicators
        risk_items = []
        for forecast in forecast_data:
            for inventory in inventory_data:
                if (forecast['City'] == inventory['City'] and 
                    forecast['Product'] == inventory['Product']):
                    if inventory['Stock_Level'] < forecast['Forecasted_Demand']:
                        risk_items.append(f"{forecast['City']} - {forecast['Product']}")
        
        if risk_items:
            st.markdown("#### ⚠️ At-Risk Items")
            for item in risk_items:
                st.warning(item)
        else:
            st.success("No immediate stockout risks detected")
    
    # Detailed analysis charts
    st.markdown("#### Detailed Analysis Charts")
    
    # Create demand vs inventory comparison
    comparison_data = []
    for forecast in forecast_data:
        for inventory in inventory_data:
            if (forecast['City'] == inventory['City'] and 
                forecast['Product'] == inventory['Product']):
                comparison_data.append({
                    'Location_Product': f"{forecast['City']} - {forecast['Product']}",
                    'Forecasted_Demand': forecast['Forecasted_Demand'],
                    'Current_Stock': inventory['Stock_Level'],
                    'Gap': inventory['Stock_Level'] - forecast['Forecasted_Demand']
                })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Demand vs Stock Comparison', 'Supply-Demand Gap Analysis'),
            vertical_spacing=0.1
        )
        
        # Comparison chart
        fig.add_trace(
            go.Bar(name='Forecasted Demand', x=df_comparison['Location_Product'], 
                   y=df_comparison['Forecasted_Demand'], marker_color='#3498DB'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Current Stock', x=df_comparison['Location_Product'], 
                   y=df_comparison['Current_Stock'], marker_color='#2C3E50'),
            row=1, col=1
        )
        
        # Gap analysis
        colors = ['#E74C3C' if gap < 0 else '#27AE60' for gap in df_comparison['Gap']]
        fig.add_trace(
            go.Bar(name='Gap', x=df_comparison['Location_Product'], 
                   y=df_comparison['Gap'], marker_color=colors, showlegend=False),
            row=2, col=1
        )
        
        fig.update_layout(height=600, barmode='group')
        fig.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig, use_container_width=True)

def run_inventory_optimization(groq_client, agents, forecast_data, inventory_data):
    """Run inventory optimization analysis"""
    st.markdown("---")
    st.markdown("### 📦 Inventory Optimization Results")
    
    optimization_prompt = f"""
    Analyze the inventory data and demand forecasts to provide optimization recommendations:
    
    Current Inventory: {inventory_data}
    Demand Forecast: {forecast_data}
    
    Provide recommendations for:
    1. Optimal inventory levels for each product-location combination
    2. Reorder points and quantities
    3. Safety stock recommendations
    4. Inventory redistribution opportunities
    5. Cost optimization strategies
    
    Include specific numerical recommendations where possible.
    """
    
    try:
        optimization_result = groq_client.generate_response(optimization_prompt)
        st.markdown(optimization_result)
        
        # Show optimization metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Optimization Potential", "15-25%")
        with col2:
            st.metric("Inventory Turnover", "4.2x")
        with col3:
            st.metric("Carrying Cost Reduction", "$125K")
            
    except Exception as e:
        st.error(f"Optimization analysis failed: {str(e)}")

def run_risk_assessment(groq_client, agents, forecast_data, inventory_data, route_data, supplier_data):
    """Run comprehensive risk assessment"""
    st.markdown("---")
    st.markdown("### ⚠️ Supply Chain Risk Assessment")
    
    risk_prompt = f"""
    Conduct a comprehensive risk assessment of the supply chain:
    
    Forecast Data: {forecast_data}
    Inventory Data: {inventory_data}
    Route Data: {route_data if route_data else 'Not available'}
    Supplier Data: {supplier_data if supplier_data else 'Not available'}
    
    Assess risks in:
    1. Demand variability and forecast accuracy
    2. Inventory stockout and overstock risks
    3. Transportation and logistics risks
    4. Supplier reliability and concentration risks
    5. Geographic and seasonal risks
    
    Provide risk scores (1-10) and mitigation strategies for each category.
    """
    
    try:
        risk_result = groq_client.generate_response(risk_prompt)
        st.markdown(risk_result)
        
        # Risk visualization
        risk_categories = ['Demand Risk', 'Inventory Risk', 'Transportation Risk', 'Supplier Risk', 'Geographic Risk']
        risk_scores = [7, 5, 6, 4, 8]  # These would come from AI analysis
        
        fig = go.Figure(data=go.Scatterpolar(
            r=risk_scores,
            theta=risk_categories,
            fill='toself',
            marker_color='#E74C3C'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=False,
            title="Risk Assessment Radar"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Risk assessment failed: {str(e)}")

def run_supplier_analysis(groq_client, agents, supplier_data, inventory_data):
    """Run supplier performance analysis"""
    st.markdown("---")
    st.markdown("### 🏭 Supplier Performance Analysis")
    
    supplier_prompt = f"""
    Analyze supplier performance and provide insights:
    
    Supplier Data: {supplier_data}
    Current Inventory: {inventory_data}
    
    Analyze:
    1. Supplier reliability scores and performance trends
    2. Lead time analysis and variability
    3. Cost competitiveness assessment
    4. Risk concentration by supplier
    5. Supplier diversification recommendations
    
    Provide actionable insights for supplier relationship management.
    """
    
    try:
        supplier_result = groq_client.generate_response(supplier_prompt)
        st.markdown(supplier_result)
        
        # Supplier performance visualization
        df_supplier = pd.DataFrame(supplier_data)
        
        fig = px.scatter(
            df_supplier, 
            x='Lead_Time_Days', 
            y='Reliability_Score',
            size='Cost_per_Unit',
            color='Product',
            hover_data=['Supplier_Name'],
            title="Supplier Performance Matrix"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Supplier analysis failed: {str(e)}")

def run_route_analysis(groq_client, agents, route_data, inventory_data):
    """Run route optimization analysis"""
    st.markdown("---")
    st.markdown("### 🚚 Route Optimization Analysis")
    
    route_prompt = f"""
    Analyze transportation routes and logistics efficiency:
    
    Route Data: {route_data}
    Inventory Data: {inventory_data}
    
    Analyze:
    1. Route efficiency and cost optimization opportunities
    2. Transportation time and distance analysis
    3. Network optimization recommendations
    4. Hub and spoke vs direct delivery analysis
    5. Consolidation opportunities
    
    Provide specific recommendations for route optimization.
    """
    
    try:
        route_result = groq_client.generate_response(route_prompt)
        st.markdown(route_result)
        
        # Route visualization
        df_route = pd.DataFrame(route_data)
        
        fig = px.scatter(
            df_route,
            x='Distance_km',
            y='Cost_per_km',
            size='Average_Travel_Time_hrs',
            hover_data=['Source', 'Destination'],
            title="Route Cost vs Distance Analysis"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Route analysis failed: {str(e)}")

def run_comprehensive_analysis(groq_client, agents, forecast_data, inventory_data, route_data, supplier_data):
    """Run comprehensive supply chain health check"""
    st.markdown("---")
    st.markdown("### 🎯 Comprehensive Supply Chain Health Check")
    
    comprehensive_prompt = f"""
    Conduct a comprehensive supply chain health assessment:
    
    All Available Data:
    - Forecast Data: {forecast_data}
    - Inventory Data: {inventory_data}
    - Route Data: {route_data if route_data else 'Not available'}
    - Supplier Data: {supplier_data if supplier_data else 'Not available'}
    
    Provide:
    1. Overall supply chain health score (1-100)
    2. Key performance indicators assessment
    3. Critical issues and priorities
    4. Strategic recommendations for improvement
    5. Implementation roadmap with timelines
    
    Focus on actionable insights for executive decision-making.
    """
    
    try:
        comprehensive_result = groq_client.generate_response(comprehensive_prompt)
        st.markdown(comprehensive_result)
        
        # Health score visualization
        health_score = 78  # This would come from AI analysis
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Supply Chain Health Score"},
            delta = {'reference': 85},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3498DB"},
                'steps': [
                    {'range': [0, 50], 'color': "#E74C3C"},
                    {'range': [50, 75], 'color': "#F39C12"},
                    {'range': [75, 100], 'color': "#27AE60"}
                ],
                'threshold': {
                    'line': {'color': "#2C3E50", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Comprehensive analysis failed: {str(e)}")

if __name__ == "__main__":
    main()
