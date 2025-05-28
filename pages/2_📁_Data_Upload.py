import streamlit as st
import pandas as pd
import json
import os
from utils.data_handler import DataHandler

st.set_page_config(page_title="Data Upload", page_icon="📁", layout="wide")

def main():
    st.title("📁 Data Upload & Management")
    st.markdown("Upload and manage your supply chain data")
    
    data_handler = DataHandler()
    
    # Tabs for different data types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Forecast Data", 
        "📦 Inventory Data", 
        "🚚 Route Data", 
        "🏭 Supplier Data",
        "📋 Sample Data"
    ])
    
    with tab1:
        st.markdown("### Upload Forecast Data")
        st.markdown("Upload demand forecast data for different cities and products")
        
        # File uploader
        forecast_file = st.file_uploader(
            "Choose forecast data file", 
            type=['csv', 'xlsx', 'json'],
            key="forecast_upload"
        )
        
        if forecast_file is not None:
            try:
                if forecast_file.name.endswith('.csv'):
                    df = pd.read_csv(forecast_file)
                elif forecast_file.name.endswith('.xlsx'):
                    df = pd.read_excel(forecast_file)
                elif forecast_file.name.endswith('.json'):
                    df = pd.read_json(forecast_file)
                
                st.markdown("#### Preview:")
                st.dataframe(df.head())
                
                # Validate required columns
                required_cols = ['City', 'Product', 'Forecasted_Demand', 'Month']
                if all(col in df.columns for col in required_cols):
                    if st.button("Save Forecast Data", key="save_forecast"):
                        data_handler.save_forecast_data(df.to_dict('records'))
                        st.success("Forecast data saved successfully!")
                        st.rerun()
                else:
                    st.error(f"Missing required columns: {required_cols}")
                    st.info("Your data should include: City, Product, Forecasted_Demand, Month")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Show current data
        current_forecast = data_handler.get_forecast_data()
        if current_forecast:
            st.markdown("#### Current Forecast Data:")
            st.dataframe(pd.DataFrame(current_forecast))
            if st.button("Clear Forecast Data", key="clear_forecast"):
                data_handler.clear_forecast_data()
                st.success("Forecast data cleared!")
                st.rerun()
    
    with tab2:
        st.markdown("### Upload Inventory Data")
        st.markdown("Upload current inventory levels for different locations")
        
        inventory_file = st.file_uploader(
            "Choose inventory data file", 
            type=['csv', 'xlsx', 'json'],
            key="inventory_upload"
        )
        
        if inventory_file is not None:
            try:
                if inventory_file.name.endswith('.csv'):
                    df = pd.read_csv(inventory_file)
                elif inventory_file.name.endswith('.xlsx'):
                    df = pd.read_excel(inventory_file)
                elif inventory_file.name.endswith('.json'):
                    df = pd.read_json(inventory_file)
                
                st.markdown("#### Preview:")
                st.dataframe(df.head())
                
                required_cols = ['City', 'Product', 'Stock_Level']
                if all(col in df.columns for col in required_cols):
                    if st.button("Save Inventory Data", key="save_inventory"):
                        data_handler.save_inventory_data(df.to_dict('records'))
                        st.success("Inventory data saved successfully!")
                        st.rerun()
                else:
                    st.error(f"Missing required columns: {required_cols}")
                    st.info("Your data should include: City, Product, Stock_Level")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        current_inventory = data_handler.get_inventory_data()
        if current_inventory:
            st.markdown("#### Current Inventory Data:")
            st.dataframe(pd.DataFrame(current_inventory))
            if st.button("Clear Inventory Data", key="clear_inventory"):
                data_handler.clear_inventory_data()
                st.success("Inventory data cleared!")
                st.rerun()
    
    with tab3:
        st.markdown("### Upload Route Data")
        st.markdown("Upload transportation routes and costs between locations")
        
        route_file = st.file_uploader(
            "Choose route data file", 
            type=['csv', 'xlsx', 'json'],
            key="route_upload"
        )
        
        if route_file is not None:
            try:
                if route_file.name.endswith('.csv'):
                    df = pd.read_csv(route_file)
                elif route_file.name.endswith('.xlsx'):
                    df = pd.read_excel(route_file)
                elif route_file.name.endswith('.json'):
                    df = pd.read_json(route_file)
                
                st.markdown("#### Preview:")
                st.dataframe(df.head())
                
                required_cols = ['Source', 'Destination', 'Distance_km', 'Cost_per_km', 'Average_Travel_Time_hrs']
                if all(col in df.columns for col in required_cols):
                    if st.button("Save Route Data", key="save_route"):
                        data_handler.save_route_data(df.to_dict('records'))
                        st.success("Route data saved successfully!")
                        st.rerun()
                else:
                    st.error(f"Missing required columns: {required_cols}")
                    st.info("Your data should include: Source, Destination, Distance_km, Cost_per_km, Average_Travel_Time_hrs")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        current_route = data_handler.get_route_data()
        if current_route:
            st.markdown("#### Current Route Data:")
            st.dataframe(pd.DataFrame(current_route))
            if st.button("Clear Route Data", key="clear_route"):
                data_handler.clear_route_data()
                st.success("Route data cleared!")
                st.rerun()
    
    with tab4:
        st.markdown("### Upload Supplier Data")
        st.markdown("Upload supplier information and performance metrics")
        
        supplier_file = st.file_uploader(
            "Choose supplier data file", 
            type=['csv', 'xlsx', 'json'],
            key="supplier_upload"
        )
        
        if supplier_file is not None:
            try:
                if supplier_file.name.endswith('.csv'):
                    df = pd.read_csv(supplier_file)
                elif supplier_file.name.endswith('.xlsx'):
                    df = pd.read_excel(supplier_file)
                elif supplier_file.name.endswith('.json'):
                    df = pd.read_json(supplier_file)
                
                st.markdown("#### Preview:")
                st.dataframe(df.head())
                
                required_cols = ['Supplier_Name', 'Product', 'Lead_Time_Days', 'Reliability_Score', 'Cost_per_Unit']
                if all(col in df.columns for col in required_cols):
                    if st.button("Save Supplier Data", key="save_supplier"):
                        data_handler.save_supplier_data(df.to_dict('records'))
                        st.success("Supplier data saved successfully!")
                        st.rerun()
                else:
                    st.error(f"Missing required columns: {required_cols}")
                    st.info("Your data should include: Supplier_Name, Product, Lead_Time_Days, Reliability_Score, Cost_per_Unit")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        current_supplier = data_handler.get_supplier_data()
        if current_supplier:
            st.markdown("#### Current Supplier Data:")
            st.dataframe(pd.DataFrame(current_supplier))
            if st.button("Clear Supplier Data", key="clear_supplier"):
                data_handler.clear_supplier_data()
                st.success("Supplier data cleared!")
                st.rerun()
    
    with tab5:
        st.markdown("### Sample Data")
        st.markdown("Load sample datasets to explore the platform functionality")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Available Sample Datasets:")
            st.markdown("""
            - **Forecast Data**: Demand predictions for tourist destinations
            - **Inventory Data**: Current stock levels across locations
            - **Route Data**: Transportation routes and costs
            - **Supplier Data**: Supplier information and performance metrics
            """)
            
            if st.button("Load All Sample Data", key="load_samples"):
                data_handler.load_sample_data()
                st.success("Sample data loaded successfully!")
                st.rerun()
        
        with col2:
            st.markdown("#### Sample Data Preview:")
            
            # Show sample data previews
            sample_forecast = data_handler.load_sample_forecast()
            if sample_forecast:
                st.markdown("**Forecast Sample:**")
                st.dataframe(pd.DataFrame(sample_forecast[:3]))
            
            sample_inventory = data_handler.load_sample_inventory()
            if sample_inventory:
                st.markdown("**Inventory Sample:**")
                st.dataframe(pd.DataFrame(sample_inventory[:3]))
        
        # Data export options
        st.markdown("---")
        st.markdown("### Export Current Data")
        
        export_col1, export_col2, export_col3, export_col4 = st.columns(4)
        
        with export_col1:
            if st.button("Export Forecast", key="export_forecast"):
                forecast_data = data_handler.get_forecast_data()
                if forecast_data:
                    df = pd.DataFrame(forecast_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Forecast CSV",
                        data=csv,
                        file_name="forecast_data.csv",
                        mime="text/csv"
                    )
        
        with export_col2:
            if st.button("Export Inventory", key="export_inventory"):
                inventory_data = data_handler.get_inventory_data()
                if inventory_data:
                    df = pd.DataFrame(inventory_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Inventory CSV",
                        data=csv,
                        file_name="inventory_data.csv",
                        mime="text/csv"
                    )
        
        with export_col3:
            if st.button("Export Routes", key="export_routes"):
                route_data = data_handler.get_route_data()
                if route_data:
                    df = pd.DataFrame(route_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Routes CSV",
                        data=csv,
                        file_name="route_data.csv",
                        mime="text/csv"
                    )
        
        with export_col4:
            if st.button("Export Suppliers", key="export_suppliers"):
                supplier_data = data_handler.get_supplier_data()
                if supplier_data:
                    df = pd.DataFrame(supplier_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Suppliers CSV",
                        data=csv,
                        file_name="supplier_data.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()
