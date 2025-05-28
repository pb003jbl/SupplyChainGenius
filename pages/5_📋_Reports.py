import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from io import BytesIO
import base64
from utils.data_handler import DataHandler
from utils.groq_client import GroqClient

st.set_page_config(page_title="Reports", page_icon="📋", layout="wide")

def main():
    st.title("📋 Executive Reports & Analytics")
    st.markdown("Comprehensive reporting and business intelligence for supply chain management")
    
    data_handler = DataHandler()
    
    # Check data availability
    forecast_data = data_handler.get_forecast_data()
    inventory_data = data_handler.get_inventory_data()
    route_data = data_handler.get_route_data()
    supplier_data = data_handler.get_supplier_data()
    
    if not all([forecast_data, inventory_data]):
        st.warning("Please upload data before generating reports.")
        if st.button("Load Sample Data for Reports"):
            data_handler.load_sample_data()
            st.rerun()
        return
    
    # Report type selection
    st.markdown("### Report Configuration")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        report_type = st.selectbox(
            "Select Report Type",
            [
                "Executive Summary Dashboard",
                "Supply Chain Performance Report",
                "Inventory Analysis Report",
                "Cost Analysis Report",
                "Risk Assessment Report",
                "Supplier Performance Report",
                "Transportation & Logistics Report",
                "Demand Forecasting Report",
                "Custom Analytics Report"
            ]
        )
    
    with col2:
        report_period = st.selectbox(
            "Report Period",
            ["Current Month", "Last Quarter", "YTD", "Last 12 Months", "Custom Range"]
        )
    
    with col3:
        report_format = st.selectbox(
            "Output Format",
            ["Interactive Dashboard", "PDF Report", "Excel Workbook", "PowerPoint Summary"]
        )
    
    # Advanced report options
    with st.expander("Advanced Report Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_ai_insights = st.checkbox("Include AI Insights", value=True)
            include_recommendations = st.checkbox("Include Recommendations", value=True)
            include_forecasts = st.checkbox("Include Future Projections", value=True)
        
        with col2:
            detail_level = st.selectbox("Detail Level", ["Summary", "Detailed", "Comprehensive"])
            stakeholder_view = st.selectbox("Stakeholder View", ["C-Suite", "Operations", "Finance", "All"])
    
    # Generate report
    if st.button("📊 Generate Report", type="primary"):
        with st.spinner("Generating comprehensive report..."):
            generate_report(
                report_type, 
                report_period, 
                report_format,
                forecast_data, 
                inventory_data, 
                route_data, 
                supplier_data,
                {
                    'include_ai_insights': include_ai_insights,
                    'include_recommendations': include_recommendations,
                    'include_forecasts': include_forecasts,
                    'detail_level': detail_level,
                    'stakeholder_view': stakeholder_view
                }
            )

def generate_report(report_type, period, format_type, forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate the selected report type"""
    
    if report_type == "Executive Summary Dashboard":
        generate_executive_summary(forecast_data, inventory_data, route_data, supplier_data, options)
    
    elif report_type == "Supply Chain Performance Report":
        generate_performance_report(forecast_data, inventory_data, route_data, supplier_data, options)
    
    elif report_type == "Inventory Analysis Report":
        generate_inventory_report(forecast_data, inventory_data, options)
    
    elif report_type == "Cost Analysis Report":
        generate_cost_report(forecast_data, inventory_data, route_data, supplier_data, options)
    
    elif report_type == "Risk Assessment Report":
        generate_risk_report(forecast_data, inventory_data, route_data, supplier_data, options)
    
    elif report_type == "Supplier Performance Report":
        if supplier_data:
            generate_supplier_report(supplier_data, forecast_data, options)
        else:
            st.error("Supplier data not available")
    
    elif report_type == "Transportation & Logistics Report":
        if route_data:
            generate_logistics_report(route_data, inventory_data, options)
        else:
            st.error("Route data not available")
    
    elif report_type == "Demand Forecasting Report":
        generate_demand_report(forecast_data, inventory_data, options)
    
    elif report_type == "Custom Analytics Report":
        generate_custom_report(forecast_data, inventory_data, route_data, supplier_data, options)

def generate_executive_summary(forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate executive summary dashboard"""
    st.markdown("---")
    st.markdown("# 📊 Executive Summary Dashboard")
    st.markdown(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Key metrics overview
    st.markdown("## Key Performance Indicators")
    
    # Calculate key metrics
    total_demand = sum(item['Forecasted_Demand'] for item in forecast_data)
    total_stock = sum(item['Stock_Level'] for item in inventory_data)
    fill_rate = min(100, (total_stock / total_demand) * 100) if total_demand > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Supply Chain Health",
            f"{78}%",
            delta="5%",
            help="Overall supply chain performance score"
        )
    
    with col2:
        st.metric(
            "Fill Rate",
            f"{fill_rate:.1f}%",
            delta="3.2%",
            help="Percentage of demand met from stock"
        )
    
    with col3:
        if route_data:
            avg_cost = sum(r['Distance_km'] * r['Cost_per_km'] for r in route_data) / len(route_data)
            st.metric(
                "Avg Transportation Cost",
                f"${avg_cost:,.0f}",
                delta="-8%",
                help="Average cost per route"
            )
        else:
            st.metric("Transportation Cost", "N/A")
    
    with col4:
        inventory_value = sum(item['Stock_Level'] * 10 for item in inventory_data)  # Assume $10 per unit
        st.metric(
            "Inventory Value",
            f"${inventory_value:,}",
            delta="-2%",
            help="Total inventory value"
        )
    
    # Executive summary charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Supply-demand analysis
        st.markdown("### Supply vs Demand Analysis")
        
        supply_demand_data = []
        for forecast in forecast_data:
            for inventory in inventory_data:
                if (forecast['City'] == inventory['City'] and 
                    forecast['Product'] == inventory['Product']):
                    supply_demand_data.append({
                        'Location': forecast['City'],
                        'Product': forecast['Product'],
                        'Demand': forecast['Forecasted_Demand'],
                        'Supply': inventory['Stock_Level']
                    })
        
        if supply_demand_data:
            df_supply_demand = pd.DataFrame(supply_demand_data)
            
            fig = px.bar(
                df_supply_demand,
                x='Location',
                y=['Demand', 'Supply'],
                color_discrete_map={'Demand': '#E74C3C', 'Supply': '#3498DB'},
                title="Supply vs Demand by Location"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance trends
        st.markdown("### Performance Trends (30 Days)")
        
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        performance_data = {
            'Date': dates,
            'Fill_Rate': [fill_rate + (i % 10 - 5) for i in range(30)],
            'Cost_Efficiency': [75 + (i % 8 - 4) for i in range(30)],
            'Service_Level': [90 + (i % 6 - 3) for i in range(30)]
        }
        
        df_performance = pd.DataFrame(performance_data)
        
        fig = px.line(
            df_performance,
            x='Date',
            y=['Fill_Rate', 'Cost_Efficiency', 'Service_Level'],
            title="Key Performance Trends"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights section
    if options['include_ai_insights']:
        st.markdown("---")
        st.markdown("## 🤖 AI-Generated Insights")
        
        try:
            groq_client = GroqClient()
            
            insights_prompt = f"""
            Generate executive-level insights for supply chain performance:
            
            Data Summary:
            - Total Demand: {total_demand:,} units
            - Total Stock: {total_stock:,} units
            - Fill Rate: {fill_rate:.1f}%
            - Number of Locations: {len(set(item['City'] for item in forecast_data))}
            - Number of Products: {len(set(item['Product'] for item in forecast_data))}
            
            Provide:
            1. Key performance highlights
            2. Critical issues requiring attention
            3. Strategic opportunities
            4. Market trends and external factors
            
            Keep insights concise and actionable for C-suite executives.
            """
            
            insights = groq_client.generate_response(insights_prompt)
            st.markdown(insights)
            
        except Exception as e:
            st.warning("AI insights temporarily unavailable")
    
    # Recommendations section
    if options['include_recommendations']:
        st.markdown("---")
        st.markdown("## 📈 Strategic Recommendations")
        
        recommendations = [
            {
                "Priority": "High",
                "Area": "Inventory Optimization",
                "Recommendation": "Implement dynamic safety stock calculations to reduce excess inventory by 15%",
                "Impact": "$250K annual savings",
                "Timeline": "Q2 2024"
            },
            {
                "Priority": "Medium",
                "Area": "Transportation",
                "Recommendation": "Consolidate shipments on high-volume routes to reduce costs",
                "Impact": "12% cost reduction",
                "Timeline": "Q3 2024"
            },
            {
                "Priority": "High",
                "Area": "Demand Planning",
                "Recommendation": "Enhance forecast accuracy with machine learning models",
                "Impact": "8% improvement in fill rate",
                "Timeline": "Q1 2024"
            }
        ]
        
        df_recommendations = pd.DataFrame(recommendations)
        st.dataframe(df_recommendations, use_container_width=True)
    
    # Export options
    st.markdown("---")
    create_export_options("Executive_Summary", {
        'kpis': {'fill_rate': fill_rate, 'health_score': 78},
        'supply_demand': supply_demand_data,
        'performance': performance_data
    })

def generate_performance_report(forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate supply chain performance report"""
    st.markdown("---")
    st.markdown("# 📈 Supply Chain Performance Report")
    
    # Performance metrics calculation
    total_demand = sum(item['Forecasted_Demand'] for item in forecast_data)
    total_stock = sum(item['Stock_Level'] for item in inventory_data)
    
    # Performance scorecard
    st.markdown("## Performance Scorecard")
    
    metrics = {
        'Fill Rate': min(100, (total_stock / total_demand) * 100),
        'Inventory Turnover': 4.2,
        'Order Accuracy': 98.5,
        'On-Time Delivery': 94.2,
        'Cost Efficiency': 87.3,
        'Supplier Performance': 91.8 if supplier_data else 0
    }
    
    col1, col2, col3 = st.columns(3)
    
    for i, (metric, value) in enumerate(metrics.items()):
        with [col1, col2, col3][i % 3]:
            color = "#27AE60" if value >= 90 else "#F39C12" if value >= 80 else "#E74C3C"
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 15px; border-left: 4px solid {color}; margin: 10px 0;">
                <h3 style="margin: 0; color: {color};">{metric}</h3>
                <h2 style="margin: 5px 0; color: {color};">{value:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed performance analysis
    st.markdown("## Detailed Performance Analysis")
    
    # Location-wise performance
    location_performance = {}
    for forecast in forecast_data:
        for inventory in inventory_data:
            if (forecast['City'] == inventory['City'] and 
                forecast['Product'] == inventory['Product']):
                city = forecast['City']
                if city not in location_performance:
                    location_performance[city] = {'demand': 0, 'stock': 0}
                location_performance[city]['demand'] += forecast['Forecasted_Demand']
                location_performance[city]['stock'] += inventory['Stock_Level']
    
    performance_data = []
    for city, data in location_performance.items():
        fill_rate = min(100, (data['stock'] / data['demand']) * 100) if data['demand'] > 0 else 0
        performance_data.append({
            'Location': city,
            'Demand': data['demand'],
            'Stock': data['stock'],
            'Fill_Rate': fill_rate,
            'Performance_Grade': 'A' if fill_rate >= 95 else 'B' if fill_rate >= 85 else 'C'
        })
    
    df_performance = pd.DataFrame(performance_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance by location
        fig = px.bar(
            df_performance,
            x='Location',
            y='Fill_Rate',
            color='Performance_Grade',
            title="Fill Rate Performance by Location",
            color_discrete_map={'A': '#27AE60', 'B': '#F39C12', 'C': '#E74C3C'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance distribution
        grade_counts = df_performance['Performance_Grade'].value_counts()
        
        fig = px.pie(
            values=grade_counts.values,
            names=grade_counts.index,
            title="Performance Grade Distribution",
            color_discrete_map={'A': '#27AE60', 'B': '#F39C12', 'C': '#E74C3C'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance table
    st.markdown("### Location Performance Details")
    st.dataframe(df_performance, use_container_width=True)
    
    create_export_options("Performance_Report", {
        'metrics': metrics,
        'location_performance': performance_data
    })

def generate_inventory_report(forecast_data, inventory_data, options):
    """Generate inventory analysis report"""
    st.markdown("---")
    st.markdown("# 📦 Inventory Analysis Report")
    
    # Inventory metrics
    total_inventory_value = sum(item['Stock_Level'] * 10 for item in inventory_data)  # Assume $10 per unit
    total_demand = sum(item['Forecasted_Demand'] for item in forecast_data)
    
    st.markdown("## Inventory Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Inventory Value", f"${total_inventory_value:,}")
    with col2:
        st.metric("Total Units in Stock", f"{sum(item['Stock_Level'] for item in inventory_data):,}")
    with col3:
        st.metric("Average Days on Hand", "45 days")
    with col4:
        st.metric("Inventory Turnover", "4.2x annually")
    
    # Inventory analysis
    inventory_analysis = []
    for forecast in forecast_data:
        for inventory in inventory_data:
            if (forecast['City'] == inventory['City'] and 
                forecast['Product'] == inventory['Product']):
                days_supply = (inventory['Stock_Level'] / forecast['Forecasted_Demand']) * 30 if forecast['Forecasted_Demand'] > 0 else 0
                status = "Overstock" if days_supply > 60 else "Optimal" if days_supply >= 30 else "Understock"
                
                inventory_analysis.append({
                    'City': forecast['City'],
                    'Product': forecast['Product'],
                    'Current_Stock': inventory['Stock_Level'],
                    'Monthly_Demand': forecast['Forecasted_Demand'],
                    'Days_Supply': days_supply,
                    'Status': status,
                    'Inventory_Value': inventory['Stock_Level'] * 10
                })
    
    df_inventory = pd.DataFrame(inventory_analysis)
    
    # Inventory status visualization
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = df_inventory['Status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Inventory Status Distribution",
            color_discrete_map={
                'Optimal': '#27AE60',
                'Overstock': '#F39C12',
                'Understock': '#E74C3C'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            df_inventory,
            x='Monthly_Demand',
            y='Current_Stock',
            color='Status',
            size='Inventory_Value',
            hover_data=['City', 'Product'],
            title="Stock vs Demand Analysis",
            color_discrete_map={
                'Optimal': '#27AE60',
                'Overstock': '#F39C12',
                'Understock': '#E74C3C'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Inventory details table
    st.markdown("### Detailed Inventory Analysis")
    st.dataframe(df_inventory, use_container_width=True)
    
    # Inventory recommendations
    st.markdown("### Inventory Optimization Recommendations")
    
    overstock_items = df_inventory[df_inventory['Status'] == 'Overstock']
    understock_items = df_inventory[df_inventory['Status'] == 'Understock']
    
    if not overstock_items.empty:
        st.markdown("#### 📈 Overstock Items (Consider Redistribution)")
        st.dataframe(overstock_items[['City', 'Product', 'Current_Stock', 'Days_Supply']])
    
    if not understock_items.empty:
        st.markdown("#### 📉 Understock Items (Require Replenishment)")
        st.dataframe(understock_items[['City', 'Product', 'Current_Stock', 'Days_Supply']])
    
    create_export_options("Inventory_Report", {
        'inventory_analysis': inventory_analysis,
        'summary_metrics': {
            'total_value': total_inventory_value,
            'total_units': sum(item['Stock_Level'] for item in inventory_data)
        }
    })

def generate_cost_report(forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate cost analysis report"""
    st.markdown("---")
    st.markdown("# 💰 Cost Analysis Report")
    
    # Cost calculations
    inventory_holding_cost = sum(item['Stock_Level'] * 10 * 0.2 for item in inventory_data)  # 20% holding cost
    
    transportation_cost = 0
    if route_data:
        transportation_cost = sum(route['Distance_km'] * route['Cost_per_km'] for route in route_data)
    
    procurement_cost = 0
    if supplier_data:
        procurement_cost = sum(supplier['Cost_per_Unit'] * 1000 for supplier in supplier_data)  # Assume 1000 units each
    
    total_cost = inventory_holding_cost + transportation_cost + procurement_cost
    
    st.markdown("## Cost Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Supply Chain Cost", f"${total_cost:,.0f}")
    with col2:
        st.metric("Inventory Holding Cost", f"${inventory_holding_cost:,.0f}")
    with col3:
        st.metric("Transportation Cost", f"${transportation_cost:,.0f}")
    with col4:
        st.metric("Procurement Cost", f"${procurement_cost:,.0f}")
    
    # Cost breakdown visualization
    cost_data = {
        'Category': ['Inventory Holding', 'Transportation', 'Procurement', 'Other'],
        'Cost': [inventory_holding_cost, transportation_cost, procurement_cost, total_cost * 0.1],
        'Percentage': [
            (inventory_holding_cost / total_cost) * 100,
            (transportation_cost / total_cost) * 100,
            (procurement_cost / total_cost) * 100,
            10
        ]
    }
    
    df_costs = pd.DataFrame(cost_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            df_costs,
            values='Cost',
            names='Category',
            title="Cost Distribution by Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            df_costs,
            x='Category',
            y='Cost',
            title="Cost by Category ($)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost optimization opportunities
    st.markdown("### Cost Optimization Opportunities")
    
    optimization_data = [
        {
            'Opportunity': 'Inventory Optimization',
            'Current_Cost': f"${inventory_holding_cost:,.0f}",
            'Potential_Savings': f"${inventory_holding_cost * 0.15:,.0f}",
            'Savings_Percentage': '15%',
            'Implementation_Effort': 'Medium'
        },
        {
            'Opportunity': 'Route Optimization',
            'Current_Cost': f"${transportation_cost:,.0f}",
            'Potential_Savings': f"${transportation_cost * 0.12:,.0f}",
            'Savings_Percentage': '12%',
            'Implementation_Effort': 'Low'
        },
        {
            'Opportunity': 'Supplier Negotiation',
            'Current_Cost': f"${procurement_cost:,.0f}",
            'Potential_Savings': f"${procurement_cost * 0.08:,.0f}",
            'Savings_Percentage': '8%',
            'Implementation_Effort': 'High'
        }
    ]
    
    df_optimization = pd.DataFrame(optimization_data)
    st.dataframe(df_optimization, use_container_width=True)
    
    create_export_options("Cost_Report", {
        'cost_breakdown': cost_data,
        'optimization_opportunities': optimization_data
    })

def generate_risk_report(forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate risk assessment report"""
    st.markdown("---")
    st.markdown("# ⚠️ Supply Chain Risk Assessment Report")
    
    # Risk assessment
    risk_factors = {
        'Demand Variability': 7,
        'Supplier Reliability': 5 if supplier_data else 8,
        'Transportation Disruption': 6,
        'Inventory Stockout': 8,
        'Geographic Concentration': 7,
        'Regulatory Changes': 4,
        'Economic Volatility': 6,
        'Natural Disasters': 5
    }
    
    st.markdown("## Risk Scorecard")
    st.markdown("*Risk scores: 1 (Low) to 10 (High)*")
    
    # Risk visualization
    df_risk = pd.DataFrame([
        {'Risk_Factor': factor, 'Score': score, 'Level': 'High' if score >= 8 else 'Medium' if score >= 6 else 'Low'}
        for factor, score in risk_factors.items()
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_risk,
            x='Risk_Factor',
            y='Score',
            color='Level',
            title="Risk Assessment by Factor",
            color_discrete_map={'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}
        )
        
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(risk_factors.values()),
            theta=list(risk_factors.keys()),
            fill='toself',
            name='Risk Profile',
            fillcolor='rgba(228, 76, 60, 0.3)',
            line_color='#E74C3C'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=False,
            title="Risk Profile Radar"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk mitigation strategies
    st.markdown("### Risk Mitigation Strategies")
    
    mitigation_strategies = [
        {
            'Risk_Factor': 'Demand Variability',
            'Current_Score': 7,
            'Mitigation_Strategy': 'Implement advanced demand forecasting with AI/ML models',
            'Expected_Impact': 'Reduce to 5',
            'Timeline': '6 months',
            'Investment_Required': '$150K'
        },
        {
            'Risk_Factor': 'Inventory Stockout',
            'Current_Score': 8,
            'Mitigation_Strategy': 'Optimize safety stock levels and implement dynamic reordering',
            'Expected_Impact': 'Reduce to 5',
            'Timeline': '3 months',
            'Investment_Required': '$75K'
        },
        {
            'Risk_Factor': 'Geographic Concentration',
            'Current_Score': 7,
            'Mitigation_Strategy': 'Diversify supplier base and distribution centers',
            'Expected_Impact': 'Reduce to 4',
            'Timeline': '12 months',
            'Investment_Required': '$500K'
        }
    ]
    
    df_mitigation = pd.DataFrame(mitigation_strategies)
    st.dataframe(df_mitigation, use_container_width=True)
    
    create_export_options("Risk_Report", {
        'risk_scores': risk_factors,
        'mitigation_strategies': mitigation_strategies
    })

def generate_supplier_report(supplier_data, forecast_data, options):
    """Generate supplier performance report"""
    st.markdown("---")
    st.markdown("# 🏭 Supplier Performance Report")
    
    df_suppliers = pd.DataFrame(supplier_data)
    
    # Supplier performance metrics
    avg_reliability = df_suppliers['Reliability_Score'].mean()
    avg_lead_time = df_suppliers['Lead_Time_Days'].mean()
    avg_cost = df_suppliers['Cost_per_Unit'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Number of Suppliers", len(df_suppliers))
    with col2:
        st.metric("Average Reliability", f"{avg_reliability:.1f}%")
    with col3:
        st.metric("Average Lead Time", f"{avg_lead_time:.1f} days")
    with col4:
        st.metric("Average Cost per Unit", f"${avg_cost:.2f}")
    
    # Supplier performance analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Reliability vs Cost scatter plot
        fig = px.scatter(
            df_suppliers,
            x='Cost_per_Unit',
            y='Reliability_Score',
            size='Lead_Time_Days',
            color='Product',
            hover_data=['Supplier_Name'],
            title="Supplier Performance Matrix"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Supplier ranking
        df_suppliers['Performance_Score'] = (
            df_suppliers['Reliability_Score'] * 0.5 +
            (100 - df_suppliers['Lead_Time_Days']) * 0.3 +
            (100 - df_suppliers['Cost_per_Unit']) * 0.2
        )
        
        df_ranked = df_suppliers.nlargest(10, 'Performance_Score')
        
        fig = px.bar(
            df_ranked,
            x='Supplier_Name',
            y='Performance_Score',
            title="Top 10 Supplier Performance Scores"
        )
        
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed supplier table
    st.markdown("### Supplier Performance Details")
    st.dataframe(df_suppliers.sort_values('Performance_Score', ascending=False), use_container_width=True)
    
    create_export_options("Supplier_Report", {
        'supplier_data': supplier_data,
        'performance_metrics': {
            'avg_reliability': avg_reliability,
            'avg_lead_time': avg_lead_time,
            'avg_cost': avg_cost
        }
    })

def generate_logistics_report(route_data, inventory_data, options):
    """Generate transportation and logistics report"""
    st.markdown("---")
    st.markdown("# 🚚 Transportation & Logistics Report")
    
    df_routes = pd.DataFrame(route_data)
    
    # Logistics metrics
    total_distance = df_routes['Distance_km'].sum()
    total_cost = (df_routes['Distance_km'] * df_routes['Cost_per_km']).sum()
    avg_cost_per_km = df_routes['Cost_per_km'].mean()
    avg_travel_time = df_routes['Average_Travel_Time_hrs'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Route Distance", f"{total_distance:,} km")
    with col2:
        st.metric("Total Transportation Cost", f"${total_cost:,.0f}")
    with col3:
        st.metric("Average Cost per km", f"${avg_cost_per_km:.2f}")
    with col4:
        st.metric("Average Travel Time", f"{avg_travel_time:.1f} hours")
    
    # Route analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost vs Distance analysis
        fig = px.scatter(
            df_routes,
            x='Distance_km',
            y=df_routes['Distance_km'] * df_routes['Cost_per_km'],
            size='Average_Travel_Time_hrs',
            hover_data=['Source', 'Destination'],
            title="Route Cost vs Distance Analysis"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Route efficiency
        df_routes['Cost_Efficiency'] = df_routes['Distance_km'] / (df_routes['Distance_km'] * df_routes['Cost_per_km'])
        
        fig = px.bar(
            df_routes,
            x='Source',
            y='Cost_Efficiency',
            title="Route Cost Efficiency by Source"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Route details
    st.markdown("### Route Performance Details")
    df_routes['Total_Cost'] = df_routes['Distance_km'] * df_routes['Cost_per_km']
    st.dataframe(df_routes, use_container_width=True)
    
    create_export_options("Logistics_Report", {
        'route_data': route_data,
        'logistics_metrics': {
            'total_distance': total_distance,
            'total_cost': total_cost,
            'avg_cost_per_km': avg_cost_per_km
        }
    })

def generate_demand_report(forecast_data, inventory_data, options):
    """Generate demand forecasting report"""
    st.markdown("---")
    st.markdown("# 📈 Demand Forecasting Report")
    
    df_forecast = pd.DataFrame(forecast_data)
    
    # Demand analysis
    total_demand = df_forecast['Forecasted_Demand'].sum()
    avg_demand = df_forecast['Forecasted_Demand'].mean()
    demand_by_product = df_forecast.groupby('Product')['Forecasted_Demand'].sum()
    demand_by_city = df_forecast.groupby('City')['Forecasted_Demand'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Forecasted Demand", f"{total_demand:,} units")
    with col2:
        st.metric("Average Demand per Location", f"{avg_demand:.0f} units")
    with col3:
        st.metric("Number of Products", len(demand_by_product))
    with col4:
        st.metric("Number of Locations", len(demand_by_city))
    
    # Demand visualization
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=demand_by_product.values,
            names=demand_by_product.index,
            title="Demand Distribution by Product"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=demand_by_city.index,
            y=demand_by_city.values,
            title="Demand by Location"
        )
        
        fig.update_xaxes(title="City")
        fig.update_yaxes(title="Forecasted Demand")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Forecast accuracy analysis
    st.markdown("### Forecast Accuracy Analysis")
    
    accuracy_data = []
    for forecast in forecast_data:
        for inventory in inventory_data:
            if (forecast['City'] == inventory['City'] and 
                forecast['Product'] == inventory['Product']):
                # Simulate historical actual demand
                actual_demand = forecast['Forecasted_Demand'] * (0.9 + 0.2 * (hash(forecast['City'] + forecast['Product']) % 100) / 100)
                accuracy = 100 - abs(forecast['Forecasted_Demand'] - actual_demand) / forecast['Forecasted_Demand'] * 100
                
                accuracy_data.append({
                    'City': forecast['City'],
                    'Product': forecast['Product'],
                    'Forecasted': forecast['Forecasted_Demand'],
                    'Actual': int(actual_demand),
                    'Accuracy': accuracy
                })
    
    if accuracy_data:
        df_accuracy = pd.DataFrame(accuracy_data)
        
        avg_accuracy = df_accuracy['Accuracy'].mean()
        st.metric("Average Forecast Accuracy", f"{avg_accuracy:.1f}%")
        
        fig = px.scatter(
            df_accuracy,
            x='Forecasted',
            y='Actual',
            color='Accuracy',
            hover_data=['City', 'Product'],
            title="Forecast vs Actual Demand"
        )
        
        # Add perfect accuracy line
        max_val = max(df_accuracy['Forecasted'].max(), df_accuracy['Actual'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Perfect Accuracy',
            line=dict(dash='dash', color='red')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_accuracy, use_container_width=True)
    
    create_export_options("Demand_Report", {
        'forecast_data': forecast_data,
        'demand_metrics': {
            'total_demand': total_demand,
            'avg_demand': avg_demand
        }
    })

def generate_custom_report(forecast_data, inventory_data, route_data, supplier_data, options):
    """Generate custom analytics report"""
    st.markdown("---")
    st.markdown("# 📊 Custom Analytics Report")
    
    st.markdown("### Custom Analysis Options")
    
    # Custom analysis selection
    analysis_options = st.multiselect(
        "Select Analysis Components",
        [
            "Cross-Product Analysis",
            "Geographic Performance Heatmap",
            "Seasonal Demand Patterns",
            "Supply Chain Network Analysis",
            "Cost-Benefit Optimization",
            "Predictive Analytics",
            "Benchmark Comparison"
        ],
        default=["Cross-Product Analysis", "Geographic Performance Heatmap"]
    )
    
    if "Cross-Product Analysis" in analysis_options:
        st.markdown("#### Cross-Product Analysis")
        
        df_forecast = pd.DataFrame(forecast_data)
        product_performance = df_forecast.groupby('Product').agg({
            'Forecasted_Demand': ['sum', 'mean', 'count']
        }).round(2)
        
        st.dataframe(product_performance)
    
    if "Geographic Performance Heatmap" in analysis_options:
        st.markdown("#### Geographic Performance Analysis")
        
        city_performance = {}
        for forecast in forecast_data:
            for inventory in inventory_data:
                if (forecast['City'] == inventory['City'] and 
                    forecast['Product'] == inventory['Product']):
                    city = forecast['City']
                    if city not in city_performance:
                        city_performance[city] = {'total_demand': 0, 'total_stock': 0}
                    city_performance[city]['total_demand'] += forecast['Forecasted_Demand']
                    city_performance[city]['total_stock'] += inventory['Stock_Level']
        
        performance_data = []
        for city, data in city_performance.items():
            fill_rate = min(100, (data['total_stock'] / data['total_demand']) * 100) if data['total_demand'] > 0 else 0
            performance_data.append({
                'City': city,
                'Fill_Rate': fill_rate,
                'Total_Demand': data['total_demand'],
                'Total_Stock': data['total_stock']
            })
        
        df_geo = pd.DataFrame(performance_data)
        
        fig = px.bar(
            df_geo,
            x='City',
            y='Fill_Rate',
            color='Fill_Rate',
            title="Fill Rate by Geographic Location",
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    create_export_options("Custom_Report", {
        'selected_analyses': analysis_options,
        'custom_data': {}
    })

def create_export_options(report_name, report_data):
    """Create export options for reports"""
    st.markdown("---")
    st.markdown("### Export Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Export as PDF"):
            st.info("PDF export functionality would be implemented here")
    
    with col2:
        if st.button("📊 Export to Excel"):
            # Create Excel export
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Convert report data to DataFrames and save to Excel
                for sheet_name, data in report_data.items():
                    if isinstance(data, list) and data:
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Excel File",
                data=excel_buffer.getvalue(),
                file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if st.button("📈 Export to PowerPoint"):
            st.info("PowerPoint export functionality would be implemented here")
    
    with col4:
        # JSON export
        json_data = json.dumps(report_data, indent=2, default=str)
        st.download_button(
            label="📋 Export as JSON",
            data=json_data,
            file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
