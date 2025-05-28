import streamlit as st
import os
import json
from pathlib import Path



def main():
    st.title("⚙️ Platform Settings")
    st.markdown("Configure API keys and platform settings")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔑 API Configuration", 
        "🤖 Agent Settings", 
        "📊 Dashboard Preferences",
        "🔒 Security & Privacy"
    ])
    
    with tab1:
        configure_apis()
    
    with tab2:
        configure_agents()
    
    with tab3:
        configure_dashboard()
    
    with tab4:
        configure_security()

def configure_apis():
    """Configure API keys and endpoints"""
    st.markdown("### API Configuration")
    st.markdown("Configure your API keys for GROQ LLM and other services")
    
    # Load existing configuration
    config = load_config()
    
    # GROQ API Configuration
    st.markdown("#### GROQ LLM Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        groq_api_key = st.text_input(
            "GROQ API Key",
            value=config.get("groq_api_key", ""),
            type="password",
            help="Your GROQ API key for LLM services"
        )
        
        groq_model = st.selectbox(
            "GROQ Model",
            ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            index=0,
            help="Select the GROQ model to use"
        )
        
        groq_endpoint = st.text_input(
            "GROQ API Endpoint",
            value=config.get("groq_endpoint", "https://api.groq.com/openai/v1"),
            help="GROQ API endpoint URL"
        )
    
    with col2:
        # Test GROQ connection
        if st.button("🧪 Test GROQ Connection"):
            if groq_api_key:
                with st.spinner("Testing GROQ connection..."):
                    test_result = test_groq_connection(groq_api_key, groq_endpoint, groq_model)
                    if test_result["success"]:
                        st.success("✅ GROQ connection successful!")
                        st.info(f"Model: {test_result['model']}")
                    else:
                        st.error(f"❌ Connection failed: {test_result['error']}")
            else:
                st.warning("Please enter GROQ API key first")
    
    st.markdown("---")
    
    # AutoGen Configuration
    st.markdown("#### AutoGen Agent Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        autogen_llm_provider = st.selectbox(
            "AutoGen LLM Provider",
            ["GROQ", "OpenAI", "Azure OpenAI"],
            help="LLM provider for AutoGen agents"
        )
        
        if autogen_llm_provider == "OpenAI":
            openai_api_key = st.text_input(
                "OpenAI API Key",
                value=config.get("openai_api_key", ""),
                type="password"
            )
        elif autogen_llm_provider == "Azure OpenAI":
            azure_api_key = st.text_input("Azure OpenAI API Key", type="password")
            azure_endpoint = st.text_input("Azure OpenAI Endpoint")
        
        max_agent_rounds = st.number_input(
            "Max Agent Conversation Rounds",
            min_value=5,
            max_value=50,
            value=config.get("max_agent_rounds", 12),
            help="Maximum rounds for agent conversations"
        )
        
        agent_timeout = st.number_input(
            "Agent Timeout (seconds)",
            min_value=30,
            max_value=300,
            value=config.get("agent_timeout", 120),
            help="Timeout for individual agent operations"
        )
    
    with col2:
        if st.button("🧪 Test AutoGen Setup"):
            st.info("Testing AutoGen configuration...")
            # Test would be implemented here
    
    st.markdown("---")
    
    # External Services
    st.markdown("#### External Services (Optional)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tavily_api_key = st.text_input(
            "Tavily Search API Key",
            value=config.get("tavily_api_key", ""),
            type="password",
            help="For external data search and validation"
        )
        
        weather_api_key = st.text_input(
            "Weather API Key",
            value=config.get("weather_api_key", ""),
            type="password",
            help="For weather-based supply chain analysis"
        )
    
    with col2:
        news_api_key = st.text_input(
            "News API Key",
            value=config.get("news_api_key", ""),
            type="password",
            help="For market news and trend analysis"
        )
        
        maps_api_key = st.text_input(
            "Google Maps API Key",
            value=config.get("maps_api_key", ""),
            type="password",
            help="For interactive maps, route optimization, and geographic analysis"
        )
        
        if maps_api_key and st.button("🧪 Test Google Maps API"):
            with st.spinner("Testing Google Maps API..."):
                from utils.maps_integration import GoogleMapsIntegration
                maps_client = GoogleMapsIntegration()
                test_result = maps_client.test_api_connection()
                
                if test_result["success"]:
                    st.success("✅ Google Maps API connected successfully!")
                    st.info(test_result["message"])
                else:
                    st.error(f"❌ Google Maps API test failed: {test_result['error']}")
                    st.info("Please verify your API key and ensure the following APIs are enabled: Geocoding, Directions, Distance Matrix")
    
    # Save configuration
    if st.button("💾 Save API Configuration", type="primary"):
        new_config = {
            "groq_api_key": groq_api_key,
            "groq_model": groq_model,
            "groq_endpoint": groq_endpoint,
            "autogen_llm_provider": autogen_llm_provider,
            "max_agent_rounds": max_agent_rounds,
            "agent_timeout": agent_timeout,
            "tavily_api_key": tavily_api_key,
            "weather_api_key": weather_api_key,
            "news_api_key": news_api_key,
            "maps_api_key": maps_api_key
        }
        
        if autogen_llm_provider == "OpenAI":
            new_config["openai_api_key"] = openai_api_key
        elif autogen_llm_provider == "Azure OpenAI":
            new_config["azure_api_key"] = azure_api_key
            new_config["azure_endpoint"] = azure_endpoint
        
        save_config(new_config)
        st.success("✅ Configuration saved successfully!")
        st.rerun()

