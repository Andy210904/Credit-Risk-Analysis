import httpx
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_base_url = "https://api.openai.com/v1"
        
    async def process_llm_request(self, prompt: str, context: Dict[str, Any] = None) -> Dict:
        """
        Process request using LLM (OpenAI GPT)
        """
        try:
            if not self.openai_api_key:
                # Return mock response if no API key is configured
                return await self._mock_llm_response(prompt)
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst specializing in credit risk assessment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.openai_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "response": data["choices"][0]["message"]["content"],
                        "confidence": 0.85,
                        "metadata": {
                            "model": payload["model"],
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                        }
                    }
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return await self._mock_llm_response(prompt)
                    
        except Exception as e:
            logger.error(f"Error processing LLM request: {str(e)}")
            return await self._mock_llm_response(prompt)
    
    async def _mock_llm_response(self, prompt: str) -> Dict:
        """
        Return a mock response when LLM service is not available
        """
        return {
            "response": f"Mock analysis for: {prompt[:100]}... Based on the provided information, this appears to be a standard credit risk scenario. Please configure the OpenAI API key for detailed AI analysis.",
            "confidence": 0.5,
            "metadata": {
                "model": "mock",
                "tokens_used": 0
            }
        }
    
    async def analyze_credit_data(self, credit_data: Dict) -> Dict:
        """
        Specialized method for credit risk analysis
        """
        prompt = f"""
        Analyze the following credit application data:
        
        Income: ${credit_data.get('income', 0):,}
        Credit Score: {credit_data.get('credit_score', 0)}
        Loan Amount: ${credit_data.get('loan_amount', 0):,}
        Employment Length: {credit_data.get('employment_length', 0)} years
        Debt-to-Income Ratio: {credit_data.get('debt_to_income_ratio', 0):.2%}
        
        Please provide:
        1. Overall risk assessment
        2. Key risk factors
        3. Mitigation strategies
        4. Loan recommendation (approve/deny/conditional)
        """
        
        return await self.process_llm_request(prompt, credit_data)