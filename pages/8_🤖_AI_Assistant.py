import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_handler import DataHandler
from utils.groq_client import GroqClient
from utils.agents import SupplyChainAgents
import json
from datetime import datetime, timedelta

def main():
    st.title("🤖 AI Supply Chain Assistant")
    st.markdown("Intelligent conversational AI for supply chain management and decision support")
    
    # Initialize components
    data_handler = DataHandler()
    groq_client = GroqClient()
    agents = SupplyChainAgents()
    
    # Load data
    forecast_data = data_handler.get_forecast_data()
    inventory_data = data_handler.get_inventory_data()
    route_data = data_handler.get_route_data()
    supplier_data = data_handler.get_supplier_data()
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat Assistant", 
        "📊 Smart Analytics", 
        "🎯 Decision Support",
        "📈 Predictive Insights"
    ])
    
    with tab1:
        st.markdown("### Conversational AI Assistant")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display chat history
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        
                        # Display data visualizations if present
                        if "chart_data" in message:
                            if message["chart_data"]["type"] == "metrics":
                                metrics = message["chart_data"]["data"]
                                cols = st.columns(len(metrics))
                                for i, (key, value) in enumerate(metrics.items()):
                                    cols[i].metric(key, value)
                            elif message["chart_data"]["type"] == "chart":
                                st.plotly_chart(message["chart_data"]["figure"], use_container_width=True)
            
            # Chat input
            if prompt := st.chat_input("Ask me about your supply chain..."):
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing your request..."):
                        response = generate_ai_response(prompt, groq_client, agents, 
                                                     forecast_data, inventory_data, 
                                                     route_data, supplier_data)
                        
                        st.markdown(response["content"])
                        
                        # Display generated charts or metrics
                        if "chart_data" in response:
                            if response["chart_data"]["type"] == "metrics":
                                metrics = response["chart_data"]["data"]
                                cols = st.columns(len(metrics))
                                for i, (key, value) in enumerate(metrics.items()):
                                    cols[i].metric(key, value)
                            elif response["chart_data"]["type"] == "chart":
                                st.plotly_chart(response["chart_data"]["figure"], use_container_width=True)
                        
                        # Add assistant response to history
                        st.session_state.chat_history.append(response)
        
        with col2:
            st.markdown("#### Quick Actions")
            
            if st.button("📊 Inventory Status"):
                if inventory_data:
                    response = generate_quick_analysis("inventory_status", inventory_data, groq_client)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
            
            if st.button("🚚 Route Performance"):
                if route_data:
                    response = generate_quick_analysis("route_performance", route_data, groq_client)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
            
            if st.button("📈 Demand Forecast"):
                if forecast_data:
                    response = generate_quick_analysis("demand_forecast", forecast_data, groq_client)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
            
            if st.button("⚠️ Risk Assessment"):
                response = generate_quick_analysis("risk_assessment", 
                                                 {"inventory": inventory_data, "routes": route_data, 
                                                  "suppliers": supplier_data}, groq_client)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            
            if st.button("🧹 Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
            
            st.markdown("#### Suggested Questions")
            st.markdown("""
            - "What are my top inventory risks?"
            - "Show me cost optimization opportunities"
            - "Which routes need attention?"
            - "Predict next month's demand"
            - "Compare supplier performance"
            - "What's my carbon footprint?"
            """)
    
    with tab2:
        st.markdown("### Smart Analytics Engine")
        
        if not any([forecast_data, inventory_data, route_data, supplier_data]):
            st.warning("Please upload data to enable smart analytics.")
            return
        
        # Analytics options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            analytics_type = st.selectbox(
                "Select Analysis Type",
                ["Multi-dimensional Analysis", "Correlation Analysis", "Anomaly Detection", 
                 "Performance Benchmarking", "Cost Driver Analysis", "Efficiency Scoring"]
            )
            
            time_period = st.selectbox("Time Period", ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year"])
            
            if st.button("🔍 Run Smart Analysis", type="primary"):
                with st.spinner("Running advanced analytics..."):
                    analysis_result = run_smart_analytics(analytics_type, time_period, 
                                                        forecast_data, inventory_data, 
                                                        route_data, supplier_data, groq_client)
                    
                    if analysis_result:
                        st.markdown("#### Analysis Results")
                        st.markdown(analysis_result["summary"])
                        
                        if "visualizations" in analysis_result:
                            for viz in analysis_result["visualizations"]:
                                st.plotly_chart(viz, use_container_width=True)
                        
                        if "recommendations" in analysis_result:
                            st.markdown("#### Key Recommendations")
                            for i, rec in enumerate(analysis_result["recommendations"], 1):
                                st.markdown(f"**{i}.** {rec}")
        
        with col2:
            st.markdown("#### Analysis Insights")
            
            if inventory_data and route_data:
                # Quick metrics
                total_inventory_value = sum(item.get('Current_Stock', 0) * item.get('Unit_Cost', 0) for item in inventory_data)
                total_route_cost = sum(route.get('Distance_km', 0) * route.get('Cost_per_km', 0) for route in route_data)
                
                st.metric("Total Inventory Value", f"${total_inventory_value:,.0f}")
                st.metric("Monthly Route Costs", f"${total_route_cost:,.0f}")
                
                # Efficiency score
                if inventory_data:
                    avg_stock_ratio = sum(item.get('Current_Stock', 0) / max(item.get('Reorder_Point', 1), 1) 
                                        for item in inventory_data) / len(inventory_data)
                    efficiency_score = min(100, max(0, (2 - avg_stock_ratio) * 50))
                    st.metric("Efficiency Score", f"{efficiency_score:.0f}%")
    
    with tab3:
        st.markdown("### AI Decision Support System")
        
        # Decision scenarios
        decision_scenario = st.selectbox(
            "Select Decision Scenario",
            ["Capacity Planning", "Supplier Selection", "Route Optimization", 
             "Inventory Rebalancing", "Risk Mitigation", "Investment Planning"]
        )
        
        # Scenario-specific inputs
        if decision_scenario == "Capacity Planning":
            st.markdown("#### Capacity Planning Assistant")
            
            col1, col2 = st.columns(2)
            with col1:
                growth_rate = st.slider("Expected Growth Rate (%)", 0, 50, 15)
                time_horizon = st.selectbox("Planning Horizon", ["3 months", "6 months", "1 year", "2 years"])
            
            with col2:
                budget_constraint = st.number_input("Budget Constraint ($)", min_value=0, value=500000)
                priority_areas = st.multiselect("Priority Areas", 
                                               ["Warehouse", "Transportation", "Technology", "Staff"])
            
            if st.button("📋 Generate Capacity Plan"):
                with st.spinner("Generating capacity planning recommendations..."):
                    plan = generate_capacity_plan(growth_rate, time_horizon, budget_constraint, 
                                                priority_areas, inventory_data, route_data, groq_client)
                    
                    st.markdown("#### Recommended Capacity Plan")
                    st.markdown(plan)
        
        elif decision_scenario == "Supplier Selection":
            st.markdown("#### Intelligent Supplier Selection")
            
            if supplier_data:
                # Supplier comparison criteria
                criteria_weights = {}
                criteria_weights["Cost"] = st.slider("Cost Weight", 0.0, 1.0, 0.3)
                criteria_weights["Quality"] = st.slider("Quality Weight", 0.0, 1.0, 0.25)
                criteria_weights["Delivery"] = st.slider("Delivery Reliability Weight", 0.0, 1.0, 0.25)
                criteria_weights["Sustainability"] = st.slider("Sustainability Weight", 0.0, 1.0, 0.2)
                
                if st.button("🏆 Rank Suppliers"):
                    ranking = rank_suppliers(supplier_data, criteria_weights, groq_client)
                    
                    st.markdown("#### Supplier Rankings")
                    for i, supplier in enumerate(ranking, 1):
                        with st.expander(f"#{i} {supplier['name']} (Score: {supplier['score']:.1f})"):
                            st.write(supplier['analysis'])
    
    with tab4:
        st.markdown("### Predictive Insights & Forecasting")
        
        # Prediction types
        prediction_type = st.selectbox(
            "Select Prediction Type",
            ["Demand Forecasting", "Risk Prediction", "Cost Forecasting", 
             "Supply Disruption", "Market Trends", "Seasonal Patterns"]
        )
        
        forecast_horizon = st.selectbox("Forecast Horizon", 
                                      ["1 week", "1 month", "3 months", "6 months", "1 year"])
        
        confidence_level = st.slider("Confidence Level (%)", 80, 99, 95)
        
        if st.button("🔮 Generate Predictions", type="primary"):
            with st.spinner("Running predictive models..."):
                predictions = generate_predictions(prediction_type, forecast_horizon, confidence_level,
                                                 forecast_data, inventory_data, route_data, 
                                                 supplier_data, groq_client)
                
                if predictions:
                    st.markdown("#### Predictive Analysis Results")
                    
                    # Display prediction summary
                    st.markdown(predictions["summary"])
                    
                    # Show prediction charts
                    if "charts" in predictions:
                        for chart in predictions["charts"]:
                            st.plotly_chart(chart, use_container_width=True)
                    
                    # Risk indicators
                    if "risks" in predictions:
                        st.markdown("#### Risk Indicators")
                        for risk in predictions["risks"]:
                            if risk["severity"] == "High":
                                st.error(f"🔴 **{risk['category']}**: {risk['description']}")
                            elif risk["severity"] == "Medium":
                                st.warning(f"🟡 **{risk['category']}**: {risk['description']}")
                            else:
                                st.info(f"🟢 **{risk['category']}**: {risk['description']}")
                    
                    # Action recommendations
                    if "actions" in predictions:
                        st.markdown("#### Recommended Actions")
                        for action in predictions["actions"]:
                            st.markdown(f"- {action}")

def generate_ai_response(prompt, groq_client, agents, forecast_data, inventory_data, route_data, supplier_data):
    """Generate intelligent AI response based on user prompt"""
    
    # Prepare data context
    data_context = {
        "forecast": forecast_data,
        "inventory": inventory_data,
        "routes": route_data,
        "suppliers": supplier_data
    }
    
    # Analyze the prompt to determine intent
    if any(word in prompt.lower() for word in ["inventory", "stock", "warehouse"]):
        analysis_type = "inventory_analysis"
    elif any(word in prompt.lower() for word in ["route", "transport", "logistics", "delivery"]):
        analysis_type = "route_analysis"
    elif any(word in prompt.lower() for word in ["demand", "forecast", "predict"]):
        analysis_type = "demand_forecast"
    elif any(word in prompt.lower() for word in ["supplier", "vendor", "partner"]):
        analysis_type = "supplier_analysis"
    elif any(word in prompt.lower() for word in ["risk", "threat", "danger"]):
        analysis_type = "risk_assessment"
    elif any(word in prompt.lower() for word in ["cost", "expense", "budget", "money"]):
        analysis_type = "cost_analysis"
    else:
        analysis_type = "general_analysis"
    
    try:
        # Generate response using AI agents
        enhanced_prompt = f"""
        User Question: {prompt}
        
        Context: Supply chain management platform with data on inventory, routes, suppliers, and demand forecasts.
        
        Please provide a comprehensive response that:
        1. Directly addresses the user's question
        2. Uses the available data to provide specific insights
        3. Includes actionable recommendations
        4. Maintains a professional yet conversational tone
        
        Available data summary:
        - Inventory items: {len(inventory_data) if inventory_data else 0}
        - Routes: {len(route_data) if route_data else 0}
        - Suppliers: {len(supplier_data) if supplier_data else 0}
        - Forecast periods: {len(forecast_data) if forecast_data else 0}
        """
        
        response = groq_client.generate_response(enhanced_prompt)
        
        # Check if we should generate visualizations
        chart_data = None
        if any(word in prompt.lower() for word in ["show", "chart", "graph", "visualize", "plot"]):
            chart_data = generate_response_visualization(analysis_type, data_context)
        
        return {
            "role": "assistant",
            "content": response,
            "chart_data": chart_data
        }
        
    except Exception as e:
        return {
            "role": "assistant",
            "content": f"I'm having trouble processing your request right now. Please ensure your AI service is properly configured in Settings. Error: {str(e)}"
        }

def generate_quick_analysis(analysis_type, data, groq_client):
    """Generate quick analysis for predefined scenarios"""
    
    prompts = {
        "inventory_status": "Provide a concise inventory status summary including key metrics, stock levels, and immediate action items.",
        "route_performance": "Analyze route performance data and highlight efficiency metrics, cost optimization opportunities, and performance trends.",
        "demand_forecast": "Summarize demand forecasting insights including trends, seasonality, and accuracy metrics.",
        "risk_assessment": "Conduct a comprehensive risk assessment covering operational, financial, and strategic risks with mitigation recommendations."
    }
    
    try:
        prompt = prompts.get(analysis_type, "Provide a general analysis of the provided data.")
        
        if isinstance(data, dict):
            data_summary = f"Data includes: {', '.join(data.keys())}"
        else:
            data_summary = f"Data points: {len(data) if data else 0}"
        
        enhanced_prompt = f"{prompt}\n\nData context: {data_summary}"
        
        return groq_client.generate_response(enhanced_prompt, temperature=0.2)
        
    except Exception as e:
        return f"Unable to generate analysis. Please check your AI configuration. Error: {str(e)}"

def generate_response_visualization(analysis_type, data_context):
    """Generate appropriate visualization based on analysis type"""
    
    try:
        if analysis_type == "inventory_analysis" and data_context["inventory"]:
            # Create inventory level chart
            inventory_data = data_context["inventory"]
            df = pd.DataFrame(inventory_data)
            
            fig = px.bar(df.head(10), x='Product_Name', y='Current_Stock', 
                        title="Top 10 Products by Stock Level")
            fig.update_layout(xaxis_tickangle=-45)
            
            return {"type": "chart", "figure": fig}
            
        elif analysis_type == "route_analysis" and data_context["routes"]:
            # Create route cost analysis
            route_data = data_context["routes"]
            total_cost = sum(r.get('Distance_km', 0) * r.get('Cost_per_km', 0) for r in route_data)
            avg_distance = sum(r.get('Distance_km', 0) for r in route_data) / len(route_data)
            
            return {
                "type": "metrics",
                "data": {
                    "Total Route Cost": f"${total_cost:,.0f}",
                    "Average Distance": f"{avg_distance:.0f} km",
                    "Active Routes": len(route_data)
                }
            }
        
        return None
        
    except Exception:
        return None

def run_smart_analytics(analytics_type, time_period, forecast_data, inventory_data, route_data, supplier_data, groq_client):
    """Run advanced analytics based on selected type"""
    
    try:
        analysis_prompt = f"""
        Conduct a {analytics_type} for the {time_period} period.
        
        Available data:
        - Inventory items: {len(inventory_data) if inventory_data else 0}
        - Routes: {len(route_data) if route_data else 0}
        - Suppliers: {len(supplier_data) if supplier_data else 0}
        - Forecast data: {len(forecast_data) if forecast_data else 0}
        
        Provide:
        1. Executive summary
        2. Key findings
        3. Performance metrics
        4. Actionable recommendations
        5. Risk factors
        """
        
        summary = groq_client.generate_response(analysis_prompt, temperature=0.2)
        
        # Generate sample recommendations
        recommendations = [
            "Optimize inventory levels for top 20% of SKUs to reduce carrying costs",
            "Consolidate routes in high-density areas to improve efficiency",
            "Implement predictive maintenance for critical supply chain assets",
            "Diversify supplier base to reduce concentration risk"
        ]
        
        return {
            "summary": summary,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {"summary": f"Unable to generate analytics. Please check your AI configuration. Error: {str(e)}"}

def generate_capacity_plan(growth_rate, time_horizon, budget, priority_areas, inventory_data, route_data, groq_client):
    """Generate capacity planning recommendations"""
    
    try:
        prompt = f"""
        Generate a comprehensive capacity plan with the following parameters:
        - Expected growth rate: {growth_rate}%
        - Planning horizon: {time_horizon}
        - Budget constraint: ${budget:,}
        - Priority areas: {', '.join(priority_areas)}
        
        Current capacity metrics:
        - Inventory locations: {len(set(item.get('Location', 'Unknown') for item in inventory_data)) if inventory_data else 0}
        - Active routes: {len(route_data) if route_data else 0}
        
        Provide specific recommendations for scaling operations.
        """
        
        return groq_client.generate_response(prompt, temperature=0.3)
        
    except Exception as e:
        return f"Unable to generate capacity plan. Please check your AI configuration. Error: {str(e)}"

def rank_suppliers(supplier_data, criteria_weights, groq_client):
    """Rank suppliers based on weighted criteria"""
    
    try:
        rankings = []
        
        for supplier in supplier_data:
            # Calculate weighted score
            score = 0
            name = supplier.get('Supplier_Name', 'Unknown')
            
            # Normalize and weight criteria (simplified scoring)
            cost_score = min(100, max(0, 100 - (supplier.get('Cost_per_Unit', 50) - 20) * 2))
            quality_score = supplier.get('Quality_Rating', 3) * 20  # Convert to 0-100 scale
            delivery_score = supplier.get('Delivery_Performance', 0.8) * 100
            sustainability_score = 75  # Default sustainability score
            
            score = (cost_score * criteria_weights['Cost'] + 
                    quality_score * criteria_weights['Quality'] +
                    delivery_score * criteria_weights['Delivery'] + 
                    sustainability_score * criteria_weights['Sustainability'])
            
            analysis = f"Strong performance in delivery ({delivery_score:.0f}%) and quality ({quality_score:.0f}%). Cost efficiency: {cost_score:.0f}%"
            
            rankings.append({
                'name': name,
                'score': score,
                'analysis': analysis
            })
        
        return sorted(rankings, key=lambda x: x['score'], reverse=True)
        
    except Exception:
        return [{'name': 'Analysis Error', 'score': 0, 'analysis': 'Unable to rank suppliers'}]

def generate_predictions(prediction_type, horizon, confidence, forecast_data, inventory_data, route_data, supplier_data, groq_client):
    """Generate predictive insights"""
    
    try:
        prompt = f"""
        Generate {prediction_type} predictions for {horizon} with {confidence}% confidence level.
        
        Analyze patterns and trends to provide:
        1. Prediction summary
        2. Key risk factors
        3. Recommended actions
        4. Confidence intervals
        
        Base predictions on available supply chain data patterns.
        """
        
        summary = groq_client.generate_response(prompt, temperature=0.2)
        
        # Generate sample risk indicators
        risks = [
            {"category": "Demand Volatility", "severity": "Medium", "description": "Seasonal demand fluctuation expected"},
            {"category": "Supply Chain", "severity": "Low", "description": "Supplier performance within normal parameters"},
            {"category": "Cost Inflation", "severity": "High", "description": "Transportation costs trending upward"}
        ]
        
        actions = [
            "Increase safety stock for high-demand items",
            "Negotiate long-term contracts with key suppliers",
            "Implement dynamic pricing strategies",
            "Monitor market conditions closely"
        ]
        
        return {
            "summary": summary,
            "risks": risks,
            "actions": actions
        }
        
    except Exception as e:
        return {"summary": f"Unable to generate predictions. Please check your AI configuration. Error: {str(e)}"}

if __name__ == "__main__":
    main()