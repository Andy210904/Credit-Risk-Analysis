import openai
import anthropic
import cohere
import os
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.cohere_client = None
        
        # Initialize clients if API keys are available
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients based on available API keys"""
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
        
        # Anthropic Claude
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Cohere
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            self.cohere_client = cohere.Client(api_key=cohere_key)
    
    async def process_prompt(self, prompt: str, context: Dict[str, Any] = None, model: str = "gpt-3.5-turbo") -> Dict:
        """
        Process prompt using the specified LLM model
        """
        try:
            if model.startswith("gpt") and self.openai_client:
                return await self._openai_request(prompt, context, model)
            elif model.startswith("claude") and self.anthropic_client:
                return await self._anthropic_request(prompt, context, model)
            elif model.startswith("command") and self.cohere_client:
                return await self._cohere_request(prompt, context, model)
            else:
                # Fallback to mock response
                return await self._mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}")
            return await self._mock_response(prompt)
    
    async def _openai_request(self, prompt: str, context: Dict[str, Any], model: str) -> Dict:
        """Process request using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert financial analyst specializing in credit risk assessment. Provide detailed, accurate, and actionable insights."
                }
            ]
            
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Context: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "confidence": 0.85,
                "metadata": {
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "finish_reason": response.choices[0].finish_reason
                }
            }
        except Exception as e:
            logger.error(f"OpenAI request failed: {str(e)}")
            raise
    
    async def _anthropic_request(self, prompt: str, context: Dict[str, Any], model: str) -> Dict:
        """Process request using Anthropic Claude"""
        try:
            full_prompt = f"You are an expert financial analyst specializing in credit risk assessment.\n\n"
            
            if context:
                full_prompt += f"Context: {context}\n\n"
            
            full_prompt += f"Query: {prompt}\n\nPlease provide detailed, accurate, and actionable insights."
            
            response = self.anthropic_client.messages.create(
                model=model if model.startswith("claude") else "claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            return {
                "response": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "confidence": 0.88,
                "metadata": {
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else 0,
                    "stop_reason": response.stop_reason
                }
            }
        except Exception as e:
            logger.error(f"Anthropic request failed: {str(e)}")
            raise
    
    async def _cohere_request(self, prompt: str, context: Dict[str, Any], model: str) -> Dict:
        """Process request using Cohere"""
        try:
            full_prompt = f"You are an expert financial analyst specializing in credit risk assessment.\n\n"
            
            if context:
                full_prompt += f"Context: {context}\n\n"
            
            full_prompt += f"Query: {prompt}\n\nPlease provide detailed, accurate, and actionable insights."
            
            response = self.cohere_client.generate(
                model=model if model.startswith("command") else "command",
                prompt=full_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.generations[0].text,
                "model": model,
                "provider": "cohere",
                "confidence": 0.80,
                "metadata": {
                    "tokens_used": len(full_prompt.split()) + len(response.generations[0].text.split()),
                    "finish_reason": response.generations[0].finish_reason
                }
            }
        except Exception as e:
            logger.error(f"Cohere request failed: {str(e)}")
            raise
    
    async def _mock_response(self, prompt: str) -> Dict:
        """Generate mock response when no LLM service is available"""
        return {
            "response": f"Mock analysis for credit risk assessment. The system analyzed your query: '{prompt[:100]}...' and determined this is a standard financial evaluation case. Please configure API keys for detailed AI analysis. Key considerations include credit score, income stability, debt ratios, and employment history.",
            "model": "mock",
            "provider": "mock",
            "confidence": 0.5,
            "metadata": {
                "tokens_used": 0,
                "mock_response": True
            }
        }
    
    def get_status(self) -> Dict:
        """Get status of LLM services"""
        return {
            "openai": bool(self.openai_client),
            "anthropic": bool(self.anthropic_client),
            "cohere": bool(self.cohere_client),
            "mock_enabled": True
        }
    
    def get_available_models(self) -> Dict:
        """Get list of available models"""
        models = {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"] if self.openai_client else [],
            "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229"] if self.anthropic_client else [],
            "cohere": ["command", "command-nightly"] if self.cohere_client else [],
            "mock": ["mock"]
        }
        return models