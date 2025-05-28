import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import folium
from streamlit_folium import folium_static

class GoogleMapsIntegration:
    """Google Maps integration for supply chain route optimization"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    def _get_api_key(self) -> str:
        """Get Google Maps API key from environment or config"""
        # First try environment variable
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not api_key:
            # Try configuration file
            config = self._load_config()
            api_key = config.get("maps_api_key", "")
        
        return api_key
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path("data/config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def geocode_location(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location using Google Geocoding API"""
        if not self.api_key:
            st.warning("Google Maps API key not configured. Please add it in Settings.")
            return None
            
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "address": location,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK" and data["results"]:
                    location_data = data["results"][0]["geometry"]["location"]
                    return {
                        "lat": location_data["lat"],
                        "lng": location_data["lng"]
                    }
                else:
                    st.warning(f"Could not geocode location: {location}")
                    return None
            else:
                st.error(f"Geocoding API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error geocoding location {location}: {str(e)}")
            return None
    
    def get_route_optimization(self, locations: List[str], optimize: bool = True) -> Optional[Dict[str, Any]]:
        """Get optimized route using Google Maps Directions API"""
        if not self.api_key:
            st.warning("Google Maps API key not configured. Please add it in Settings.")
            return None
            
        if len(locations) < 2:
            st.error("At least 2 locations required for route optimization")
            return None
            
        try:
            origin = locations[0]
            destination = locations[-1]
            waypoints = locations[1:-1] if len(locations) > 2 else []
            
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "key": self.api_key,
                "optimize": optimize
            }
            
            if waypoints:
                waypoints_str = "|".join(waypoints)
                if optimize:
                    waypoints_str = "optimize:true|" + waypoints_str
                params["waypoints"] = waypoints_str
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK" and data["routes"]:
                    route = data["routes"][0]
                    
                    # Extract route information
                    route_info = {
                        "total_distance": route["legs"][0]["distance"]["value"] / 1000,  # Convert to km
                        "total_duration": route["legs"][0]["duration"]["value"] / 3600,  # Convert to hours
                        "waypoint_order": route.get("waypoint_order", []),
                        "overview_polyline": route["overview_polyline"]["points"],
                        "legs": []
                    }
                    
                    # Extract leg information
                    for leg in route["legs"]:
                        leg_info = {
                            "start_address": leg["start_address"],
                            "end_address": leg["end_address"],
                            "distance_km": leg["distance"]["value"] / 1000,
                            "duration_hours": leg["duration"]["value"] / 3600,
                            "start_location": leg["start_location"],
                            "end_location": leg["end_location"]
                        }
                        route_info["legs"].append(leg_info)
                    
                    return route_info
                else:
                    st.error(f"Route optimization failed: {data.get('status', 'Unknown error')}")
                    return None
            else:
                st.error(f"Directions API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error optimizing route: {str(e)}")
            return None
    
    def calculate_route_matrix(self, locations: List[str]) -> Optional[Dict[str, Any]]:
        """Calculate distance and time matrix between locations"""
        if not self.api_key:
            st.warning("Google Maps API key not configured. Please add it in Settings.")
            return None
            
        try:
            url = f"{self.base_url}/distancematrix/json"
            params = {
                "origins": "|".join(locations),
                "destinations": "|".join(locations),
                "key": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    matrix_data = {
                        "origins": data["origin_addresses"],
                        "destinations": data["destination_addresses"],
                        "distance_matrix": [],
                        "duration_matrix": []
                    }
                    
                    for row in data["rows"]:
                        distance_row = []
                        duration_row = []
                        
                        for element in row["elements"]:
                            if element["status"] == "OK":
                                distance_row.append(element["distance"]["value"] / 1000)  # km
                                duration_row.append(element["duration"]["value"] / 3600)  # hours
                            else:
                                distance_row.append(float('inf'))
                                duration_row.append(float('inf'))
                        
                        matrix_data["distance_matrix"].append(distance_row)
                        matrix_data["duration_matrix"].append(duration_row)
                    
                    return matrix_data
                else:
                    st.error(f"Distance Matrix API error: {data.get('status', 'Unknown error')}")
                    return None
            else:
                st.error(f"Distance Matrix API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error calculating route matrix: {str(e)}")
            return None
    
    def create_interactive_map(self, route_data: List[Dict], optimization_result: Optional[Dict] = None) -> folium.Map:
        """Create interactive map with route visualization"""
        
        # Get center coordinates
        if route_data:
            # Try to geocode first location for map center
            first_location = route_data[0].get('Source', 'India')
            center_coords = self.geocode_location(first_location)
            
            if center_coords:
                center_lat, center_lng = center_coords["lat"], center_coords["lng"]
            else:
                # Default to India center
                center_lat, center_lng = 20.5937, 78.9629
        else:
            center_lat, center_lng = 20.5937, 78.9629
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Add location markers
        locations_added = set()
        for route in route_data:
            source = route['Source']
            destination = route['Destination']
            
            # Add source marker
            if source not in locations_added:
                source_coords = self.geocode_location(source)
                if source_coords:
                    folium.Marker(
                        [source_coords["lat"], source_coords["lng"]],
                        popup=f"<b>{source}</b><br>Hub Location",
                        tooltip=source,
                        icon=folium.Icon(color='blue', icon='warehouse', prefix='fa')
                    ).add_to(m)
                    locations_added.add(source)
            
            # Add destination marker
            if destination not in locations_added:
                dest_coords = self.geocode_location(destination)
                if dest_coords:
                    folium.Marker(
                        [dest_coords["lat"], dest_coords["lng"]],
                        popup=f"<b>{destination}</b><br>Destination",
                        tooltip=destination,
                        icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
                    ).add_to(m)
                    locations_added.add(destination)
            
            # Add route line
            source_coords = self.geocode_location(source)
            dest_coords = self.geocode_location(destination)
            
            if source_coords and dest_coords:
                # Calculate route color based on efficiency
                distance = route.get('Distance_km', 0)
                cost = route.get('Cost_per_km', 0)
                total_cost = distance * cost
                
                # Color coding: green for efficient, red for expensive
                if total_cost < 10000:
                    color = 'green'
                elif total_cost < 20000:
                    color = 'orange'
                else:
                    color = 'red'
                
                folium.PolyLine(
                    locations=[[source_coords["lat"], source_coords["lng"]], 
                              [dest_coords["lat"], dest_coords["lng"]]],
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"<b>{source} → {destination}</b><br>"
                          f"Distance: {distance} km<br>"
                          f"Cost: ${total_cost:,.0f}<br>"
                          f"Time: {route.get('Average_Travel_Time_hrs', 0)} hrs"
                ).add_to(m)
        
        # Add optimization results if available
        if optimization_result and optimization_result.get('legs'):
            for i, leg in enumerate(optimization_result['legs']):
                start_loc = leg['start_location']
                end_loc = leg['end_location']
                
                folium.PolyLine(
                    locations=[[start_loc["lat"], start_loc["lng"]], 
                              [end_loc["lat"], end_loc["lng"]]],
                    color='purple',
                    weight=5,
                    opacity=1.0,
                    popup=f"<b>Optimized Route {i+1}</b><br>"
                          f"Distance: {leg['distance_km']:.1f} km<br>"
                          f"Duration: {leg['duration_hours']:.1f} hrs",
                    tooltip="Optimized Route"
                ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Route Legend</b></p>
        <p><i class="fa fa-warehouse" style="color:blue"></i> Source Hub</p>
        <p><i class="fa fa-map-marker" style="color:red"></i> Destination</p>
        <p><span style="color:green">━━━</span> Low Cost Route</p>
        <p><span style="color:orange">━━━</span> Medium Cost Route</p>
        <p><span style="color:red">━━━</span> High Cost Route</p>
        <p><span style="color:purple">━━━</span> Optimized Route</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def create_route_efficiency_heatmap(self, route_data: List[Dict]) -> go.Figure:
        """Create heatmap showing route efficiency across locations"""
        
        # Extract unique locations
        sources = list(set([route['Source'] for route in route_data]))
        destinations = list(set([route['Destination'] for route in route_data]))
        all_locations = list(set(sources + destinations))
        
        # Create efficiency matrix
        efficiency_matrix = []
        for source in all_locations:
            row = []
            for dest in all_locations:
                if source == dest:
                    row.append(100)  # Same location = 100% efficient
                else:
                    # Find route efficiency
                    route_found = False
                    for route in route_data:
                        if route['Source'] == source and route['Destination'] == dest:
                            distance = route['Distance_km']
                            cost_per_km = route['Cost_per_km']
                            total_cost = distance * cost_per_km
                            # Calculate efficiency score (inverse of cost, normalized)
                            efficiency = max(0, 100 - (total_cost / 500))  # Adjust scaling as needed
                            row.append(efficiency)
                            route_found = True
                            break
                    
                    if not route_found:
                        row.append(0)  # No direct route
            
            efficiency_matrix.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=efficiency_matrix,
            x=all_locations,
            y=all_locations,
            colorscale='RdYlGn',
            hoverongaps=False,
            hovertemplate='<b>%{y} → %{x}</b><br>Efficiency: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='Route Efficiency Heatmap',
            xaxis_title='Destination',
            yaxis_title='Source',
            height=600
        )
        
        return fig
    
    def suggest_route_optimization(self, route_data: List[Dict]) -> Dict[str, Any]:
        """Analyze routes and suggest optimizations"""
        
        suggestions = {
            "consolidation_opportunities": [],
            "alternative_routes": [],
            "cost_savings": 0,
            "efficiency_improvements": []
        }
        
        # Analyze for consolidation opportunities
        route_groups = {}
        for route in route_data:
            key = f"{route['Source']}-{route['Destination']}"
            if key not in route_groups:
                route_groups[key] = []
            route_groups[key].append(route)
        
        # Find routes that could be consolidated
        for key, routes in route_groups.items():
            if len(routes) > 1:
                total_cost = sum(r['Distance_km'] * r['Cost_per_km'] for r in routes)
                avg_cost = total_cost / len(routes)
                
                suggestions["consolidation_opportunities"].append({
                    "route": key,
                    "current_routes": len(routes),
                    "potential_savings": total_cost * 0.15,  # Assume 15% savings
                    "recommendation": f"Consolidate {len(routes)} routes into optimized schedule"
                })
        
        # Calculate potential total savings
        total_current_cost = sum(r['Distance_km'] * r['Cost_per_km'] for r in route_data)
        suggestions["cost_savings"] = total_current_cost * 0.12  # Assume 12% average savings
        
        # Efficiency improvements
        high_cost_routes = [r for r in route_data if r['Distance_km'] * r['Cost_per_km'] > 15000]
        
        for route in high_cost_routes:
            suggestions["efficiency_improvements"].append({
                "route": f"{route['Source']} → {route['Destination']}",
                "current_cost": route['Distance_km'] * route['Cost_per_km'],
                "improvement": "Consider alternative transportation modes or route optimization",
                "potential_savings": route['Distance_km'] * route['Cost_per_km'] * 0.2
            })
        
        return suggestions
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test Google Maps API connection"""
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key configured"
            }
        
        try:
            # Test with a simple geocoding request
            test_location = self.geocode_location("Mumbai, India")
            
            if test_location:
                return {
                    "success": True,
                    "message": "Google Maps API connection successful",
                    "test_result": f"Successfully geocoded Mumbai: {test_location}"
                }
            else:
                return {
                    "success": False,
                    "error": "API key may be invalid or quota exceeded"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }