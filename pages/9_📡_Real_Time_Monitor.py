import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
from utils.data_handler import DataHandler
from utils.groq_client import GroqClient
import random

def main():
    st.title("📡 Real-Time Supply Chain Monitor")
    st.markdown("Live monitoring and alerting system for critical supply chain operations")
    
    # Initialize components
    data_handler = DataHandler()
    groq_client = GroqClient()
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_refresh = st.toggle("🔄 Auto Refresh", value=True)
    with col2:
        refresh_interval = st.selectbox("Refresh Rate", ["5s", "10s", "30s", "1m"], index=1)
    with col3:
        if st.button("🔄 Manual Refresh"):
            st.rerun()
    
    # Auto-refresh functionality
    if auto_refresh:
        interval_map = {"5s": 5, "10s": 10, "30s": 30, "1m": 60}
        time.sleep(interval_map[refresh_interval])
        st.rerun()
    
    # Load data
    forecast_data = data_handler.get_forecast_data()
    inventory_data = data_handler.get_inventory_data()
    route_data = data_handler.get_route_data()
    supplier_data = data_handler.get_supplier_data()
    
    if not any([forecast_data, inventory_data, route_data, supplier_data]):
        st.warning("Please upload data to enable real-time monitoring.")
        if st.button("Load Sample Data"):
            data_handler.load_sample_data()
            st.rerun()
        return
    
    # Generate real-time metrics (simulated)
    current_time = datetime.now()
    
    # Main monitoring dashboard
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Live Dashboard", 
        "⚠️ Alert Center", 
        "📊 Performance Metrics",
        "🚨 Incident Response"
    ])
    
    with tab1:
        st.markdown("### Live Operations Dashboard")
        st.caption(f"Last updated: {current_time.strftime('%H:%M:%S')}")
        
        # Key Performance Indicators
        create_live_kpi_dashboard(inventory_data, route_data, supplier_data)
        
        # Real-time charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Live inventory levels
            st.markdown("#### 📦 Inventory Levels (Live)")
            inventory_chart = create_live_inventory_chart(inventory_data)
            st.plotly_chart(inventory_chart, use_container_width=True)
            
            # Route performance
            st.markdown("#### 🚛 Route Performance")
            route_chart = create_live_route_chart(route_data)
            st.plotly_chart(route_chart, use_container_width=True)
        
        with col2:
            # System health
            st.markdown("#### 💚 System Health")
            health_chart = create_system_health_chart()
            st.plotly_chart(health_chart, use_container_width=True)
            
            # Supplier status
            st.markdown("#### 🏭 Supplier Status")
            supplier_chart = create_live_supplier_chart(supplier_data)
            st.plotly_chart(supplier_chart, use_container_width=True)
        
        # Live activity feed
        st.markdown("#### 📰 Live Activity Feed")
        activity_feed = generate_activity_feed(inventory_data, route_data, supplier_data)
        
        feed_container = st.container()
        with feed_container:
            for activity in activity_feed[:10]:  # Show latest 10 activities
                timestamp = current_time - timedelta(minutes=random.randint(1, 60))
                
                if activity['type'] == 'warning':
                    st.warning(f"🟡 {timestamp.strftime('%H:%M')} - {activity['message']}")
                elif activity['type'] == 'success':
                    st.success(f"🟢 {timestamp.strftime('%H:%M')} - {activity['message']}")
                elif activity['type'] == 'error':
                    st.error(f"🔴 {timestamp.strftime('%H:%M')} - {activity['message']}")
                else:
                    st.info(f"🔵 {timestamp.strftime('%H:%M')} - {activity['message']}")
    
    with tab2:
        st.markdown("### Alert Management Center")
        
        # Alert severity filter
        severity_filter = st.multiselect(
            "Filter by Severity", 
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"]
        )
        
        # Generate alerts based on data
        alerts = generate_smart_alerts(inventory_data, route_data, supplier_data, forecast_data)
        
        # Filter alerts by severity
        filtered_alerts = [alert for alert in alerts if alert['severity'] in severity_filter]
        
        if filtered_alerts:
            st.markdown(f"#### Active Alerts ({len(filtered_alerts)})")
            
            for alert in filtered_alerts:
                with st.expander(f"{get_severity_icon(alert['severity'])} {alert['title']}", expanded=alert['severity'] == 'Critical'):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Description:** {alert['description']}")
                        st.write(f"**Impact:** {alert['impact']}")
                        st.write(f"**Recommendation:** {alert['recommendation']}")
                    
                    with col2:
                        st.metric("Severity", alert['severity'])
                        st.metric("Priority", alert['priority'])
                    
                    with col3:
                        if st.button(f"Resolve", key=f"resolve_{alert['id']}"):
                            st.success("Alert marked as resolved!")
                        if st.button(f"Escalate", key=f"escalate_{alert['id']}"):
                            st.warning("Alert escalated to management!")
        else:
            st.success("🎉 No active alerts matching your criteria!")
        
        # Alert statistics
        st.markdown("#### Alert Statistics")
        alert_stats = analyze_alert_patterns(alerts)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Alerts", len(alerts))
        with col2:
            critical_count = len([a for a in alerts if a['severity'] == 'Critical'])
            st.metric("Critical", critical_count, delta=random.randint(-2, 2))
        with col3:
            high_count = len([a for a in alerts if a['severity'] == 'High'])
            st.metric("High Priority", high_count, delta=random.randint(-1, 3))
        with col4:
            avg_resolution_time = "12 min"
            st.metric("Avg Resolution", avg_resolution_time)
    
    with tab3:
        st.markdown("### Performance Metrics Dashboard")
        
        # Performance timeframe
        timeframe = st.selectbox("Performance Period", ["Last Hour", "Last 4 Hours", "Last 24 Hours", "Last Week"])
        
        # Generate performance data
        perf_data = generate_performance_metrics(inventory_data, route_data, supplier_data, timeframe)
        
        # Performance overview
        st.markdown("#### Overall Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("System Uptime", "99.8%", delta="0.2%")
        with col2:
            st.metric("Order Accuracy", "97.3%", delta="1.1%")
        with col3:
            st.metric("Delivery Performance", "94.7%", delta="-0.8%")
        with col4:
            st.metric("Cost Efficiency", "89.2%", delta="2.4%")
        
        # Detailed performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Throughput trends
            throughput_chart = create_throughput_chart(timeframe)
            st.plotly_chart(throughput_chart, use_container_width=True)
            
            # Error rate trends
            error_chart = create_error_rate_chart(timeframe)
            st.plotly_chart(error_chart, use_container_width=True)
        
        with col2:
            # Response time distribution
            response_chart = create_response_time_chart(timeframe)
            st.plotly_chart(response_chart, use_container_width=True)
            
            # Resource utilization
            resource_chart = create_resource_utilization_chart()
            st.plotly_chart(resource_chart, use_container_width=True)
    
    with tab4:
        st.markdown("### Incident Response System")
        
        # Incident creation
        st.markdown("#### Report New Incident")
        
        col1, col2 = st.columns(2)
        with col1:
            incident_type = st.selectbox(
                "Incident Type", 
                ["Supply Disruption", "Quality Issue", "Transportation Delay", 
                 "System Outage", "Demand Spike", "Supplier Issue"]
            )
            
            severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
            
        with col2:
            affected_area = st.multiselect(
                "Affected Areas", 
                ["Inventory", "Transportation", "Suppliers", "Customers", "Systems"]
            )
            
            priority = st.selectbox("Priority", ["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"])
        
        description = st.text_area("Incident Description", height=100)
        
        if st.button("🚨 Create Incident", type="primary"):
            if description:
                # Simulate incident creation
                incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                
                st.success(f"Incident {incident_id} created successfully!")
                
                # Generate AI-powered response plan
                with st.spinner("Generating AI response plan..."):
                    response_plan = generate_incident_response_plan(
                        incident_type, severity, affected_area, description, groq_client
                    )
                    
                    st.markdown("#### AI-Generated Response Plan")
                    st.markdown(response_plan)
            else:
                st.error("Please provide an incident description.")
        
        # Active incidents
        st.markdown("#### Active Incidents")
        
        # Simulate active incidents
        active_incidents = generate_sample_incidents()
        
        for incident in active_incidents:
            with st.expander(f"{incident['id']} - {incident['title']} ({incident['status']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Type:** {incident['type']}")
                    st.write(f"**Severity:** {incident['severity']}")
                    st.write(f"**Created:** {incident['created']}")
                
                with col2:
                    st.write(f"**Assigned:** {incident['assigned']}")
                    st.write(f"**Status:** {incident['status']}")
                    st.write(f"**Priority:** {incident['priority']}")
                
                with col3:
                    new_status = st.selectbox(
                        "Update Status", 
                        ["Open", "In Progress", "Resolved", "Closed"],
                        index=["Open", "In Progress", "Resolved", "Closed"].index(incident['status']),
                        key=f"status_{incident['id']}"
                    )
                    
                    if st.button("Update", key=f"update_{incident['id']}"):
                        st.success(f"Incident {incident['id']} status updated to {new_status}")

def create_live_kpi_dashboard(inventory_data, route_data, supplier_data):
    """Create live KPI dashboard"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if inventory_data:
            total_items = sum(item.get('Current_Stock', 0) for item in inventory_data)
            st.metric("Total Inventory", f"{total_items:,.0f}", delta=random.randint(-50, 100))
        else:
            st.metric("Total Inventory", "N/A")
    
    with col2:
        if route_data:
            active_routes = len(route_data)
            st.metric("Active Routes", active_routes, delta=random.randint(-2, 5))
        else:
            st.metric("Active Routes", "N/A")
    
    with col3:
        if supplier_data:
            active_suppliers = len(supplier_data)
            st.metric("Active Suppliers", active_suppliers, delta=random.randint(-1, 2))
        else:
            st.metric("Active Suppliers", "N/A")
    
    with col4:
        # Simulated real-time metrics
        order_rate = random.randint(45, 65)
        st.metric("Orders/Hour", order_rate, delta=random.randint(-5, 10))
    
    with col5:
        system_health = random.randint(95, 100)
        st.metric("System Health", f"{system_health}%", delta=f"{random.randint(-1, 2)}%")

def create_live_inventory_chart(inventory_data):
    """Create live inventory monitoring chart"""
    
    if not inventory_data:
        return go.Figure().add_annotation(text="No inventory data available", 
                                        x=0.5, y=0.5, showarrow=False)
    
    # Take top 10 items for visualization
    top_items = sorted(inventory_data, key=lambda x: x.get('Current_Stock', 0), reverse=True)[:10]
    
    products = [item['Product_Name'] for item in top_items]
    current_stock = [item.get('Current_Stock', 0) for item in top_items]
    reorder_points = [item.get('Reorder_Point', 0) for item in top_items]
    
    fig = go.Figure()
    
    # Current stock bars
    fig.add_trace(go.Bar(
        name='Current Stock',
        x=products,
        y=current_stock,
        marker_color='lightblue'
    ))
    
    # Reorder point line
    fig.add_trace(go.Scatter(
        name='Reorder Point',
        x=products,
        y=reorder_points,
        mode='markers+lines',
        marker_color='red',
        line=dict(dash='dash')
    ))
    
    fig.update_layout(
        title="Live Inventory Levels",
        xaxis_title="Products",
        yaxis_title="Units",
        height=300,
        showlegend=True
    )
    
    return fig

def create_live_route_chart(route_data):
    """Create live route performance chart"""
    
    if not route_data:
        return go.Figure().add_annotation(text="No route data available", 
                                        x=0.5, y=0.5, showarrow=False)
    
    # Calculate route efficiency metrics
    routes = []
    efficiency_scores = []
    
    for route in route_data[:8]:  # Top 8 routes
        route_name = f"{route['Source']} → {route['Destination']}"
        
        # Simulate efficiency score based on distance and cost
        distance = route.get('Distance_km', 100)
        cost_per_km = route.get('Cost_per_km', 20)
        base_efficiency = max(0, 100 - (cost_per_km - 15) * 3)
        
        # Add some real-time variation
        efficiency = base_efficiency + random.randint(-10, 10)
        efficiency = max(0, min(100, efficiency))
        
        routes.append(route_name)
        efficiency_scores.append(efficiency)
    
    # Color code based on efficiency
    colors = ['green' if score >= 80 else 'orange' if score >= 60 else 'red' 
              for score in efficiency_scores]
    
    fig = go.Figure(data=go.Bar(
        x=routes,
        y=efficiency_scores,
        marker_color=colors,
        text=[f"{score}%" for score in efficiency_scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Route Efficiency Scores",
        xaxis_title="Routes",
        yaxis_title="Efficiency %",
        height=300,
        xaxis_tickangle=-45
    )
    
    return fig

def create_system_health_chart():
    """Create system health monitoring chart"""
    
    # Simulate system components
    components = ['Database', 'API Gateway', 'Web Server', 'Cache', 'Queue', 'Storage']
    health_scores = [random.randint(85, 100) for _ in components]
    
    # Color coding
    colors = ['green' if score >= 95 else 'orange' if score >= 85 else 'red' 
              for score in health_scores]
    
    fig = go.Figure(data=go.Bar(
        x=components,
        y=health_scores,
        marker_color=colors,
        text=[f"{score}%" for score in health_scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="System Component Health",
        xaxis_title="Components",
        yaxis_title="Health %",
        height=300
    )
    
    return fig

def create_live_supplier_chart(supplier_data):
    """Create live supplier performance chart"""
    
    if not supplier_data:
        return go.Figure().add_annotation(text="No supplier data available", 
                                        x=0.5, y=0.5, showarrow=False)
    
    suppliers = [s['Supplier_Name'] for s in supplier_data[:6]]
    performance_scores = []
    
    for supplier in supplier_data[:6]:
        # Calculate performance based on delivery and quality
        delivery_perf = supplier.get('Delivery_Performance', 0.8) * 100
        quality_rating = supplier.get('Quality_Rating', 3) * 20
        
        # Weighted performance score
        performance = (delivery_perf * 0.6 + quality_rating * 0.4) + random.randint(-5, 5)
        performance = max(0, min(100, performance))
        performance_scores.append(performance)
    
    fig = go.Figure(data=go.Scatter(
        x=suppliers,
        y=performance_scores,
        mode='markers+lines',
        marker=dict(size=12, color=performance_scores, colorscale='RdYlGn', showscale=True),
        line=dict(width=2)
    ))
    
    fig.update_layout(
        title="Supplier Performance Trends",
        xaxis_title="Suppliers",
        yaxis_title="Performance Score",
        height=300
    )
    
    return fig

def generate_activity_feed(inventory_data, route_data, supplier_data):
    """Generate live activity feed"""
    
    activities = []
    
    # Inventory activities
    if inventory_data:
        for item in random.sample(inventory_data, min(3, len(inventory_data))):
            if random.random() < 0.3:  # 30% chance of low stock
                activities.append({
                    'type': 'warning',
                    'message': f"Low stock alert: {item['Product_Name']} ({item.get('Current_Stock', 0)} units remaining)"
                })
            elif random.random() < 0.2:  # 20% chance of restock
                activities.append({
                    'type': 'success',
                    'message': f"Inventory restocked: {item['Product_Name']} (+{random.randint(100, 500)} units)"
                })
    
    # Route activities
    if route_data:
        for route in random.sample(route_data, min(2, len(route_data))):
            if random.random() < 0.4:  # 40% chance of route update
                activities.append({
                    'type': 'info',
                    'message': f"Route completed: {route['Source']} → {route['Destination']} (On time)"
                })
            elif random.random() < 0.1:  # 10% chance of delay
                activities.append({
                    'type': 'warning',
                    'message': f"Route delay: {route['Source']} → {route['Destination']} (+{random.randint(15, 60)} min)"
                })
    
    # System activities
    system_activities = [
        {'type': 'success', 'message': 'Data synchronization completed successfully'},
        {'type': 'info', 'message': 'Scheduled backup initiated'},
        {'type': 'info', 'message': 'Performance optimization routine completed'},
        {'type': 'success', 'message': 'Alert resolution: Critical inventory alert cleared'}
    ]
    
    activities.extend(random.sample(system_activities, 2))
    
    return activities

def generate_smart_alerts(inventory_data, route_data, supplier_data, forecast_data):
    """Generate intelligent alerts based on data analysis"""
    
    alerts = []
    
    # Inventory-based alerts
    if inventory_data:
        for item in inventory_data:
            current_stock = item.get('Current_Stock', 0)
            reorder_point = item.get('Reorder_Point', 0)
            
            if current_stock <= reorder_point:
                alerts.append({
                    'id': f"INV-{random.randint(1000, 9999)}",
                    'title': f"Low Stock: {item['Product_Name']}",
                    'description': f"Current stock ({current_stock}) is at or below reorder point ({reorder_point})",
                    'severity': 'High' if current_stock < reorder_point * 0.5 else 'Medium',
                    'priority': 'P2' if current_stock < reorder_point * 0.5 else 'P3',
                    'impact': 'Potential stockout risk affecting customer orders',
                    'recommendation': 'Initiate emergency procurement or redistribute from other locations'
                })
    
    # Route-based alerts
    if route_data:
        for route in route_data:
            cost_per_km = route.get('Cost_per_km', 0)
            distance = route.get('Distance_km', 0)
            total_cost = cost_per_km * distance
            
            if total_cost > 25000:  # High cost route
                alerts.append({
                    'id': f"ROUTE-{random.randint(1000, 9999)}",
                    'title': f"High Cost Route: {route['Source']} → {route['Destination']}",
                    'description': f"Route cost (${total_cost:,.0f}) exceeds threshold",
                    'severity': 'Medium',
                    'priority': 'P3',
                    'impact': 'Increased operational costs affecting profit margins',
                    'recommendation': 'Review route optimization or consider alternative transportation modes'
                })
    
    # Supplier-based alerts
    if supplier_data:
        for supplier in supplier_data:
            delivery_perf = supplier.get('Delivery_Performance', 1.0)
            quality_rating = supplier.get('Quality_Rating', 5)
            
            if delivery_perf < 0.85:  # Poor delivery performance
                alerts.append({
                    'id': f"SUP-{random.randint(1000, 9999)}",
                    'title': f"Poor Delivery Performance: {supplier['Supplier_Name']}",
                    'description': f"Delivery performance ({delivery_perf:.1%}) below acceptable threshold",
                    'severity': 'High' if delivery_perf < 0.7 else 'Medium',
                    'priority': 'P2' if delivery_perf < 0.7 else 'P3',
                    'impact': 'Potential delays in production and customer deliveries',
                    'recommendation': 'Engage with supplier for improvement plan or seek alternative sources'
                })
    
    # Add some system alerts
    if random.random() < 0.3:  # 30% chance of system alert
        alerts.append({
            'id': f"SYS-{random.randint(1000, 9999)}",
            'title': "High System Load Detected",
            'description': "API response times exceeding normal thresholds",
            'severity': 'Medium',
            'priority': 'P3',
            'impact': 'Potential slowdown in data processing and user experience',
            'recommendation': 'Monitor system resources and consider scaling if pattern continues'
        })
    
    return alerts

def get_severity_icon(severity):
    """Get icon for alert severity"""
    icons = {
        'Critical': '🔴',
        'High': '🟠',
        'Medium': '🟡',
        'Low': '🟢'
    }
    return icons.get(severity, '🔵')

def analyze_alert_patterns(alerts):
    """Analyze alert patterns for insights"""
    return {
        'total': len(alerts),
        'by_severity': {severity: len([a for a in alerts if a['severity'] == severity]) 
                       for severity in ['Critical', 'High', 'Medium', 'Low']},
        'trend': 'increasing'  # Simplified
    }

def generate_performance_metrics(inventory_data, route_data, supplier_data, timeframe):
    """Generate performance metrics for specified timeframe"""
    return {
        'uptime': random.uniform(98.5, 99.9),
        'throughput': random.randint(1000, 5000),
        'error_rate': random.uniform(0.1, 2.0),
        'response_time': random.uniform(100, 500)
    }

def create_throughput_chart(timeframe):
    """Create throughput monitoring chart"""
    hours = list(range(24))
    throughput = [random.randint(50, 200) + 50 * np.sin(h/4) for h in hours]
    
    fig = go.Figure(data=go.Scatter(
        x=hours,
        y=throughput,
        mode='lines+markers',
        line=dict(color='blue', width=2),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title="Throughput Trends",
        xaxis_title="Hour",
        yaxis_title="Orders/Hour",
        height=300
    )
    
    return fig

def create_error_rate_chart(timeframe):
    """Create error rate monitoring chart"""
    hours = list(range(24))
    error_rates = [max(0, random.uniform(0.5, 3.0) + random.uniform(-1, 1)) for _ in hours]
    
    fig = go.Figure(data=go.Scatter(
        x=hours,
        y=error_rates,
        mode='lines+markers',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title="Error Rate Trends",
        xaxis_title="Hour",
        yaxis_title="Error Rate %",
        height=300
    )
    
    return fig

def create_response_time_chart(timeframe):
    """Create response time distribution chart"""
    response_times = [random.normal(200, 50) for _ in range(100)]
    response_times = [max(50, rt) for rt in response_times]  # Ensure positive values
    
    fig = go.Figure(data=go.Histogram(
        x=response_times,
        nbinsx=20,
        marker_color='green',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Response Time Distribution",
        xaxis_title="Response Time (ms)",
        yaxis_title="Frequency",
        height=300
    )
    
    return fig

def create_resource_utilization_chart():
    """Create resource utilization chart"""
    resources = ['CPU', 'Memory', 'Disk', 'Network']
    utilization = [random.randint(60, 90) for _ in resources]
    
    fig = go.Figure(data=go.Bar(
        x=resources,
        y=utilization,
        marker_color=['red' if u > 80 else 'orange' if u > 70 else 'green' for u in utilization],
        text=[f"{u}%" for u in utilization],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Resource Utilization",
        xaxis_title="Resource Type",
        yaxis_title="Utilization %",
        height=300
    )
    
    return fig

def generate_incident_response_plan(incident_type, severity, affected_areas, description, groq_client):
    """Generate AI-powered incident response plan"""
    
    try:
        prompt = f"""
        Generate a comprehensive incident response plan for:
        
        Incident Type: {incident_type}
        Severity: {severity}
        Affected Areas: {', '.join(affected_areas)}
        Description: {description}
        
        Provide:
        1. Immediate actions (first 15 minutes)
        2. Short-term response (1-4 hours)
        3. Communication plan
        4. Recovery steps
        5. Prevention measures
        
        Format as a structured action plan.
        """
        
        return groq_client.generate_response(prompt, temperature=0.2)
        
    except Exception as e:
        return f"""
        **Automated Response Plan Generated**
        
        **Immediate Actions (0-15 minutes):**
        1. Assess scope and impact of {incident_type}
        2. Notify relevant stakeholders
        3. Activate incident response team
        4. Document initial findings
        
        **Short-term Response (1-4 hours):**
        1. Implement containment measures
        2. Begin resolution procedures
        3. Monitor affected systems
        4. Provide regular status updates
        
        **Communication Plan:**
        1. Internal team notification
        2. Management escalation if needed
        3. Customer communication if applicable
        4. Vendor coordination as required
        
        Note: AI service not available for detailed plan generation. Please check configuration.
        """

def generate_sample_incidents():
    """Generate sample active incidents"""
    
    return [
        {
            'id': 'INC-20250528-1001',
            'title': 'Supplier Delivery Delay',
            'type': 'Supply Disruption',
            'severity': 'High',
            'status': 'In Progress',
            'priority': 'P2',
            'assigned': 'Supply Chain Team',
            'created': '2 hours ago'
        },
        {
            'id': 'INC-20250528-1002',
            'title': 'Route Optimization Failure',
            'type': 'System Outage',
            'severity': 'Medium',
            'status': 'Open',
            'priority': 'P3',
            'assigned': 'IT Operations',
            'created': '45 minutes ago'
        },
        {
            'id': 'INC-20250527-0995',
            'title': 'Quality Control Issue',
            'type': 'Quality Issue',
            'severity': 'Low',
            'status': 'Resolved',
            'priority': 'P4',
            'assigned': 'QA Team',
            'created': '1 day ago'
        }
    ]

if __name__ == "__main__":
    main()