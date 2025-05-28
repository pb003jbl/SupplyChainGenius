import os
import json
import re
import pandas as pd
import streamlit as st
import plotly.express as px
from typing import Annotated
from tavily import TavilyClient
from autogen import AssistantAgent, UserProxyAgent, register_function, Cache
from autogen.agentchat import GroupChat, GroupChatManager

# -------------------------
# ENVIRONMENT CONFIGURATION
# -------------------------
os.environ["AUTOGEN_USE_DOCKER"] = "0"
os.environ["OPENAI_API_KEY"] = '<YOUR_OPENAI_KEY>'
os.environ["TAVILY_API_KEY"] = '<YOUR_TAVILY_KEY>'

# -------------------------
# STREAMLIT UI SETUP
# -------------------------
st.set_page_config(page_title="Inventory Redistribution AI", layout="wide")
st.title("📦 Inventory Redistribution Optimizer")

# -------------------------
# INITIALIZE TAVILY CLIENT
# -------------------------
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Search tool

def tavily_search_tool(query: Annotated[str, "City Data Query"]) -> Annotated[str, "Search results from Tavily"]:
    return tavily.get_search_context(query=query, search_depth="advanced")

# Prompt templates
REASONING_PROMPT = """
Analyze the forecast data against the real-time search results and evaluate if the forecast is reasonable or needs correction.
Forecast Data: {forecast_data}
Search Results: {search_results}

Provide a detailed reasoning on why the forecast aligns or deviates based on the search results.
"""

OPTIMIZATION_PROMPT = """
Using the analyzed forecast data, inventory levels, and route data, create an optimized redistribution plan.
Forecast Data: {forecast_data}
Inventory Data: {inventory_data}
Route Data: {route_data}

Consider minimizing costs and aligning with forecasted demands. Return the final redistribution plan in JSON list format with fields: Source, Destination, Product, Quantity.
"""

# Prompt builders

def reasoning_message(sender, recipient, context):
    return REASONING_PROMPT.format(
        forecast_data=context["forecast_data"],
        search_results=context["search_results"]
    )

def optimization_message(sender, recipient, context):
    return OPTIMIZATION_PROMPT.format(
        forecast_data=context["forecast_data"],
        inventory_data=context["inventory_data"],
        route_data=context["route_data"]
    )

# -------------------------
# AGENTS
# -------------------------
user_proxy = UserProxyAgent(
    name="UserProxy",
    system_message="You are the user interacting with the agents.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "code", "use_docker": False},
)

reasoning_agent = AssistantAgent(
    name="ReasoningAgent",
    llm_config={"config_list": [{"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}]},
    system_message="Analyze forecast data using search results. Return TERMINATE when done."
)

optimization_agent = AssistantAgent(
    name="OptimizationAgent",
    llm_config={"config_list": [{"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}]},
    system_message="Create an optimized redistribution plan using analyzed data. Return TERMINATE when done."
)

register_function(
    tavily_search_tool,
    caller=reasoning_agent,
    executor=user_proxy,
    name="tavily_search_tool",
    description="Conducts adaptive search using Tavily."
)

# -------------------------
# DATA SETUP
# -------------------------
forecast_data = [
    {"City": "Goa", "Product": "Soap", "Forecasted_Demand": 1500, "Month": "December"},
    {"City": "Coorg", "Product": "Biscuits", "Forecasted_Demand": 700, "Month": "December"},
    {"City": "Mahabaleshwar", "Product": "Soap", "Forecasted_Demand": 1000, "Month": "December"},
    {"City": "Lonavala", "Product": "Biscuits", "Forecasted_Demand": 850, "Month": "December"},
    {"City": "Ooty", "Product": "Soap", "Forecasted_Demand": 400, "Month": "December"}
]

inventory_data = [
    {"City": "Goa", "Product": "Soap", "Stock_Level": 2000},
    {"City": "Coorg", "Product": "Biscuits", "Stock_Level": 400},
    {"City": "Mahabaleshwar", "Product": "Soap", "Stock_Level": 1100},
    {"City": "Lonavala", "Product": "Biscuits", "Stock_Level": 800},
    {"City": "Ooty", "Product": "Soap", "Stock_Level": 500}
]

route_data = [
    {"Source": "Goa", "Destination": "Coorg", "Distance_km": 550, "Cost_per_km": 20, "Average_Travel_Time_hrs": 10},
    {"Source": "Goa", "Destination": "Ooty", "Distance_km": 750, "Cost_per_km": 22, "Average_Travel_Time_hrs": 15},
    {"Source": "Coorg", "Destination": "Goa", "Distance_km": 550, "Cost_per_km": 20, "Average_Travel_Time_hrs": 10},
    {"Source": "Coorg", "Destination": "Mahabaleshwar", "Distance_km": 400, "Cost_per_km": 18, "Average_Travel_Time_hrs": 8},
    {"Source": "Lonavala", "Destination": "Goa", "Distance_km": 450, "Cost_per_km": 19, "Average_Travel_Time_hrs": 7},
    {"Source": "Ooty", "Destination": "Coorg", "Distance_km": 800, "Cost_per_km": 21, "Average_Travel_Time_hrs": 16}
]

# -------------------------
# GROUP CHAT
# -------------------------
group_chat = GroupChat(
    agents=[user_proxy, reasoning_agent, optimization_agent],
    messages=[],
    max_round=12
)

manager = GroupChatManager(groupchat=group_chat, llm_config={"config_list": [{"model": "gpt-3.5-turbo"}]})

# -------------------------
# RUN PIPELINE
# -------------------------
with Cache.disk(cache_seed=42) as cache:
    st.info("Running reasoning and optimization agents...")

    reasoning_result = user_proxy.initiate_chat(
        reasoning_agent,
        message=reasoning_message,
        forecast_data=forecast_data,
        search_results=tavily_search_tool("Search for recent news about major calamities or reduced tourist footfall in Goa, Coorg, Mahabaleshwar, Lonavala, and Ooty."),
        cache=cache
    )

    st.subheader("🧠 Forecast Analysis")
    st.write(reasoning_result.chat_history[-1]['content'])

    result_optimization = user_proxy.initiate_chat(
        optimization_agent,
        message=optimization_message,
        forecast_data=forecast_data,
        inventory_data=inventory_data,
        route_data=route_data,
        cache=cache
    )

    st.subheader("📋 Redistribution Plan")
    plan_text = result_optimization.chat_history[-1]['content']
    st.write(plan_text)

    st.subheader("📊 Redistribution Plan Visualization")

    try:
        plan_json_match = re.search(r"\[.*\]", plan_text, re.DOTALL)
        if plan_json_match:
            plan_json_str = plan_json_match.group(0)
            redistribution_data = json.loads(plan_json_str)
            df = pd.DataFrame(redistribution_data)

            if not df.empty:
                st.dataframe(df)

                all_nodes = list(set(df["Source"]) | set(df["Destination"]))
                source_indices = [all_nodes.index(s) for s in df["Source"]]
                target_indices = [all_nodes.index(d) for d in df["Destination"]]

                fig = px.sankey(
                    node=dict(label=all_nodes),
                    link=dict(
                        source=source_indices,
                        target=target_indices,
                        value=df["Quantity"]
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Optimization returned an empty redistribution plan.")
        else:
            st.error("No structured redistribution data found.")
    except Exception as e:
        st.exception(f"Failed to visualize redistribution: {e}")