def configure_agents():
    """Configure agent behaviors and settings"""
    st.markdown("### Agent Configuration")
    
    config = load_config()
    
    # Agent roles and behaviors
    st.markdown("#### Agent Roles & Behaviors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Reasoning Agent Settings**")
        
        reasoning_temperature = st.slider(
            "Reasoning Temperature",
            min_value=0.0,
            max_value=1.0,
            value=config.get("reasoning_temperature", 0.3),
            step=0.1,
            help="Lower values for more focused analysis"
        )
        
        reasoning_system_message = st.text_area(
            "Reasoning Agent System Message",
            value=config.get("reasoning_system_message", 
                "You are a supply chain reasoning agent. Analyze data systematically and provide detailed insights based on evidence."),
            height=100
        )
    
    with col2:
        st.markdown("**Optimization Agent Settings**")
        
        optimization_temperature = st.slider(
            "Optimization Temperature",
            min_value=0.0,
            max_value=1.0,
            value=config.get("optimization_temperature", 0.2),
            step=0.1,
            help="Lower values for more consistent optimization"
        )
        
        optimization_system_message = st.text_area(
            "Optimization Agent System Message",
            value=config.get("optimization_system_message",
                "You are a supply chain optimization agent. Focus on finding practical, cost-effective solutions with clear implementation steps."),
            height=100
        )
    
    # Agent interaction settings
    st.markdown("#### Agent Interaction Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enable_agent_memory = st.checkbox(
            "Enable Agent Memory",
            value=config.get("enable_agent_memory", True),
            help="Allow agents to remember previous conversations"
        )
        
        use_code_execution = st.checkbox(
            "Enable Code Execution",
            value=config.get("use_code_execution", False),
            help="Allow agents to execute code for analysis"
        )
    
    with col2:
        auto_approval = st.checkbox(
            "Auto-approve Agent Actions",
            value=config.get("auto_approval", True),
            help="Automatically approve agent decisions"
        )
        
        verbose_logging = st.checkbox(
            "Verbose Agent Logging",
            value=config.get("verbose_logging", False),
            help="Enable detailed logging of agent interactions"
        )
    
    with col3:
        parallel_agents = st.checkbox(
            "Enable Parallel Agents",
            value=config.get("parallel_agents", False),
            help="Run multiple agents in parallel when possible"
        )
        
        agent_caching = st.checkbox(
            "Enable Agent Caching",
            value=config.get("agent_caching", True),
            help="Cache agent responses for better performance"
        )
    
    # Save agent configuration
    if st.button("💾 Save Agent Configuration", type="primary"):
        agent_config = {
            "reasoning_temperature": reasoning_temperature,
            "reasoning_system_message": reasoning_system_message,
            "optimization_temperature": optimization_temperature,
            "optimization_system_message": optimization_system_message,
            "enable_agent_memory": enable_agent_memory,
            "use_code_execution": use_code_execution,
            "auto_approval": auto_approval,
            "verbose_logging": verbose_logging,
            "parallel_agents": parallel_agents,
            "agent_caching": agent_caching
        }
        
        config.update(agent_config)
        save_config(config)
        st.success("✅ Agent configuration saved!")

