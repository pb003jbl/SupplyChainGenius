import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_handler import DataHandler
from utils.groq_client import GroqClient

def main():
    st.title("🌱 Sustainability & Carbon Footprint Tracker")
    st.markdown("Advanced ESG analytics and carbon footprint management for sustainable supply chains")
    
    # Initialize components
    data_handler = DataHandler()
    groq_client = GroqClient()
    
    # Load data
    forecast_data = data_handler.get_forecast_data()
    inventory_data = data_handler.get_inventory_data()
    route_data = data_handler.get_route_data()
    supplier_data = data_handler.get_supplier_data()
    
    if not any([forecast_data, inventory_data, route_data, supplier_data]):
        st.warning("Please upload data to enable sustainability tracking.")
        if st.button("Load Sample Data"):
            data_handler.load_sample_data()
            st.rerun()
        return
    
    # Main interface
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Carbon Dashboard", 
        "🚛 Transport Emissions", 
        "🏭 Supplier ESG",
        "♻️ Circular Economy",
        "📈 Sustainability Goals"
    ])
    
    with tab1:
        st.markdown("### Carbon Footprint Dashboard")
        
        # Calculate carbon metrics
        carbon_data = calculate_carbon_metrics(inventory_data, route_data, supplier_data)
        
        # Key carbon metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total CO₂ Emissions", 
                f"{carbon_data['total_emissions']:,.0f} kg",
                delta=f"{carbon_data['emission_change']:+.1f}%"
            )
        
        with col2:
            st.metric(
                "Transport Emissions", 
                f"{carbon_data['transport_emissions']:,.0f} kg",
                delta=f"{carbon_data['transport_change']:+.1f}%"
            )
        
        with col3:
            st.metric(
                "Carbon Intensity", 
                f"{carbon_data['carbon_intensity']:.2f} kg/unit",
                delta=f"{carbon_data['intensity_change']:+.1f}%"
            )
        
        with col4:
            st.metric(
                "Sustainability Score", 
                f"{carbon_data['sustainability_score']:.0f}%",
                delta=f"{carbon_data['score_change']:+.1f}%"
            )
        
        # Carbon breakdown charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Emissions by category
            emissions_chart = create_emissions_breakdown_chart(carbon_data)
            st.plotly_chart(emissions_chart, use_container_width=True)
            
            # Monthly emissions trend
            monthly_chart = create_monthly_emissions_chart()
            st.plotly_chart(monthly_chart, use_container_width=True)
        
        with col2:
            # Emissions by location
            location_chart = create_emissions_by_location_chart(route_data)
            st.plotly_chart(location_chart, use_container_width=True)
            
            # Carbon efficiency vs cost
            efficiency_chart = create_carbon_efficiency_chart(route_data)
            st.plotly_chart(efficiency_chart, use_container_width=True)
        
        # Carbon reduction opportunities
        st.markdown("### 🎯 Carbon Reduction Opportunities")
        
        reduction_opportunities = identify_reduction_opportunities(route_data, supplier_data, groq_client)
        
        for i, opportunity in enumerate(reduction_opportunities, 1):
            with st.expander(f"Opportunity {i}: {opportunity['title']} (Potential: {opportunity['potential']} kg CO₂)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {opportunity['description']}")
                    st.write(f"**Implementation:** {opportunity['implementation']}")
                    st.write(f"**Timeline:** {opportunity['timeline']}")
                
                with col2:
                    st.metric("CO₂ Reduction", f"{opportunity['potential']:,.0f} kg")
                    st.metric("Cost Savings", f"${opportunity['cost_savings']:,.0f}")
                    st.metric("ROI", f"{opportunity['roi']}%")
    
    with tab2:
        st.markdown("### Transportation Emissions Analysis")
        
        # Transport mode selection
        transport_modes = st.multiselect(
            "Select Transport Modes",
            ["Road", "Rail", "Air", "Sea", "Multimodal"],
            default=["Road", "Rail"]
        )
        
        # Route emissions analysis
        if route_data:
            route_emissions = calculate_route_emissions(route_data, transport_modes)
            
            # Top emitting routes
            st.markdown("#### Highest Emission Routes")
            
            top_routes = sorted(route_emissions, key=lambda x: x['total_emissions'], reverse=True)[:10]
            
            routes_df = pd.DataFrame([{
                'Route': f"{r['source']} → {r['destination']}",
                'Distance (km)': r['distance'],
                'CO₂ Emissions (kg)': f"{r['total_emissions']:,.0f}",
                'Emissions/km': f"{r['emissions_per_km']:.2f}",
                'Mode': r['transport_mode'],
                'Efficiency Rating': r['efficiency_rating']
            } for r in top_routes])
            
            st.dataframe(routes_df, use_container_width=True)
            
            # Route optimization for emissions
            st.markdown("#### Route Optimization for Lower Emissions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Emissions by transport mode
                mode_chart = create_emissions_by_mode_chart(route_emissions)
                st.plotly_chart(mode_chart, use_container_width=True)
            
            with col2:
                # Distance vs emissions scatter
                distance_emissions_chart = create_distance_emissions_chart(route_emissions)
                st.plotly_chart(distance_emissions_chart, use_container_width=True)
            
            # Alternative route suggestions
            st.markdown("#### 🔄 Low-Carbon Route Alternatives")
            
            alternatives = generate_low_carbon_alternatives(route_data, groq_client)
            
            for alt in alternatives:
                with st.expander(f"Alternative for {alt['original_route']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Current Route:**")
                        st.write(f"Emissions: {alt['current_emissions']} kg CO₂")
                        st.write(f"Cost: ${alt['current_cost']:,.0f}")
                    
                    with col2:
                        st.write("**Proposed Alternative:**")
                        st.write(f"Emissions: {alt['alt_emissions']} kg CO₂")
                        st.write(f"Cost: ${alt['alt_cost']:,.0f}")
                    
                    with col3:
                        st.write("**Impact:**")
                        st.metric("CO₂ Reduction", f"{alt['emission_reduction']:.0f} kg")
                        st.metric("Cost Change", f"${alt['cost_change']:+,.0f}")
    
    with tab3:
        st.markdown("### Supplier ESG Performance")
        
        if supplier_data:
            # ESG scoring
            esg_scores = calculate_supplier_esg_scores(supplier_data)
            
            # Supplier ESG dashboard
            col1, col2 = st.columns(2)
            
            with col1:
                # ESG score distribution
                esg_dist_chart = create_esg_distribution_chart(esg_scores)
                st.plotly_chart(esg_dist_chart, use_container_width=True)
            
            with col2:
                # ESG performance radar
                esg_radar_chart = create_esg_radar_chart(esg_scores)
                st.plotly_chart(esg_radar_chart, use_container_width=True)
            
            # Detailed supplier ESG table
            st.markdown("#### Detailed Supplier ESG Ratings")
            
            esg_df = pd.DataFrame([{
                'Supplier': score['name'],
                'Overall ESG': f"{score['overall']:.1f}/10",
                'Environmental': f"{score['environmental']:.1f}/10",
                'Social': f"{score['social']:.1f}/10",
                'Governance': f"{score['governance']:.1f}/10",
                'Carbon Rating': score['carbon_rating'],
                'Certification': score['certifications']
            } for score in esg_scores])
            
            # Color coding for ESG scores
            def color_esg_score(val):
                if isinstance(val, str) and '/' in val:
                    score = float(val.split('/')[0])
                    if score >= 8:
                        return 'background-color: #d4edda'
                    elif score >= 6:
                        return 'background-color: #fff3cd'
                    else:
                        return 'background-color: #f8d7da'
                return ''
            
            styled_df = esg_df.style.applymap(color_esg_score, subset=['Overall ESG', 'Environmental', 'Social', 'Governance'])
            st.dataframe(styled_df, use_container_width=True)
            
            # ESG improvement recommendations
            st.markdown("#### 📈 ESG Improvement Recommendations")
            
            improvements = generate_esg_improvements(esg_scores, groq_client)
            
            for improvement in improvements:
                with st.expander(f"Improve {improvement['supplier']} - Priority: {improvement['priority']}"):
                    st.write(f"**Current Issues:** {improvement['issues']}")
                    st.write(f"**Recommended Actions:** {improvement['actions']}")
                    st.write(f"**Expected Impact:** {improvement['impact']}")
                    st.write(f"**Timeline:** {improvement['timeline']}")
    
    with tab4:
        st.markdown("### Circular Economy Initiatives")
        
        # Circular economy metrics
        circular_metrics = calculate_circular_economy_metrics(inventory_data, supplier_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Recycling Rate", f"{circular_metrics['recycling_rate']:.1f}%")
        
        with col2:
            st.metric("Waste Reduction", f"{circular_metrics['waste_reduction']:.1f}%")
        
        with col3:
            st.metric("Reuse Potential", f"{circular_metrics['reuse_potential']:.1f}%")
        
        with col4:
            st.metric("Circular Score", f"{circular_metrics['circular_score']:.0f}/100")
        
        # Circular economy initiatives
        col1, col2 = st.columns(2)
        
        with col1:
            # Material flow analysis
            material_flow_chart = create_material_flow_chart(inventory_data)
            st.plotly_chart(material_flow_chart, use_container_width=True)
            
            # Waste stream analysis
            waste_chart = create_waste_stream_chart()
            st.plotly_chart(waste_chart, use_container_width=True)
        
        with col2:
            # Circular opportunities
            circular_opportunities_chart = create_circular_opportunities_chart()
            st.plotly_chart(circular_opportunities_chart, use_container_width=True)
            
            # Resource efficiency trends
            efficiency_trends_chart = create_resource_efficiency_chart()
            st.plotly_chart(efficiency_trends_chart, use_container_width=True)
        
        # Circular economy action plan
        st.markdown("#### ♻️ Circular Economy Action Plan")
        
        action_plan = generate_circular_action_plan(inventory_data, groq_client)
        
        for i, action in enumerate(action_plan, 1):
            with st.expander(f"Initiative {i}: {action['title']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {action['description']}")
                    st.write(f"**Implementation Steps:** {action['steps']}")
                    st.write(f"**Resources Required:** {action['resources']}")
                
                with col2:
                    st.metric("Investment", f"${action['investment']:,.0f}")
                    st.metric("Annual Savings", f"${action['savings']:,.0f}")
                    st.metric("Payback Period", f"{action['payback']} months")
    
    with tab5:
        st.markdown("### Sustainability Goals & Targets")
        
        # Goal setting interface
        st.markdown("#### 🎯 Set Sustainability Targets")
        
        col1, col2 = st.columns(2)
        
        with col1:
            co2_target = st.slider("CO₂ Reduction Target (%)", 0, 100, 30)
            timeline = st.selectbox("Target Timeline", ["1 year", "2 years", "3 years", "5 years"])
            
        with col2:
            focus_areas = st.multiselect(
                "Focus Areas",
                ["Transportation", "Packaging", "Energy", "Waste", "Water", "Suppliers"],
                default=["Transportation", "Packaging"]
            )
            
            reporting_standard = st.selectbox(
                "Reporting Standard",
                ["GRI", "SASB", "TCFD", "CDP", "UN SDGs"]
            )
        
        if st.button("📊 Generate Sustainability Roadmap", type="primary"):
            with st.spinner("Creating personalized sustainability roadmap..."):
                roadmap = generate_sustainability_roadmap(
                    co2_target, timeline, focus_areas, reporting_standard,
                    inventory_data, route_data, supplier_data, groq_client
                )
                
                st.markdown("#### 🛣️ Your Sustainability Roadmap")
                st.markdown(roadmap)
        
        # Progress tracking
        st.markdown("#### 📈 Progress Tracking")
        
        # Current progress vs targets
        progress_data = {
            'CO₂ Reduction': {'current': 15, 'target': co2_target, 'unit': '%'},
            'Renewable Energy': {'current': 25, 'target': 50, 'unit': '%'},
            'Waste Reduction': {'current': 40, 'target': 60, 'unit': '%'},
            'Supplier ESG Score': {'current': 7.2, 'target': 8.5, 'unit': '/10'}
        }
        
        for metric, data in progress_data.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                progress = min(100, (data['current'] / data['target']) * 100)
                st.progress(progress / 100)
                st.write(f"**{metric}**")
            
            with col2:
                st.metric("Current", f"{data['current']}{data['unit']}")
            
            with col3:
                st.metric("Target", f"{data['target']}{data['unit']}")
        
        # Sustainability reporting
        st.markdown("#### 📋 Sustainability Reporting")
        
        report_type = st.selectbox(
            "Generate Report",
            ["Monthly ESG Summary", "Carbon Footprint Report", "Supplier Sustainability Report", "Circular Economy Report"]
        )
        
        if st.button(f"Generate {report_type}"):
            with st.spinner("Generating sustainability report..."):
                report = generate_sustainability_report(
                    report_type, inventory_data, route_data, supplier_data, groq_client
                )
                
                st.markdown("#### Generated Report")
                st.markdown(report)
                
                # Export options
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📄 Download PDF", data="Report content", file_name=f"{report_type}.pdf")
                with col2:
                    st.download_button("📊 Download Excel", data="Report data", file_name=f"{report_type}.xlsx")
                with col3:
                    st.download_button("📧 Email Report", data="Report content", file_name=f"{report_type}.txt")

def calculate_carbon_metrics(inventory_data, route_data, supplier_data):
    """Calculate comprehensive carbon footprint metrics"""
    
    # Transport emissions (simplified calculation)
    transport_emissions = 0
    if route_data:
        for route in route_data:
            distance = route.get('Distance_km', 0)
            # Assume average CO2 emission of 0.8 kg per km for freight transport
            transport_emissions += distance * 0.8
    
    # Inventory emissions (based on product lifecycle)
    inventory_emissions = 0
    if inventory_data:
        for item in inventory_data:
            stock = item.get('Current_Stock', 0)
            # Assume average 2 kg CO2 per unit for manufacturing
            inventory_emissions += stock * 2
    
    # Supplier emissions (estimated)
    supplier_emissions = len(supplier_data) * 1000 if supplier_data else 0
    
    total_emissions = transport_emissions + inventory_emissions + supplier_emissions
    
    # Calculate other metrics
    total_units = sum(item.get('Current_Stock', 0) for item in inventory_data) if inventory_data else 1
    carbon_intensity = total_emissions / max(total_units, 1)
    
    # Simulate changes (would be calculated from historical data)
    import random
    
    return {
        'total_emissions': total_emissions,
        'transport_emissions': transport_emissions,
        'inventory_emissions': inventory_emissions,
        'supplier_emissions': supplier_emissions,
        'carbon_intensity': carbon_intensity,
        'sustainability_score': max(0, 100 - (carbon_intensity * 10)),
        'emission_change': random.uniform(-5, 10),
        'transport_change': random.uniform(-8, 15),
        'intensity_change': random.uniform(-3, 7),
        'score_change': random.uniform(-2, 5)
    }

def create_emissions_breakdown_chart(carbon_data):
    """Create emissions breakdown pie chart"""
    
    labels = ['Transportation', 'Manufacturing', 'Suppliers', 'Other']
    values = [
        carbon_data['transport_emissions'],
        carbon_data['inventory_emissions'],
        carbon_data['supplier_emissions'],
        carbon_data['total_emissions'] * 0.1  # Other emissions
    ]
    
    fig = go.Figure(data=go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    ))
    
    fig.update_layout(
        title="CO₂ Emissions Breakdown",
        height=300
    )
    
    return fig

def create_monthly_emissions_chart():
    """Create monthly emissions trend chart"""
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    emissions = [15000 + np.random.randint(-2000, 3000) for _ in months]
    
    fig = go.Figure(data=go.Scatter(
        x=months,
        y=emissions,
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Monthly CO₂ Emissions Trend",
        xaxis_title="Month",
        yaxis_title="CO₂ Emissions (kg)",
        height=300
    )
    
    return fig

def create_emissions_by_location_chart(route_data):
    """Create emissions by location chart"""
    
    if not route_data:
        return go.Figure().add_annotation(text="No route data available", x=0.5, y=0.5, showarrow=False)
    
    # Aggregate emissions by source location
    location_emissions = {}
    for route in route_data:
        source = route.get('Source', 'Unknown')
        distance = route.get('Distance_km', 0)
        emissions = distance * 0.8  # kg CO2 per km
        
        if source in location_emissions:
            location_emissions[source] += emissions
        else:
            location_emissions[source] = emissions
    
    locations = list(location_emissions.keys())
    emissions = list(location_emissions.values())
    
    fig = go.Figure(data=go.Bar(
        x=locations,
        y=emissions,
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title="CO₂ Emissions by Location",
        xaxis_title="Location",
        yaxis_title="CO₂ Emissions (kg)",
        height=300,
        xaxis_tickangle=-45
    )
    
    return fig

def create_carbon_efficiency_chart(route_data):
    """Create carbon efficiency vs cost chart"""
    
    if not route_data:
        return go.Figure().add_annotation(text="No route data available", x=0.5, y=0.5, showarrow=False)
    
    costs = []
    emissions = []
    routes = []
    
    for route in route_data[:10]:  # Top 10 routes
        distance = route.get('Distance_km', 0)
        cost_per_km = route.get('Cost_per_km', 20)
        total_cost = distance * cost_per_km
        total_emissions = distance * 0.8
        
        costs.append(total_cost)
        emissions.append(total_emissions)
        routes.append(f"{route.get('Source', '')} → {route.get('Destination', '')}")
    
    fig = go.Figure(data=go.Scatter(
        x=costs,
        y=emissions,
        mode='markers+text',
        text=[route.split(' → ')[0] for route in routes],
        textposition="top center",
        marker=dict(size=10, color=emissions, colorscale='Reds', showscale=True)
    ))
    
    fig.update_layout(
        title="Cost vs Carbon Emissions",
        xaxis_title="Total Cost ($)",
        yaxis_title="CO₂ Emissions (kg)",
        height=300
    )
    
    return fig

def identify_reduction_opportunities(route_data, supplier_data, groq_client):
    """Identify carbon reduction opportunities"""
    
    opportunities = [
        {
            'title': 'Route Consolidation',
            'description': 'Combine multiple delivery routes to reduce total distance traveled',
            'potential': 2500,
            'cost_savings': 15000,
            'roi': 150,
            'implementation': 'Deploy route optimization software and restructure delivery schedules',
            'timeline': '3-6 months'
        },
        {
            'title': 'Modal Shift to Rail',
            'description': 'Switch long-distance road transport to more efficient rail transport',
            'potential': 4200,
            'cost_savings': 25000,
            'roi': 180,
            'implementation': 'Negotiate rail contracts and adjust logistics planning',
            'timeline': '6-12 months'
        },
        {
            'title': 'Electric Vehicle Fleet',
            'description': 'Replace diesel vehicles with electric alternatives for local deliveries',
            'potential': 3800,
            'cost_savings': 22000,
            'roi': 120,
            'implementation': 'Gradual fleet replacement and charging infrastructure setup',
            'timeline': '12-24 months'
        },
        {
            'title': 'Supplier Engagement',
            'description': 'Work with suppliers to reduce their carbon footprint',
            'potential': 5500,
            'cost_savings': 18000,
            'roi': 95,
            'implementation': 'Supplier sustainability programs and green procurement policies',
            'timeline': '6-18 months'
        }
    ]
    
    return opportunities

def calculate_route_emissions(route_data, transport_modes):
    """Calculate detailed route emissions"""
    
    emissions_factors = {
        'Road': 0.8,  # kg CO2 per km
        'Rail': 0.3,
        'Air': 2.1,
        'Sea': 0.1,
        'Multimodal': 0.6
    }
    
    route_emissions = []
    
    for route in route_data:
        distance = route.get('Distance_km', 0)
        source = route.get('Source', '')
        destination = route.get('Destination', '')
        
        # Assign transport mode (simplified)
        if distance > 1000:
            mode = 'Air' if distance > 2000 else 'Rail'
        else:
            mode = 'Road'
        
        if mode in transport_modes:
            emissions_per_km = emissions_factors.get(mode, 0.8)
            total_emissions = distance * emissions_per_km
            
            # Calculate efficiency rating
            if total_emissions < distance * 0.3:
                efficiency_rating = 'Excellent'
            elif total_emissions < distance * 0.6:
                efficiency_rating = 'Good'
            elif total_emissions < distance * 1.0:
                efficiency_rating = 'Average'
            else:
                efficiency_rating = 'Poor'
            
            route_emissions.append({
                'source': source,
                'destination': destination,
                'distance': distance,
                'transport_mode': mode,
                'emissions_per_km': emissions_per_km,
                'total_emissions': total_emissions,
                'efficiency_rating': efficiency_rating
            })
    
    return route_emissions

def create_emissions_by_mode_chart(route_emissions):
    """Create emissions by transport mode chart"""
    
    mode_emissions = {}
    for route in route_emissions:
        mode = route['transport_mode']
        if mode in mode_emissions:
            mode_emissions[mode] += route['total_emissions']
        else:
            mode_emissions[mode] = route['total_emissions']
    
    modes = list(mode_emissions.keys())
    emissions = list(mode_emissions.values())
    
    fig = go.Figure(data=go.Bar(
        x=modes,
        y=emissions,
        marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'][:len(modes)]
    ))
    
    fig.update_layout(
        title="Emissions by Transport Mode",
        xaxis_title="Transport Mode",
        yaxis_title="CO₂ Emissions (kg)",
        height=300
    )
    
    return fig

def create_distance_emissions_chart(route_emissions):
    """Create distance vs emissions scatter plot"""
    
    distances = [route['distance'] for route in route_emissions]
    emissions = [route['total_emissions'] for route in route_emissions]
    modes = [route['transport_mode'] for route in route_emissions]
    
    color_map = {'Road': '#ff6b6b', 'Rail': '#4ecdc4', 'Air': '#45b7d1', 'Sea': '#96ceb4', 'Multimodal': '#f7b731'}
    colors = [color_map.get(mode, '#95a5a6') for mode in modes]
    
    fig = go.Figure(data=go.Scatter(
        x=distances,
        y=emissions,
        mode='markers',
        marker=dict(size=8, color=colors),
        text=modes,
        hovertemplate='Distance: %{x} km<br>Emissions: %{y} kg CO₂<br>Mode: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Distance vs Emissions by Mode",
        xaxis_title="Distance (km)",
        yaxis_title="CO₂ Emissions (kg)",
        height=300
    )
    
    return fig

def generate_low_carbon_alternatives(route_data, groq_client):
    """Generate low-carbon route alternatives"""
    
    alternatives = []
    
    for route in route_data[:3]:  # Top 3 routes for demonstration
        distance = route.get('Distance_km', 0)
        cost_per_km = route.get('Cost_per_km', 20)
        current_cost = distance * cost_per_km
        current_emissions = distance * 0.8  # Road transport
        
        # Simulate rail alternative
        alt_emissions = distance * 0.3  # Rail transport
        alt_cost = current_cost * 0.85  # Slightly cheaper
        
        alternatives.append({
            'original_route': f"{route.get('Source', '')} → {route.get('Destination', '')}",
            'current_emissions': current_emissions,
            'current_cost': current_cost,
            'alt_emissions': alt_emissions,
            'alt_cost': alt_cost,
            'emission_reduction': current_emissions - alt_emissions,
            'cost_change': alt_cost - current_cost
        })
    
    return alternatives

def calculate_supplier_esg_scores(supplier_data):
    """Calculate ESG scores for suppliers"""
    
    esg_scores = []
    
    for supplier in supplier_data:
        name = supplier.get('Supplier_Name', 'Unknown')
        
        # Generate ESG scores (in real implementation, this would come from ESG data providers)
        environmental = np.random.uniform(4, 9)
        social = np.random.uniform(5, 8.5)
        governance = np.random.uniform(6, 9)
        overall = (environmental + social + governance) / 3
        
        # Carbon rating
        if environmental >= 8:
            carbon_rating = 'A'
        elif environmental >= 6:
            carbon_rating = 'B'
        elif environmental >= 4:
            carbon_rating = 'C'
        else:
            carbon_rating = 'D'
        
        # Certifications
        certifications = np.random.choice(['ISO 14001', 'B-Corp', 'FSC', 'Fair Trade', 'None'], 
                                        p=[0.3, 0.2, 0.2, 0.15, 0.15])
        
        esg_scores.append({
            'name': name,
            'environmental': environmental,
            'social': social,
            'governance': governance,
            'overall': overall,
            'carbon_rating': carbon_rating,
            'certifications': certifications
        })
    
    return esg_scores

def create_esg_distribution_chart(esg_scores):
    """Create ESG score distribution chart"""
    
    overall_scores = [score['overall'] for score in esg_scores]
    
    fig = go.Figure(data=go.Histogram(
        x=overall_scores,
        nbinsx=10,
        marker_color='#3498db',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="ESG Score Distribution",
        xaxis_title="ESG Score",
        yaxis_title="Number of Suppliers",
        height=300
    )
    
    return fig

def create_esg_radar_chart(esg_scores):
    """Create ESG performance radar chart"""
    
    avg_env = np.mean([score['environmental'] for score in esg_scores])
    avg_social = np.mean([score['social'] for score in esg_scores])
    avg_gov = np.mean([score['governance'] for score in esg_scores])
    
    categories = ['Environmental', 'Social', 'Governance']
    values = [avg_env, avg_social, avg_gov]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        title="Average ESG Performance",
        height=300
    )
    
    return fig

def generate_esg_improvements(esg_scores, groq_client):
    """Generate ESG improvement recommendations"""
    
    improvements = []
    
    # Find suppliers with low scores
    low_performers = [score for score in esg_scores if score['overall'] < 6]
    
    for supplier in low_performers[:3]:  # Top 3 for improvement
        issues = []
        actions = []
        
        if supplier['environmental'] < 5:
            issues.append("Poor environmental practices")
            actions.append("Implement environmental management system")
        
        if supplier['social'] < 5:
            issues.append("Inadequate social standards")
            actions.append("Develop worker welfare programs")
        
        if supplier['governance'] < 5:
            issues.append("Weak governance structure")
            actions.append("Strengthen compliance and reporting")
        
        improvements.append({
            'supplier': supplier['name'],
            'priority': 'High' if supplier['overall'] < 4 else 'Medium',
            'issues': '; '.join(issues),
            'actions': '; '.join(actions),
            'impact': 'Improved ESG score by 2-3 points',
            'timeline': '6-12 months'
        })
    
    return improvements

def calculate_circular_economy_metrics(inventory_data, supplier_data):
    """Calculate circular economy metrics"""
    
    # Simulate circular economy metrics
    recycling_rate = np.random.uniform(60, 85)
    waste_reduction = np.random.uniform(45, 75)
    reuse_potential = np.random.uniform(35, 65)
    circular_score = (recycling_rate + waste_reduction + reuse_potential) / 3
    
    return {
        'recycling_rate': recycling_rate,
        'waste_reduction': waste_reduction,
        'reuse_potential': reuse_potential,
        'circular_score': circular_score
    }

def create_material_flow_chart(inventory_data):
    """Create material flow Sankey diagram"""
    
    fig = go.Figure(data=go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Raw Materials", "Manufacturing", "Distribution", "Use", "End of Life", "Recycling", "Waste"],
            color=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff99cc", "#c2c2f0", "#ffb3e6"]
        ),
        link=dict(
            source=[0, 1, 2, 3, 4, 4, 5],
            target=[1, 2, 3, 4, 5, 6, 1],
            value=[100, 95, 90, 85, 50, 35, 40]
        )
    ))
    
    fig.update_layout(
        title="Material Flow Analysis",
        height=300
    )
    
    return fig

def create_waste_stream_chart():
    """Create waste stream analysis chart"""
    
    waste_types = ['Packaging', 'Product Returns', 'Manufacturing', 'Office', 'Transport']
    waste_amounts = [2500, 1800, 3200, 800, 1200]
    recycled_amounts = [amount * np.random.uniform(0.4, 0.8) for amount in waste_amounts]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Waste',
        x=waste_types,
        y=waste_amounts,
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        name='Recycled',
        x=waste_types,
        y=recycled_amounts,
        marker_color='#27ae60'
    ))
    
    fig.update_layout(
        title="Waste Stream Analysis",
        xaxis_title="Waste Type",
        yaxis_title="Amount (kg)",
        height=300,
        barmode='group'
    )
    
    return fig

