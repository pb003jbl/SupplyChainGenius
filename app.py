import streamlit as st
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Supply Chain Management Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path("styles/main.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Main page content
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🏭 Supply Chain Management Platform</h1>
        <p class="subtitle">AI-Powered Enterprise Supply Chain Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Analytics</h3>
            <p>Real-time supply chain insights powered by GROQ LLM</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI Agents</h3>
            <p>Autonomous decision-making with AutoGen framework</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Optimization</h3>
            <p>Advanced algorithms for supply chain efficiency</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📋 Reports</h3>
            <p>Executive-level reporting and recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Platform overview
    st.markdown("---")
    
    st.markdown("""
    ## 🎯 Platform Overview
    
    This enterprise-grade supply chain management platform leverages cutting-edge AI technology to optimize your supply chain operations:
    
    ### Key Features:
    - **AI-Powered Analysis**: Advanced natural language processing with GROQ LLM for intelligent insights
    - **Autonomous Agents**: Multi-agent system using AutoGen for automated decision-making
    - **Interactive Dashboards**: Real-time visualization of supply chain KPIs and metrics
    - **Data Integration**: Upload and analyze your own supply chain datasets
    - **Optimization Engine**: Advanced algorithms for inventory, routing, and demand forecasting
    - **Executive Reporting**: CXO-level reports and strategic recommendations
    
    ### Navigation:
    Use the sidebar to navigate between different modules:
    - 📊 **Dashboard**: Overview of key metrics and performance indicators
    - 📁 **Data Upload**: Import and manage your supply chain data
    - 🔍 **Analysis**: AI-powered supply chain analysis and insights
    - ⚡ **Optimization**: Advanced optimization algorithms and recommendations
    - 📋 **Reports**: Generate executive-level reports and documentation
    - ⚙️ **Settings**: Configure platform settings and API keys
    """)
    
    # Getting started section
    st.markdown("---")
    
    st.markdown("""
    ## 🚀 Getting Started
    
    1. **Configure Settings**: Visit the Settings page to configure your API keys
    2. **Upload Data**: Use the Data Upload module to import your supply chain data
    3. **Explore Dashboard**: View real-time metrics and KPIs
    4. **Run Analysis**: Leverage AI agents for intelligent insights
    5. **Optimize Operations**: Apply optimization recommendations
    6. **Generate Reports**: Create executive-level documentation
    """)

if __name__ == "__main__":
    main()