def configure_dashboard():
    """Configure dashboard preferences"""
    st.markdown("### Dashboard Preferences")
    
    config = load_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Settings")
        
        default_time_range = st.selectbox(
            "Default Time Range",
            ["Last 7 Days", "Last 30 Days", "Last Quarter", "Last Year"],
            index=1
        )
        
        auto_refresh = st.checkbox(
            "Auto-refresh Dashboard",
            value=config.get("auto_refresh", False)
        )
        
        if auto_refresh:
            refresh_interval = st.number_input(
                "Refresh Interval (minutes)",
                min_value=1,
                max_value=60,
                value=config.get("refresh_interval", 5)
            )
        
        dark_mode = st.checkbox(
            "Dark Mode",
            value=config.get("dark_mode", False)
        )
        
        show_tutorial = st.checkbox(
            "Show Tutorial on Login",
            value=config.get("show_tutorial", True)
        )
    
    with col2:
        st.markdown("#### Chart Preferences")
        
        default_chart_type = st.selectbox(
            "Default Chart Type",
            ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot"],
            index=0
        )
        
        chart_color_scheme = st.selectbox(
            "Color Scheme",
            ["Professional Blue", "Corporate Green", "Classic Grayscale", "Vibrant Colors"],
            index=0
        )
        
        show_data_labels = st.checkbox(
            "Show Data Labels on Charts",
            value=config.get("show_data_labels", True)
        )
        
        animate_charts = st.checkbox(
            "Animate Chart Transitions",
            value=config.get("animate_charts", True)
        )
    
    # KPI Selection
    st.markdown("#### Key Performance Indicators")
    st.markdown("Select which KPIs to display on the main dashboard")
    
    available_kpis = [
        "Fill Rate", "Inventory Turnover", "On-Time Delivery", 
        "Cost Efficiency", "Supplier Performance", "Transportation Cost",
        "Stock Accuracy", "Order Accuracy", "Lead Time Performance"
    ]
    
    selected_kpis = st.multiselect(
        "Dashboard KPIs",
        available_kpis,
        default=config.get("selected_kpis", available_kpis[:4])
    )
    
    # Save dashboard configuration
    if st.button("💾 Save Dashboard Preferences", type="primary"):
        dashboard_config = {
            "default_time_range": default_time_range,
            "auto_refresh": auto_refresh,
            "dark_mode": dark_mode,
            "show_tutorial": show_tutorial,
            "default_chart_type": default_chart_type,
            "chart_color_scheme": chart_color_scheme,
            "show_data_labels": show_data_labels,
            "animate_charts": animate_charts,
            "selected_kpis": selected_kpis
        }
        
        if auto_refresh:
            dashboard_config["refresh_interval"] = refresh_interval
        
        config.update(dashboard_config)
        save_config(config)
        st.success("✅ Dashboard preferences saved!")

