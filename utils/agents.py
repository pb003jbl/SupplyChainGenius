import os
import json
from typing import Dict, Any, List, Optional
import streamlit as st
from pathlib import Path
import asyncio
from datetime import datetime

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    from autogen.agentchat import Agent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    st.warning("AutoGen not available. Some agent features will be limited.")

from utils.groq_client import GroqClient

class SupplyChainAgents:
    """Manages AutoGen agents for supply chain analysis and optimization"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.config = self._load_config()
        self.agents = {}
        self.group_chat = None
        self.manager = None
        
        if AUTOGEN_AVAILABLE:
            self._initialize_agents()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        config_path = Path("data/config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _get_llm_config(self, agent_type: str = "default") -> Dict[str, Any]:
        """Get LLM configuration for agents"""
        
        # Check if using GROQ or other providers
        provider = self.config.get("autogen_llm_provider", "GROQ")
        
        if provider == "GROQ":
            return {
                "config_list": [{
                    "model": self.config.get("groq_model", "llama3-8b-8192"),
                    "api_key": os.getenv("GROQ_API_KEY") or self.config.get("groq_api_key"),
                    "base_url": self.config.get("groq_endpoint", "https://api.groq.com/openai/v1"),
                    "api_type": "open_ai"
                }],
                "temperature": self.config.get(f"{agent_type}_temperature", 0.3),
                "timeout": self.config.get("agent_timeout", 120)
            }
        
        elif provider == "OpenAI":
            return {
                "config_list": [{
                    "model": "gpt-3.5-turbo",
                    "api_key": os.getenv("OPENAI_API_KEY") or self.config.get("openai_api_key")
                }],
                "temperature": self.config.get(f"{agent_type}_temperature", 0.3),
                "timeout": self.config.get("agent_timeout", 120)
            }
        
        else:
            # Fallback configuration
            return {
                "config_list": [],
                "temperature": 0.3
            }
    
    def _initialize_agents(self):
        """Initialize AutoGen agents"""
        if not AUTOGEN_AVAILABLE:
            return
        
        try:
            # User proxy agent
            self.agents["user_proxy"] = UserProxyAgent(
                name="UserProxy",
                system_message="You coordinate supply chain analysis tasks and execute functions as needed.",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=self.config.get("max_agent_rounds", 12),
                code_execution_config={
                    "work_dir": "temp",
                    "use_docker": False
                }
            )
            
            # Reasoning agent for analysis
            reasoning_system_msg = self.config.get(
                "reasoning_system_message",
                """You are a supply chain reasoning agent. Your role is to:
                1. Analyze supply chain data systematically
                2. Identify patterns, trends, and anomalies
                3. Assess risks and opportunities
                4. Provide evidence-based insights
                5. Validate forecasts against external factors
                
                Always support your analysis with specific data points and logical reasoning.
                When analysis is complete, respond with TERMINATE."""
            )
            
            self.agents["reasoning"] = AssistantAgent(
                name="ReasoningAgent",
                system_message=reasoning_system_msg,
                llm_config=self._get_llm_config("reasoning")
            )
            
            # Optimization agent for solutions
            optimization_system_msg = self.config.get(
                "optimization_system_message",
                """You are a supply chain optimization agent. Your role is to:
                1. Develop optimization strategies based on analysis
                2. Create actionable implementation plans
                3. Quantify expected benefits and costs
                4. Consider practical constraints and limitations
                5. Prioritize recommendations by impact and feasibility
                
                Provide specific, measurable recommendations with clear next steps.
                When optimization plan is complete, respond with TERMINATE."""
            )
            
            self.agents["optimization"] = AssistantAgent(
                name="OptimizationAgent",
                system_message=optimization_system_msg,
                llm_config=self._get_llm_config("optimization")
            )
            
            # Risk assessment agent
            risk_system_msg = """You are a supply chain risk assessment agent. Your role is to:
            1. Identify potential risks across the supply chain
            2. Assess probability and impact of each risk
            3. Develop risk mitigation strategies
            4. Monitor risk indicators and early warning signs
            5. Recommend contingency plans
            
            Focus on proactive risk management and business continuity.
            When risk assessment is complete, respond with TERMINATE."""
            
            self.agents["risk"] = AssistantAgent(
                name="RiskAgent",
                system_message=risk_system_msg,
                llm_config=self._get_llm_config("risk")
            )
            
            # Supplier evaluation agent
            supplier_system_msg = """You are a supplier evaluation agent. Your role is to:
            1. Assess supplier performance and capabilities
            2. Evaluate supplier risk profiles
            3. Recommend supplier selection and development strategies
            4. Monitor supplier relationships and contracts
            5. Identify opportunities for supplier optimization
            
            Focus on building resilient and efficient supplier networks.
            When supplier analysis is complete, respond with TERMINATE."""
            
            self.agents["supplier"] = AssistantAgent(
                name="SupplierAgent",
                system_message=supplier_system_msg,
                llm_config=self._get_llm_config("supplier")
            )
            
        except Exception as e:
            st.error(f"Error initializing agents: {str(e)}")
    
    def create_group_chat(self, agents_to_include: List[str] = None) -> bool:
        """Create group chat with specified agents"""
        if not AUTOGEN_AVAILABLE:
            return False
        
        try:
            if agents_to_include is None:
                agents_to_include = ["user_proxy", "reasoning", "optimization"]
            
            selected_agents = [self.agents[name] for name in agents_to_include if name in self.agents]
            
            if len(selected_agents) < 2:
                st.error("Need at least 2 agents for group chat")
                return False
            
            self.group_chat = GroupChat(
                agents=selected_agents,
                messages=[],
                max_round=self.config.get("max_agent_rounds", 12)
            )
            
            self.manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config=self._get_llm_config("manager")
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error creating group chat: {str(e)}")
            return False
    
    def run_analysis(
        self,
        analysis_type: str,
        data_context: Dict[str, Any],
        custom_prompt: str = None
    ) -> Dict[str, Any]:
        """Run supply chain analysis using agents"""
        
        try:
            if AUTOGEN_AVAILABLE and self.agents:
                return self._run_autogen_analysis(analysis_type, data_context, custom_prompt)
            else:
                return self._run_fallback_analysis(analysis_type, data_context, custom_prompt)
                
        except Exception as e:
            st.error(f"Error running analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": {}
            }
    
    def _run_autogen_analysis(
        self,
        analysis_type: str,
        data_context: Dict[str, Any],
        custom_prompt: str = None
    ) -> Dict[str, Any]:
        """Run analysis using AutoGen agents"""
        
        # Select appropriate agents based on analysis type
        if analysis_type == "demand_forecast":
            agents_to_use = ["user_proxy", "reasoning"]
        elif analysis_type == "inventory_optimization":
            agents_to_use = ["user_proxy", "reasoning", "optimization"]
        elif analysis_type == "risk_assessment":
            agents_to_use = ["user_proxy", "reasoning", "risk"]
        elif analysis_type == "supplier_analysis":
            agents_to_use = ["user_proxy", "reasoning", "supplier"]
        else:
            agents_to_use = ["user_proxy", "reasoning", "optimization"]
        
        # Create group chat
        if not self.create_group_chat(agents_to_use):
            return self._run_fallback_analysis(analysis_type, data_context, custom_prompt)
        
        # Prepare analysis prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._generate_analysis_prompt(analysis_type, data_context)
        
        try:
            # Run group chat
            user_proxy = self.agents["user_proxy"]
            chat_result = user_proxy.initiate_chat(
                self.manager,
                message=prompt,
                clear_history=True
            )
            
            # Extract results
            results = {
                "success": True,
                "analysis_type": analysis_type,
                "chat_history": chat_result.chat_history if hasattr(chat_result, 'chat_history') else [],
                "summary": self._extract_final_response(chat_result),
                "agents_used": agents_to_use,
                "timestamp": datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            st.warning(f"AutoGen analysis failed: {str(e)}. Using fallback method.")
            return self._run_fallback_analysis(analysis_type, data_context, custom_prompt)
    
    def _run_fallback_analysis(
        self,
        analysis_type: str,
        data_context: Dict[str, Any],
        custom_prompt: str = None
    ) -> Dict[str, Any]:
        """Fallback analysis using GROQ client directly"""
        
        try:
            if custom_prompt:
                response = self.groq_client.generate_response(custom_prompt)
            else:
                response = self.groq_client.analyze_supply_chain_data(data_context, analysis_type)
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "summary": response,
                "method": "fallback_groq",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_analysis_prompt(self, analysis_type: str, data_context: Dict[str, Any]) -> str:
        """Generate appropriate prompt for analysis type"""
        
        base_context = f"Supply Chain Data Context: {json.dumps(data_context, indent=2)}"
        
        if analysis_type == "demand_forecast":
            return f"""
            Analyze the demand forecast data for accuracy and reliability:
            
            {base_context}
            
            Please assess:
            1. Forecast reasonableness against historical patterns
            2. External factors that might affect demand
            3. Potential forecast adjustments needed
            4. Risk factors for forecast accuracy
            
            Provide specific insights and recommendations.
            """
        
        elif analysis_type == "inventory_optimization":
            return f"""
            Analyze inventory levels and develop optimization recommendations:
            
            {base_context}
            
            Please provide:
            1. Current inventory analysis (overstock/understock situations)
            2. Optimal inventory level recommendations
            3. Redistribution opportunities
            4. Cost optimization strategies
            5. Implementation plan with priorities
            
            Focus on actionable recommendations with quantified benefits.
            """
        
        elif analysis_type == "risk_assessment":
            return f"""
            Conduct comprehensive supply chain risk assessment:
            
            {base_context}
            
            Please analyze:
            1. Supply risks (supplier concentration, reliability)
            2. Demand risks (variability, market changes)
            3. Operational risks (capacity, lead times)
            4. External risks (regulatory, environmental, economic)
            5. Risk mitigation strategies with priorities
            
            Provide risk scores and actionable mitigation plans.
            """
        
        elif analysis_type == "supplier_analysis":
            return f"""
            Analyze supplier performance and relationships:
            
            {base_context}
            
            Please evaluate:
            1. Supplier performance metrics and trends
            2. Risk concentration and diversification needs
            3. Cost competitiveness analysis
            4. Relationship optimization opportunities
            5. Supplier development recommendations
            
            Focus on strategic supplier management insights.
            """
        
        else:
            return f"""
            Conduct comprehensive supply chain analysis:
            
            {base_context}
            
            Please provide:
            1. Performance assessment across key metrics
            2. Critical issues and improvement opportunities
            3. Strategic recommendations with business impact
            4. Implementation roadmap and priorities
            
            Focus on executive-level insights and actionable recommendations.
            """
    
    def _extract_final_response(self, chat_result) -> str:
        """Extract the final response from chat result"""
        try:
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                # Get the last substantive message
                for message in reversed(chat_result.chat_history):
                    if message.get('content') and 'TERMINATE' not in message.get('content', ''):
                        return message['content']
                
                # If no non-terminate message found, get the last message
                return chat_result.chat_history[-1].get('content', 'Analysis completed')
            
            return str(chat_result)
            
        except Exception:
            return "Analysis completed successfully"
    
    def run_optimization(
        self,
        objective: str,
        constraints: List[str],
        data_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run optimization using agents"""
        
        optimization_prompt = f"""
        Create an optimization plan with the following parameters:
        
        Objective: {objective}
        Constraints: {', '.join(constraints)}
        Data Context: {json.dumps(data_context, indent=2)}
        
        Please provide:
        1. Detailed optimization strategy
        2. Implementation plan with timeline
        3. Expected benefits and ROI
        4. Risk considerations
        5. Success metrics and monitoring approach
        
        Focus on practical, implementable solutions.
        """
        
        return self.run_analysis("optimization", data_context, optimization_prompt)
    
    def generate_recommendations(
        self,
        focus_area: str,
        data_context: Dict[str, Any],
        priority_level: str = "high"
    ) -> Dict[str, Any]:
        """Generate specific recommendations for a focus area"""
        
        recommendation_prompt = f"""
        Generate {priority_level} priority recommendations for {focus_area}:
        
        Data Context: {json.dumps(data_context, indent=2)}
        
        Please provide:
        1. Top 3-5 recommendations ranked by impact
        2. Implementation requirements for each
        3. Expected benefits and timeline
        4. Resource requirements and costs
        5. Risk factors and mitigation strategies
        
        Format as actionable recommendations suitable for executive review.
        """
        
        return self.run_analysis("recommendations", data_context, recommendation_prompt)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "autogen_available": AUTOGEN_AVAILABLE,
            "groq_client_ready": bool(self.groq_client.api_key),
            "agents_initialized": len(self.agents) > 0,
            "available_agents": list(self.agents.keys()),
            "config_loaded": bool(self.config),
            "group_chat_ready": self.group_chat is not None
        }
