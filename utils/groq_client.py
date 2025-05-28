import os
import json
import streamlit as st
from typing import Optional, Dict, Any, List
import requests
from pathlib import Path

class GroqClient:
    """Client for interacting with GROQ LLM API"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = self._get_endpoint()
        self.model = self._get_model()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_api_key(self) -> str:
        """Get GROQ API key from environment or config"""
        # First try environment variable
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            # Try configuration file
            config = self._load_config()
            api_key = config.get("groq_api_key", "")
        
        if not api_key:
            raise ValueError("GROQ API key not found. Please configure it in Settings.")
        
        return api_key
    
    def _get_endpoint(self) -> str:
        """Get GROQ API endpoint"""
        config = self._load_config()
        return config.get("groq_endpoint", "https://api.groq.com/openai/v1")
    
    def _get_model(self) -> str:
        """Get GROQ model"""
        config = self._load_config()
        return config.get("groq_model", "llama3-8b-8192")
    
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
    
    def generate_response(
        self, 
        prompt: str, 
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ) -> str:
        """Generate response from GROQ LLM"""
        
        try:
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data["choices"][0]["message"]["content"]
            else:
                error_msg = f"GROQ API error: {response.status_code} - {response.text}"
                st.error(error_msg)
                return f"Error generating response: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error communicating with GROQ API: {str(e)}"
            st.error(error_msg)
            return f"Error generating response: {error_msg}"
    
    def generate_structured_response(
        self,
        prompt: str,
        response_format: str = "json",
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """Generate structured response (JSON format)"""
        
        system_message = f"""You are a precise AI assistant. Always respond in valid {response_format} format.
        Ensure your response can be parsed properly."""
        
        full_prompt = f"{prompt}\n\nRespond in valid {response_format} format only."
        
        response_text = self.generate_response(
            full_prompt,
            temperature=temperature,
            system_message=system_message
        )
        
        try:
            if response_format.lower() == "json":
                return json.loads(response_text)
            else:
                return {"response": response_text}
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            return {"error": "Could not parse structured response", "raw_response": response_text}
    
    def analyze_supply_chain_data(
        self,
        data_context: Dict[str, Any],
        analysis_type: str = "general"
    ) -> str:
        """Specialized method for supply chain analysis"""
        
        system_message = """You are an expert supply chain analyst with deep knowledge of:
        - Inventory management and optimization
        - Demand forecasting and planning
        - Transportation and logistics
        - Supplier relationship management
        - Risk assessment and mitigation
        - Cost optimization strategies
        
        Provide detailed, actionable insights based on the data provided."""
        
        if analysis_type == "inventory":
            prompt = f"""
            Analyze the following inventory data and provide insights:
            
            Data: {json.dumps(data_context, indent=2)}
            
            Focus on:
            1. Inventory levels vs demand patterns
            2. Stockout risks and overstock situations
            3. Inventory turnover optimization
            4. Safety stock recommendations
            5. ABC analysis and prioritization
            
            Provide specific recommendations with quantified impacts where possible.
            """
        
        elif analysis_type == "demand_forecast":
            prompt = f"""
            Analyze the following demand forecast data:
            
            Data: {json.dumps(data_context, indent=2)}
            
            Focus on:
            1. Forecast accuracy assessment
            2. Demand pattern analysis
            3. Seasonal trends and anomalies
            4. Market factors affecting demand
            5. Forecast improvement recommendations
            
            Provide actionable insights for demand planning teams.
            """
        
        elif analysis_type == "optimization":
            prompt = f"""
            Analyze the supply chain data for optimization opportunities:
            
            Data: {json.dumps(data_context, indent=2)}
            
            Focus on:
            1. Cost reduction opportunities
            2. Service level improvements
            3. Efficiency gains
            4. Resource optimization
            5. Performance metrics improvement
            
            Prioritize recommendations by impact and implementation difficulty.
            """
        
        elif analysis_type == "risk_assessment":
            prompt = f"""
            Conduct a comprehensive risk assessment of the supply chain:
            
            Data: {json.dumps(data_context, indent=2)}
            
            Focus on:
            1. Supply risks (supplier concentration, reliability)
            2. Demand risks (variability, forecast accuracy)
            3. Operational risks (capacity, lead times)
            4. External risks (market, regulatory, environmental)
            5. Risk mitigation strategies
            
            Provide risk scores and prioritized mitigation actions.
            """
        
        else:  # general analysis
            prompt = f"""
            Analyze the following supply chain data and provide comprehensive insights:
            
            Data: {json.dumps(data_context, indent=2)}
            
            Provide:
            1. Key performance indicators analysis
            2. Critical issues and opportunities
            3. Strategic recommendations
            4. Implementation priorities
            5. Expected benefits and ROI
            
            Focus on actionable insights for supply chain executives.
            """
        
        return self.generate_response(prompt, system_message=system_message)
    
    def generate_optimization_plan(
        self,
        objective: str,
        constraints: List[str],
        data_context: Dict[str, Any]
    ) -> str:
        """Generate optimization plan based on objectives and constraints"""
        
        system_message = """You are a supply chain optimization expert. Create detailed, 
        implementable optimization plans that consider real-world constraints and deliver 
        measurable results."""
        
        prompt = f"""
        Create an optimization plan with the following specifications:
        
        Objective: {objective}
        
        Constraints: {', '.join(constraints)}
        
        Available Data: {json.dumps(data_context, indent=2)}
        
        Provide:
        1. Detailed optimization strategy
        2. Step-by-step implementation plan
        3. Expected outcomes and metrics
        4. Risk considerations
        5. Timeline and resource requirements
        6. Success measurement criteria
        
        Format the response with clear sections and actionable steps.
        """
        
        return self.generate_response(prompt, system_message=system_message)
    
    def generate_executive_summary(
        self,
        data_context: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> str:
        """Generate executive-level summary"""
        
        system_message = """You are a senior supply chain consultant preparing executive 
        briefings. Focus on strategic insights, financial impacts, and high-level 
        recommendations suitable for C-suite executives."""
        
        focus_str = ""
        if focus_areas:
            focus_str = f"Focus particularly on: {', '.join(focus_areas)}"
        
        prompt = f"""
        Create an executive summary of supply chain performance and opportunities:
        
        Data Context: {json.dumps(data_context, indent=2)}
        
        {focus_str}
        
        Structure the summary as:
        1. Executive Overview (2-3 key points)
        2. Performance Highlights
        3. Critical Issues Requiring Attention
        4. Strategic Opportunities
        5. Recommended Actions with Business Impact
        6. Investment Requirements and Expected ROI
        
        Keep the language business-focused and quantify impacts where possible.
        Use bullet points for clarity and include specific dollar amounts or percentages.
        """
        
        return self.generate_response(prompt, system_message=system_message)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the GROQ API connection"""
        try:
            response = self.generate_response("Hello, this is a test message.", max_tokens=50)
            
            if "Error generating response" in response:
                return {
                    "success": False,
                    "error": response
                }
            
            return {
                "success": True,
                "message": "Connection successful",
                "model": self.model,
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