def configure_security():
    """Configure security and privacy settings"""
    st.markdown("### Security & Privacy Settings")
    
    config = load_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Data Privacy")
        
        data_retention_days = st.number_input(
            "Data Retention Period (days)",
            min_value=30,
            max_value=365,
            value=config.get("data_retention_days", 90),
            help="How long to keep uploaded data"
        )
        
        anonymize_data = st.checkbox(
            "Anonymize Sensitive Data",
            value=config.get("anonymize_data", True),
            help="Remove or mask sensitive information"
        )
        
        encrypt_stored_data = st.checkbox(
            "Encrypt Stored Data",
            value=config.get("encrypt_stored_data", True),
            help="Encrypt data at rest"
        )
        
        audit_logging = st.checkbox(
            "Enable Audit Logging",
            value=config.get("audit_logging", True),
            help="Log all user actions for compliance"
        )
    
    with col2:
        st.markdown("#### API Security")
        
        rate_limit_enabled = st.checkbox(
            "Enable Rate Limiting",
            value=config.get("rate_limit_enabled", True),
            help="Limit API calls per minute"
        )
        
        if rate_limit_enabled:
            rate_limit_per_minute = st.number_input(
                "Rate Limit (calls per minute)",
                min_value=10,
                max_value=1000,
                value=config.get("rate_limit_per_minute", 100)
            )
        
        api_key_rotation = st.checkbox(
            "Enable API Key Rotation",
            value=config.get("api_key_rotation", False),
            help="Regularly rotate API keys"
        )
        
        secure_connections_only = st.checkbox(
            "HTTPS Only",
            value=config.get("secure_connections_only", True),
            help="Require secure connections"
        )
    
    # Compliance settings
    st.markdown("#### Compliance Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gdpr_compliance = st.checkbox(
            "GDPR Compliance Mode",
            value=config.get("gdpr_compliance", False)
        )
    
    with col2:
        hipaa_compliance = st.checkbox(
            "HIPAA Compliance Mode",
            value=config.get("hipaa_compliance", False)
        )
    
    with col3:
        sox_compliance = st.checkbox(
            "SOX Compliance Mode",
            value=config.get("sox_compliance", False)
        )
    
    # Save security configuration
    if st.button("💾 Save Security Settings", type="primary"):
        security_config = {
            "data_retention_days": data_retention_days,
            "anonymize_data": anonymize_data,
            "encrypt_stored_data": encrypt_stored_data,
            "audit_logging": audit_logging,
            "rate_limit_enabled": rate_limit_enabled,
            "api_key_rotation": api_key_rotation,
            "secure_connections_only": secure_connections_only,
            "gdpr_compliance": gdpr_compliance,
            "hipaa_compliance": hipaa_compliance,
            "sox_compliance": sox_compliance
        }
        
        if rate_limit_enabled:
            security_config["rate_limit_per_minute"] = rate_limit_per_minute
        
        config.update(security_config)
        save_config(config)
        st.success("✅ Security settings saved!")
    
    # System information
    st.markdown("---")
    st.markdown("### System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Platform Version:** 1.0.0")
        st.info(f"**Streamlit Version:** {st.__version__}")
    
    with col2:
        st.info(f"**Python Version:** {os.sys.version.split()[0]}")
        st.info(f"**Config File:** {get_config_path()}")
    
    with col3:
        if st.button("🧹 Clear All Data"):
            if st.checkbox("I understand this will delete all data"):
                clear_all_data()
                st.success("All data cleared!")
                st.rerun()

def load_config():
    """Load configuration from file"""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Error loading config: {e}")
            return {}
    return {}

def save_config(config):
    """Save configuration to file"""
    config_path = get_config_path()
    config_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        st.error(f"Error saving config: {e}")

def get_config_path():
    """Get path to configuration file"""
    return Path("data/config.json")

def test_groq_connection(api_key, endpoint, model):
    """Test GROQ API connection"""
    try:
        from utils.groq_client import GroqClient
        
        # Temporarily set environment variables for testing
        os.environ["GROQ_API_KEY"] = api_key
        
        client = GroqClient()
        response = client.generate_response("Test connection")
        
        return {
            "success": True,
            "model": model,
            "response_length": len(response)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def clear_all_data():
    """Clear all application data"""
    data_dir = Path("data")
    
    if data_dir.exists():
        for file in data_dir.glob("*.json"):
            if file.name != "config.json":  # Keep configuration
                file.unlink()
        
        for file in data_dir.glob("*.csv"):
            if not file.name.startswith("sample_"):  # Keep sample data
                file.unlink()

if __name__ == "__main__":
    main()