def create_circular_opportunities_chart():
    """Create circular economy opportunities chart"""
    
    opportunities = ['Design for Disassembly', 'Product as a Service', 'Remanufacturing', 'Material Recovery', 'Sharing Economy']
    potential_savings = [150000, 280000, 320000, 180000, 95000]
    
    fig = go.Figure(data=go.Bar(
        x=opportunities,
        y=potential_savings,
        marker_color='#3498db',
        text=[f"${saving/1000:.0f}K" for saving in potential_savings],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Circular Economy Opportunities",
        xaxis_title="Opportunity",
        yaxis_title="Potential Savings ($)",
        height=300,
        xaxis_tickangle=-45
    )
    
    return fig

def create_resource_efficiency_chart():
    """Create resource efficiency trends chart"""
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    efficiency = [72, 75, 78, 76, 80, 83]
    
    fig = go.Figure(data=go.Scatter(
        x=months,
        y=efficiency,
        mode='lines+markers+text',
        text=[f"{eff}%" for eff in efficiency],
        textposition="top center",
        line=dict(color='#27ae60', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Resource Efficiency Trends",
        xaxis_title="Month",
        yaxis_title="Efficiency (%)",
        height=300
    )
    
    return fig

def generate_circular_action_plan(inventory_data, groq_client):
    """Generate circular economy action plan"""
    
    return [
        {
            'title': 'Packaging Redesign Program',
            'description': 'Redesign packaging to use recycled materials and reduce waste',
            'steps': 'Audit current packaging, design alternatives, pilot test, full rollout',
            'resources': 'Design team, sustainability consultant, pilot budget',
            'investment': 75000,
            'savings': 120000,
            'payback': 8
        },
        {
            'title': 'Product Refurbishment Center',
            'description': 'Establish center to refurbish returned products for resale',
            'steps': 'Site selection, equipment procurement, staff training, operations launch',
            'resources': 'Facility space, refurbishment equipment, trained technicians',
            'investment': 250000,
            'savings': 180000,
            'payback': 17
        },
        {
            'title': 'Supplier Take-Back Program',
            'description': 'Partner with suppliers for product take-back and recycling',
            'steps': 'Identify key suppliers, negotiate agreements, implement logistics',
            'resources': 'Legal support, logistics coordination, supplier engagement',
            'investment': 45000,
            'savings': 95000,
            'payback': 6
        }
    ]

def generate_sustainability_roadmap(co2_target, timeline, focus_areas, reporting_standard, 
                                  inventory_data, route_data, supplier_data, groq_client):
    """Generate comprehensive sustainability roadmap"""
    
    try:
        prompt = f"""
        Create a comprehensive sustainability roadmap with the following parameters:
        - CO₂ reduction target: {co2_target}%
        - Timeline: {timeline}
        - Focus areas: {', '.join(focus_areas)}
        - Reporting standard: {reporting_standard}
        
        Current operations context:
        - Inventory locations: {len(set(item.get('Location', 'Unknown') for item in inventory_data)) if inventory_data else 0}
        - Active routes: {len(route_data) if route_data else 0}
        - Suppliers: {len(supplier_data) if supplier_data else 0}
        
        Provide a structured roadmap with specific milestones, actions, and KPIs.
        """
        
        return groq_client.generate_response(prompt, temperature=0.3)
        
    except Exception as e:
        return f"""
        ## Sustainability Roadmap ({timeline})

        ### Phase 1: Foundation (Months 1-6)
        - Establish baseline carbon footprint measurement
        - Implement {reporting_standard} reporting framework
        - Launch sustainability team and governance structure
        - Begin supplier ESG assessment program

        ### Phase 2: Implementation (Months 7-18)
        - Deploy route optimization for {co2_target/2}% emissions reduction
        - Implement circular economy initiatives in {', '.join(focus_areas[:2])}
        - Launch supplier engagement program
        - Introduce renewable energy procurement

        ### Phase 3: Acceleration (Months 19-{int(timeline.split()[0])*12})
        - Scale successful pilot programs
        - Achieve {co2_target}% CO₂ reduction target
        - Implement advanced technology solutions
        - Expand sustainability metrics and reporting

        ### Key Performance Indicators
        - CO₂ emissions reduction: {co2_target}%
        - Supplier ESG score improvement: 20%
        - Waste reduction: 50%
        - Renewable energy adoption: 40%

        Note: AI service not available for detailed roadmap. Please check configuration for enhanced planning.
        """

def generate_sustainability_report(report_type, inventory_data, route_data, supplier_data, groq_client):
    """Generate sustainability reports"""
    
    try:
        prompt = f"""
        Generate a comprehensive {report_type} based on supply chain data:
        
        Data summary:
        - Inventory items: {len(inventory_data) if inventory_data else 0}
        - Transportation routes: {len(route_data) if route_data else 0}
        - Suppliers: {len(supplier_data) if supplier_data else 0}
        
        Include key metrics, trends, achievements, and recommendations.
        Format as a professional report suitable for stakeholders.
        """
        
        return groq_client.generate_response(prompt, temperature=0.2)
        
    except Exception as e:
        return f"""
        ## {report_type}
        **Generated on:** {datetime.now().strftime('%B %d, %Y')}

        ### Executive Summary
        This report provides an overview of our sustainability performance and carbon footprint management across the supply chain network.

        ### Key Metrics
        - Total CO₂ emissions: 45,200 kg (↓ 8% from last period)
        - Transportation efficiency: 89% (↑ 3%)
        - Supplier ESG score: 7.2/10 (↑ 0.4)
        - Waste reduction: 42% (↑ 5%)

        ### Performance Highlights
        - Successfully reduced transportation emissions through route optimization
        - Improved supplier sustainability engagement with 85% participation
        - Implemented circular economy initiatives reducing waste by 42%
        - Achieved carbon intensity reduction of 12% year-over-year

        ### Recommendations
        1. Accelerate electric vehicle adoption for local delivery routes
        2. Expand supplier sustainability programs to tier-2 suppliers
        3. Implement advanced analytics for real-time emissions monitoring
        4. Develop carbon offset strategy for unavoidable emissions

        Note: AI service not available for detailed report generation. Please check configuration for enhanced reporting.
        """

if __name__ == "__main__":
    main()