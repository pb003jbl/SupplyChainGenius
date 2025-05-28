import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_handler import DataHandler
from utils.maps_integration import GoogleMapsIntegration
from streamlit_folium import st_folium

def main():
    st.title("🗺️ Interactive Route Maps & Optimization")
    st.markdown("Google Maps powered route visualization and optimization")
    
    # Initialize components
    data_handler = DataHandler()
    maps_integration = GoogleMapsIntegration()
    
    # Check data availability
    route_data = data_handler.get_route_data()
    inventory_data = data_handler.get_inventory_data()
    
    if not route_data:
        st.warning("Please upload route data first to visualize maps.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample Route Data"):
                data_handler.load_sample_data()
                st.rerun()
        with col2:
            st.info("Go to Data Upload section to add your own route data")
        return
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Interactive Map", 
        "🎯 Route Optimization", 
        "📊 Efficiency Analysis",
        "💡 Optimization Suggestions"
    ])
    
    with tab1:
        st.markdown("### Interactive Supply Chain Route Map")
        
        # Map controls
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("#### Map Controls")
            
            show_all_routes = st.checkbox("Show All Routes", value=True)
            
            if not show_all_routes:
                # Route filtering
                all_sources = list(set([route['Source'] for route in route_data]))
                selected_source = st.selectbox("Select Source Hub", ["All"] + all_sources)
                
                if selected_source != "All":
                    route_data = [r for r in route_data if r['Source'] == selected_source]
            
            cost_threshold = st.slider(
                "Max Route Cost ($)", 
                min_value=0, 
                max_value=50000, 
                value=50000,
                step=1000
            )
            
            # Filter by cost
            route_data = [r for r in route_data if r['Distance_km'] * r['Cost_per_km'] <= cost_threshold]
            
            st.markdown("#### Route Statistics")
            total_routes = len(route_data)
            avg_distance = sum(r['Distance_km'] for r in route_data) / total_routes if total_routes > 0 else 0
            total_cost = sum(r['Distance_km'] * r['Cost_per_km'] for r in route_data)
            
            st.metric("Total Routes", total_routes)
            st.metric("Avg Distance", f"{avg_distance:.0f} km")
            st.metric("Total Network Cost", f"${total_cost:,.0f}")
        
        with col1:
            if route_data:
                # Create and display interactive map
                interactive_map = maps_integration.create_interactive_map(route_data)
                st_folium(interactive_map, width=800, height=600)
            else:
                st.info("No routes match the current filters")
    
    with tab2:
        st.markdown("### Google Maps Route Optimization")
        
        # Route optimization interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Optimize Multi-Stop Routes")
            
            # Location selection for optimization
            all_locations = list(set([route['Source'] for route in route_data] + 
                                   [route['Destination'] for route in route_data]))
            
            selected_locations = st.multiselect(
                "Select locations for route optimization (order will be optimized)",
                all_locations,
                default=all_locations[:5] if len(all_locations) >= 5 else all_locations
            )
            
            if len(selected_locations) >= 2:
                optimization_options = st.expander("Optimization Options")
                with optimization_options:
                    optimize_waypoints = st.checkbox("Optimize waypoint order", value=True)
                    avoid_tolls = st.checkbox("Avoid tolls", value=False)
                    avoid_highways = st.checkbox("Avoid highways", value=False)
                
                if st.button("🚀 Optimize Route with Google Maps", type="primary"):
                    with st.spinner("Optimizing route using Google Maps..."):
                        optimization_result = maps_integration.get_route_optimization(selected_locations, optimize_waypoints)
                        
                        if optimization_result:
                            st.success("Route optimization completed!")
                            
                            # Display optimization results
                            st.markdown("#### Optimization Results")
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Total Distance", f"{optimization_result['total_distance']:.1f} km")
                            with col_b:
                                st.metric("Total Time", f"{optimization_result['total_duration']:.1f} hours")
                            with col_c:
                                estimated_cost = optimization_result['total_distance'] * 25  # Assume avg cost per km
                                st.metric("Estimated Cost", f"${estimated_cost:,.0f}")
                            
                            # Show optimized route details
                            if optimization_result.get('legs'):
                                st.markdown("#### Route Segments")
                                legs_data = []
                                for i, leg in enumerate(optimization_result['legs']):
                                    legs_data.append({
                                        "Segment": f"Leg {i+1}",
                                        "From": leg['start_address'],
                                        "To": leg['end_address'],
                                        "Distance (km)": f"{leg['distance_km']:.1f}",
                                        "Duration (hrs)": f"{leg['duration_hours']:.1f}"
                                    })
                                
                                st.dataframe(pd.DataFrame(legs_data), use_container_width=True)
                            
                            # Create map with optimized route
                            optimized_map = maps_integration.create_interactive_map(route_data, optimization_result)
                            st_folium(optimized_map, width=800, height=500)
                        
                        else:
                            st.error("Route optimization failed. Please check your Google Maps API configuration.")
            else:
                st.info("Select at least 2 locations for route optimization")
        
        with col2:
            st.markdown("#### API Status")
            
            # Test API connection
            if st.button("Test Google Maps API"):
                with st.spinner("Testing API connection..."):
                    test_result = maps_integration.test_api_connection()
                    
                    if test_result["success"]:
                        st.success("✅ Google Maps API connected successfully!")
                        st.info(test_result["message"])
                    else:
                        st.error(f"❌ API connection failed: {test_result['error']}")
                        st.info("Please configure your Google Maps API key in Settings")
            
            # Quick optimization tips
            st.markdown("#### Optimization Tips")
            st.markdown("""
            - **Route Consolidation**: Combine multiple trips
            - **Load Optimization**: Maximize vehicle capacity
            - **Time Windows**: Consider delivery time constraints
            - **Traffic Patterns**: Account for peak hours
            - **Fuel Efficiency**: Choose optimal vehicle types
            """)
    
    with tab3:
        st.markdown("### Route Efficiency Analysis")
        
        # Efficiency heatmap
        if route_data:
            efficiency_heatmap = maps_integration.create_route_efficiency_heatmap(route_data)
            st.plotly_chart(efficiency_heatmap, use_container_width=True)
            
            # Distance vs Cost analysis
            st.markdown("#### Cost Efficiency Analysis")
            
            # Prepare data for analysis
            analysis_data = []
            for route in route_data:
                total_cost = route['Distance_km'] * route['Cost_per_km']
                cost_per_km = route['Cost_per_km']
                efficiency_score = 100 - min(100, (cost_per_km - 15) * 5)  # Normalize around 15 $/km
                
                analysis_data.append({
                    'Route': f"{route['Source']} → {route['Destination']}",
                    'Distance_km': route['Distance_km'],
                    'Cost_per_km': cost_per_km,
                    'Total_Cost': total_cost,
                    'Travel_Time': route['Average_Travel_Time_hrs'],
                    'Efficiency_Score': max(0, efficiency_score)
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            
            # Cost vs Distance scatter plot
            fig_scatter = px.scatter(
                df_analysis,
                x='Distance_km',
                y='Total_Cost',
                size='Travel_Time',
                color='Efficiency_Score',
                hover_data=['Route'],
                title="Route Cost vs Distance Analysis",
                labels={
                    'Distance_km': 'Distance (km)',
                    'Total_Cost': 'Total Cost ($)',
                    'Efficiency_Score': 'Efficiency Score'
                },
                color_continuous_scale='RdYlGn'
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Top performing and underperforming routes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Most Efficient Routes")
                top_routes = df_analysis.nlargest(5, 'Efficiency_Score')[['Route', 'Efficiency_Score', 'Total_Cost']]
                st.dataframe(top_routes, use_container_width=True)
            
            with col2:
                st.markdown("#### Routes Needing Attention")
                bottom_routes = df_analysis.nsmallest(5, 'Efficiency_Score')[['Route', 'Efficiency_Score', 'Total_Cost']]
                st.dataframe(bottom_routes, use_container_width=True)
    
    with tab4:
        st.markdown("### AI-Powered Optimization Suggestions")
        
        if route_data:
            # Generate optimization suggestions
            suggestions = maps_integration.suggest_route_optimization(route_data)
            
            # Consolidation opportunities
            if suggestions["consolidation_opportunities"]:
                st.markdown("#### 🔄 Route Consolidation Opportunities")
                
                for opportunity in suggestions["consolidation_opportunities"]:
                    with st.expander(f"Consolidate {opportunity['route']} routes"):
                        st.write(f"**Current routes**: {opportunity['current_routes']}")
                        st.write(f"**Potential savings**: ${opportunity['potential_savings']:,.0f}")
                        st.write(f"**Recommendation**: {opportunity['recommendation']}")
            
            # Cost savings summary
            st.markdown("#### 💰 Potential Cost Savings")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Potential Savings", f"${suggestions['cost_savings']:,.0f}")
            with col2:
                current_cost = sum(r['Distance_km'] * r['Cost_per_km'] for r in route_data)
                savings_percentage = (suggestions['cost_savings'] / current_cost) * 100 if current_cost > 0 else 0
                st.metric("Savings Percentage", f"{savings_percentage:.1f}%")
            with col3:
                st.metric("Routes Analyzed", len(route_data))
            
            # Efficiency improvements
            if suggestions["efficiency_improvements"]:
                st.markdown("#### ⚡ Efficiency Improvement Recommendations")
                
                improvements_data = []
                for improvement in suggestions["efficiency_improvements"]:
                    improvements_data.append({
                        "Route": improvement["route"],
                        "Current Cost": f"${improvement['current_cost']:,.0f}",
                        "Potential Savings": f"${improvement['potential_savings']:,.0f}",
                        "Recommendation": improvement["improvement"]
                    })
                
                st.dataframe(pd.DataFrame(improvements_data), use_container_width=True)
            
            # Implementation roadmap
            st.markdown("#### 🛣️ Implementation Roadmap")
            
            roadmap_items = [
                {"Phase": "Phase 1 (Month 1)", "Action": "Implement route consolidation for high-volume corridors", "Impact": "15-20% cost reduction"},
                {"Phase": "Phase 2 (Month 2)", "Action": "Deploy Google Maps optimization for daily routing", "Impact": "8-12% efficiency gain"},
                {"Phase": "Phase 3 (Month 3)", "Action": "Integrate real-time traffic data for dynamic routing", "Impact": "5-8% time savings"},
                {"Phase": "Phase 4 (Month 4)", "Action": "Implement predictive analytics for route planning", "Impact": "10-15% cost optimization"}
            ]
            
            roadmap_df = pd.DataFrame(roadmap_items)
            st.dataframe(roadmap_df, use_container_width=True)
        
        else:
            st.info("Load route data to see optimization suggestions")

if __name__ == "__main__":
    main()