import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import csv

class DataHandler:
    """Handles all data operations for the supply chain platform"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
    
    # ========== Data Loading Methods ==========
    
    def get_forecast_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load forecast data"""
        return self._load_json_data("forecast_data.json")
    
    def get_inventory_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load inventory data"""
        return self._load_json_data("inventory_data.json")
    
    def get_route_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load route data"""
        return self._load_json_data("route_data.json")
    
    def get_supplier_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load supplier data"""
        return self._load_json_data("supplier_data.json")
    
    def _load_json_data(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from JSON file"""
        file_path = self.data_dir / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
                return None
        return None
    
    # ========== Data Saving Methods ==========
    
    def save_forecast_data(self, data: List[Dict[str, Any]]) -> bool:
        """Save forecast data"""
        return self._save_json_data("forecast_data.json", data)
    
    def save_inventory_data(self, data: List[Dict[str, Any]]) -> bool:
        """Save inventory data"""
        return self._save_json_data("inventory_data.json", data)
    
    def save_route_data(self, data: List[Dict[str, Any]]) -> bool:
        """Save route data"""
        return self._save_json_data("route_data.json", data)
    
    def save_supplier_data(self, data: List[Dict[str, Any]]) -> bool:
        """Save supplier data"""
        return self._save_json_data("supplier_data.json", data)
    
    def _save_json_data(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to JSON file"""
        file_path = self.data_dir / filename
        
        try:
            # Add metadata
            save_data = {
                "data": data,
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "record_count": len(data),
                    "data_type": filename.replace("_data.json", "")
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
            
        except Exception as e:
            st.error(f"Error saving {filename}: {str(e)}")
            return False
    
    def _load_json_data(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from JSON file with metadata support"""
        file_path = self.data_dir / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
                
                # Handle both old format (direct list) and new format (with metadata)
                if isinstance(content, list):
                    return content
                elif isinstance(content, dict) and "data" in content:
                    return content["data"]
                else:
                    st.warning(f"Unexpected format in {filename}")
                    return None
                    
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
                return None
        return None
    
    # ========== Data Clearing Methods ==========
    
    def clear_forecast_data(self) -> bool:
        """Clear forecast data"""
        return self._delete_file("forecast_data.json")
    
    def clear_inventory_data(self) -> bool:
        """Clear inventory data"""
        return self._delete_file("inventory_data.json")
    
    def clear_route_data(self) -> bool:
        """Clear route data"""
        return self._delete_file("route_data.json")
    
    def clear_supplier_data(self) -> bool:
        """Clear supplier data"""
        return self._delete_file("supplier_data.json")
    
    def _delete_file(self, filename: str) -> bool:
        """Delete data file"""
        file_path = self.data_dir / filename
        
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            st.error(f"Error deleting {filename}: {str(e)}")
            return False
    
    # ========== Sample Data Methods ==========
    
    def load_sample_data(self) -> bool:
        """Load all sample datasets"""
        try:
            # Load sample forecast data
            forecast_data = self.load_sample_forecast()
            if forecast_data:
                self.save_forecast_data(forecast_data)
            
            # Load sample inventory data
            inventory_data = self.load_sample_inventory()
            if inventory_data:
                self.save_inventory_data(inventory_data)
            
            # Load sample route data
            route_data = self.load_sample_routes()
            if route_data:
                self.save_route_data(route_data)
            
            # Load sample supplier data
            supplier_data = self.load_sample_suppliers()
            if supplier_data:
                self.save_supplier_data(supplier_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")
            return False
    
    def load_sample_forecast(self) -> List[Dict[str, Any]]:
        """Load sample forecast data from CSV or return default"""
        csv_path = self.data_dir / "sample_forecast.csv"
        
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                return df.to_dict('records')
            except Exception:
                pass
        
        # Default sample data
        return [
            {"City": "Mumbai", "Product": "Electronics", "Forecasted_Demand": 2500, "Month": "January"},
            {"City": "Delhi", "Product": "Clothing", "Forecasted_Demand": 1800, "Month": "January"},
            {"City": "Bangalore", "Product": "Electronics", "Forecasted_Demand": 2200, "Month": "January"},
            {"City": "Chennai", "Product": "Pharmaceuticals", "Forecasted_Demand": 1600, "Month": "January"},
            {"City": "Kolkata", "Product": "Food Products", "Forecasted_Demand": 1400, "Month": "January"},
            {"City": "Pune", "Product": "Electronics", "Forecasted_Demand": 1900, "Month": "January"},
            {"City": "Hyderabad", "Product": "Textiles", "Forecasted_Demand": 1300, "Month": "January"},
            {"City": "Ahmedabad", "Product": "Chemicals", "Forecasted_Demand": 1100, "Month": "January"},
        ]
    
    def load_sample_inventory(self) -> List[Dict[str, Any]]:
        """Load sample inventory data from CSV or return default"""
        csv_path = self.data_dir / "sample_inventory.csv"
        
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                return df.to_dict('records')
            except Exception:
                pass
        
        # Default sample data
        return [
            {"City": "Mumbai", "Product": "Electronics", "Stock_Level": 2800, "Warehouse_Capacity": 5000, "Last_Updated": "2024-01-15"},
            {"City": "Delhi", "Product": "Clothing", "Stock_Level": 1500, "Warehouse_Capacity": 3000, "Last_Updated": "2024-01-15"},
            {"City": "Bangalore", "Product": "Electronics", "Stock_Level": 2000, "Warehouse_Capacity": 4000, "Last_Updated": "2024-01-15"},
            {"City": "Chennai", "Product": "Pharmaceuticals", "Stock_Level": 1800, "Warehouse_Capacity": 2500, "Last_Updated": "2024-01-15"},
            {"City": "Kolkata", "Product": "Food Products", "Stock_Level": 1200, "Warehouse_Capacity": 2000, "Last_Updated": "2024-01-15"},
            {"City": "Pune", "Product": "Electronics", "Stock_Level": 1700, "Warehouse_Capacity": 3500, "Last_Updated": "2024-01-15"},
            {"City": "Hyderabad", "Product": "Textiles", "Stock_Level": 1400, "Warehouse_Capacity": 2200, "Last_Updated": "2024-01-15"},
            {"City": "Ahmedabad", "Product": "Chemicals", "Stock_Level": 950, "Warehouse_Capacity": 1800, "Last_Updated": "2024-01-15"},
        ]
    
    def load_sample_routes(self) -> List[Dict[str, Any]]:
        """Load sample route data from CSV or return default"""
        csv_path = self.data_dir / "sample_routes.csv"
        
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                return df.to_dict('records')
            except Exception:
                pass
        
        # Default sample data
        return [
            {"Source": "Mumbai", "Destination": "Delhi", "Distance_km": 1400, "Cost_per_km": 25, "Average_Travel_Time_hrs": 18, "Route_Type": "Highway"},
            {"Source": "Mumbai", "Destination": "Bangalore", "Distance_km": 980, "Cost_per_km": 22, "Average_Travel_Time_hrs": 14, "Route_Type": "Highway"},
            {"Source": "Delhi", "Destination": "Kolkata", "Distance_km": 1470, "Cost_per_km": 24, "Average_Travel_Time_hrs": 20, "Route_Type": "Highway"},
            {"Source": "Bangalore", "Destination": "Chennai", "Distance_km": 350, "Cost_per_km": 20, "Average_Travel_Time_hrs": 6, "Route_Type": "Highway"},
            {"Source": "Mumbai", "Destination": "Pune", "Distance_km": 150, "Cost_per_km": 18, "Average_Travel_Time_hrs": 3, "Route_Type": "Highway"},
            {"Source": "Delhi", "Destination": "Ahmedabad", "Distance_km": 950, "Cost_per_km": 23, "Average_Travel_Time_hrs": 12, "Route_Type": "Highway"},
            {"Source": "Bangalore", "Destination": "Hyderabad", "Distance_km": 570, "Cost_per_km": 21, "Average_Travel_Time_hrs": 8, "Route_Type": "Highway"},
            {"Source": "Chennai", "Destination": "Kolkata", "Distance_km": 1670, "Cost_per_km": 26, "Average_Travel_Time_hrs": 22, "Route_Type": "Highway"},
        ]
    
    def load_sample_suppliers(self) -> List[Dict[str, Any]]:
        """Load sample supplier data from CSV or return default"""
        csv_path = self.data_dir / "sample_suppliers.csv"
        
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                return df.to_dict('records')
            except Exception:
                pass
        
        # Default sample data
        return [
            {"Supplier_Name": "TechCorp India", "Product": "Electronics", "Lead_Time_Days": 14, "Reliability_Score": 92, "Cost_per_Unit": 45.50, "Location": "Mumbai"},
            {"Supplier_Name": "Fashion Forward Ltd", "Product": "Clothing", "Lead_Time_Days": 21, "Reliability_Score": 88, "Cost_per_Unit": 28.75, "Location": "Delhi"},
            {"Supplier_Name": "MediSupply Co", "Product": "Pharmaceuticals", "Lead_Time_Days": 7, "Reliability_Score": 96, "Cost_per_Unit": 85.25, "Location": "Bangalore"},
            {"Supplier_Name": "Fresh Foods Ltd", "Product": "Food Products", "Lead_Time_Days": 3, "Reliability_Score": 94, "Cost_per_Unit": 12.50, "Location": "Chennai"},
            {"Supplier_Name": "TextileMakers Inc", "Product": "Textiles", "Lead_Time_Days": 18, "Reliability_Score": 85, "Cost_per_Unit": 22.30, "Location": "Hyderabad"},
            {"Supplier_Name": "ChemTech Solutions", "Product": "Chemicals", "Lead_Time_Days": 12, "Reliability_Score": 91, "Cost_per_Unit": 67.80, "Location": "Ahmedabad"},
            {"Supplier_Name": "ElectroMax Systems", "Product": "Electronics", "Lead_Time_Days": 16, "Reliability_Score": 89, "Cost_per_Unit": 42.00, "Location": "Pune"},
            {"Supplier_Name": "BioMed Supplies", "Product": "Pharmaceuticals", "Lead_Time_Days": 9, "Reliability_Score": 93, "Cost_per_Unit": 78.90, "Location": "Kolkata"},
        ]
    
    # ========== Data Validation Methods ==========
    
    def validate_forecast_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate forecast data structure and content"""
        required_fields = ["City", "Product", "Forecasted_Demand", "Month"]
        return self._validate_data_structure(data, required_fields, "Forecast")
    
    def validate_inventory_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate inventory data structure and content"""
        required_fields = ["City", "Product", "Stock_Level"]
        return self._validate_data_structure(data, required_fields, "Inventory")
    
    def validate_route_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate route data structure and content"""
        required_fields = ["Source", "Destination", "Distance_km", "Cost_per_km", "Average_Travel_Time_hrs"]
        return self._validate_data_structure(data, required_fields, "Route")
    
    def validate_supplier_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate supplier data structure and content"""
        required_fields = ["Supplier_Name", "Product", "Lead_Time_Days", "Reliability_Score", "Cost_per_Unit"]
        return self._validate_data_structure(data, required_fields, "Supplier")
    
    def _validate_data_structure(self, data: List[Dict[str, Any]], required_fields: List[str], data_type: str) -> Dict[str, Any]:
        """Generic data validation"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "record_count": len(data) if data else 0
        }
        
        if not data:
            validation_result["valid"] = False
            validation_result["errors"].append(f"No {data_type.lower()} data provided")
            return validation_result
        
        # Check structure
        for i, record in enumerate(data):
            missing_fields = [field for field in required_fields if field not in record or record[field] is None]
            
            if missing_fields:
                validation_result["errors"].append(
                    f"Record {i+1}: Missing required fields: {', '.join(missing_fields)}"
                )
                validation_result["valid"] = False
        
        # Type-specific validations
        if data_type == "Forecast":
            validation_result.update(self._validate_forecast_specific(data))
        elif data_type == "Inventory":
            validation_result.update(self._validate_inventory_specific(data))
        elif data_type == "Route":
            validation_result.update(self._validate_route_specific(data))
        elif data_type == "Supplier":
            validation_result.update(self._validate_supplier_specific(data))
        
        return validation_result
    
    def _validate_forecast_specific(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast-specific validation"""
        result = {"errors": [], "warnings": []}
        
        for i, record in enumerate(data):
            if "Forecasted_Demand" in record:
                try:
                    demand = float(record["Forecasted_Demand"])
                    if demand < 0:
                        result["errors"].append(f"Record {i+1}: Negative demand not allowed")
                    elif demand == 0:
                        result["warnings"].append(f"Record {i+1}: Zero demand detected")
                except (ValueError, TypeError):
                    result["errors"].append(f"Record {i+1}: Invalid demand value")
        
        return result
    
    def _validate_inventory_specific(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Inventory-specific validation"""
        result = {"errors": [], "warnings": []}
        
        for i, record in enumerate(data):
            if "Stock_Level" in record:
                try:
                    stock = float(record["Stock_Level"])
                    if stock < 0:
                        result["errors"].append(f"Record {i+1}: Negative stock not allowed")
                except (ValueError, TypeError):
                    result["errors"].append(f"Record {i+1}: Invalid stock value")
        
        return result
    
    def _validate_route_specific(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Route-specific validation"""
        result = {"errors": [], "warnings": []}
        
        for i, record in enumerate(data):
            # Validate numeric fields
            numeric_fields = ["Distance_km", "Cost_per_km", "Average_Travel_Time_hrs"]
            for field in numeric_fields:
                if field in record:
                    try:
                        value = float(record[field])
                        if value <= 0:
                            result["errors"].append(f"Record {i+1}: {field} must be positive")
                    except (ValueError, TypeError):
                        result["errors"].append(f"Record {i+1}: Invalid {field} value")
        
        return result
    
    def _validate_supplier_specific(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Supplier-specific validation"""
        result = {"errors": [], "warnings": []}
        
        for i, record in enumerate(data):
            # Validate reliability score
            if "Reliability_Score" in record:
                try:
                    score = float(record["Reliability_Score"])
                    if not (0 <= score <= 100):
                        result["errors"].append(f"Record {i+1}: Reliability score must be 0-100")
                except (ValueError, TypeError):
                    result["errors"].append(f"Record {i+1}: Invalid reliability score")
            
            # Validate lead time
            if "Lead_Time_Days" in record:
                try:
                    lead_time = int(record["Lead_Time_Days"])
                    if lead_time < 0:
                        result["errors"].append(f"Record {i+1}: Lead time cannot be negative")
                except (ValueError, TypeError):
                    result["errors"].append(f"Record {i+1}: Invalid lead time value")
        
        return result
    
    # ========== Data Analysis Helper Methods ==========
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data"""
        summary = {
            "forecast": self._get_dataset_summary(self.get_forecast_data()),
            "inventory": self._get_dataset_summary(self.get_inventory_data()),
            "routes": self._get_dataset_summary(self.get_route_data()),
            "suppliers": self._get_dataset_summary(self.get_supplier_data())
        }
        
        return summary
    
    def _get_dataset_summary(self, data: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get summary statistics for a dataset"""
        if not data:
            return {"available": False, "record_count": 0}
        
        return {
            "available": True,
            "record_count": len(data),
            "fields": list(data[0].keys()) if data else [],
            "last_updated": datetime.now().isoformat()
        }
    
    def export_all_data(self) -> Dict[str, Any]:
        """Export all data for backup or analysis"""
        return {
            "forecast_data": self.get_forecast_data(),
            "inventory_data": self.get_inventory_data(),
            "route_data": self.get_route_data(),
            "supplier_data": self.get_supplier_data(),
            "export_timestamp": datetime.now().isoformat()
        }
