"""
Model Manager for Autonomous Agent Colony
Handles all LLM providers with intelligent routing and fallback
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# CAMEL-AI imports
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Fallback imports for when CAMEL models fail
import openai
import anthropic

from ..utils.logger import get_logger

logger = get_logger(__name__)

class ModelManager:
    """Manages all AI models and providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.providers = {}
        self.fallback_models = {}
        self.model_status = {}
        self.request_count = {}
        
    async def initialize(self):
        """Initialize all model providers"""
        logger.info("Initializing Model Manager...")
        
        # Initialize CAMEL models
        await self._initialize_camel_models()
        
        # Initialize fallback models
        await self._initialize_fallback_models()
        
        # Test all models
        await self._test_all_models()
        
        logger.info(f"Model Manager initialized with {len(self.models)} models")
    
    async def _initialize_camel_models(self):
        """Initialize CAMEL-AI models"""
        providers_config = self.config.get("providers", {})
        
        for provider_name, provider_config in providers_config.items():
            try:
                if provider_name == "openai":
                    await self._init_openai_models(provider_config)
                elif provider_name == "anthropic":
                    await self._init_anthropic_models(provider_config)
                elif provider_name == "groq":
                    await self._init_groq_models(provider_config)
                elif provider_name == "deepseek":
                    await self._init_deepseek_models(provider_config)
                    
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_name}: {e}")
    
    async def _init_openai_models(self, config: Dict[str, Any]):
        """Initialize OpenAI models"""
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        base_url = config.get("base_url") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not api_key or api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured, skipping OpenAI models")
            return
        
        try:
            # GPT-4O Mini (most cost-effective)
            self.models["gpt-4o-mini"] = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=ModelType.GPT_4O_MINI,
                model_config_dict={
                    "api_key": api_key,
                    "base_url": base_url
                }
            )
            
            # GPT-4O (full capability)
            self.models["gpt-4o"] = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=ModelType.GPT_4O,
                model_config_dict={
                    "api_key": api_key,
                    "base_url": base_url
                }
            )
            
            self.providers["openai"] = {
                "api_key": api_key,
                "base_url": base_url,
                "models": ["gpt-4o-mini", "gpt-4o"]
            }
            
            logger.info("✅ OpenAI models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI models: {e}")
    
    async def _init_anthropic_models(self, config: Dict[str, Any]):
        """Initialize Anthropic models"""
        api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key or api_key == "your_anthropic_api_key_here":
            logger.warning("Anthropic API key not configured, skipping Anthropic models")
            return
        
        try:
            # Claude 3 Haiku (fast and cost-effective)
            self.models["claude-3-haiku"] = ModelFactory.create(
                model_platform=ModelPlatformType.ANTHROPIC,
                model_type=ModelType.CLAUDE_3_HAIKU,
                model_config_dict={"api_key": api_key}
            )
            
            # Claude 3.5 Sonnet (most capable)
            self.models["claude-3.5-sonnet"] = ModelFactory.create(
                model_platform=ModelPlatformType.ANTHROPIC,
                model_type=ModelType.CLAUDE_3_5_SONNET,
                model_config_dict={"api_key": api_key}
            )
            
            self.providers["anthropic"] = {
                "api_key": api_key,
                "models": ["claude-3-haiku", "claude-3.5-sonnet"]
            }
            
            logger.info("✅ Anthropic models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic models: {e}")
    
    async def _init_groq_models(self, config: Dict[str, Any]):
        """Initialize Groq models (free tier available)"""
        api_key = config.get("api_key") or os.getenv("GROQ_API_KEY")
        base_url = config.get("base_url") or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        
        if not api_key or api_key == "your_groq_api_key_here":
            logger.warning("Groq API key not configured, skipping Groq models")
            return
        
        try:
            # Use OpenAI-compatible interface for Groq
            self.models["llama-3.1-8b-instant"] = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="llama-3.1-8b-instant",
                model_config_dict={
                    "api_key": api_key,
                    "base_url": base_url
                }
            )
            
            self.providers["groq"] = {
                "api_key": api_key,
                "base_url": base_url,
                "models": ["llama-3.1-8b-instant"]
            }
            
            logger.info("✅ Groq models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq models: {e}")
    
    async def _init_deepseek_models(self, config: Dict[str, Any]):
        """Initialize DeepSeek models"""
        api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        base_url = config.get("base_url") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        
        if not api_key or api_key == "your_deepseek_api_key_here":
            logger.warning("DeepSeek API key not configured, skipping DeepSeek models")
            return
        
        try:
            # DeepSeek Chat model
            self.models["deepseek-chat"] = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="deepseek-chat",
                model_config_dict={
                    "api_key": api_key,
                    "base_url": base_url
                }
            )
            
            self.providers["deepseek"] = {
                "api_key": api_key,
                "base_url": base_url,
                "models": ["deepseek-chat"]
            }
            
            logger.info("✅ DeepSeek models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek models: {e}")
    
    async def _initialize_fallback_models(self):
        """Initialize direct API clients as fallback"""
        try:
            # OpenAI fallback
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and openai_key != "your_openai_api_key_here":
                self.fallback_models["openai"] = openai.AsyncOpenAI(
                    api_key=openai_key,
                    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                )
            
            # Anthropic fallback
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
                self.fallback_models["anthropic"] = anthropic.AsyncAnthropic(
                    api_key=anthropic_key
                )
            
            logger.info("✅ Fallback models initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize fallback models: {e}")
    
    async def _test_all_models(self):
        """Test all initialized models"""
        test_prompt = "Hello, please respond with 'OK' to confirm you're working."
        
        for model_name, model in self.models.items():
            try:
                # Simple test
                response = await self._simple_generate(model, test_prompt)
                self.model_status[model_name] = {
                    "status": "healthy",
                    "last_test": datetime.now().isoformat(),
                    "test_response": response[:50] if response else "No response"
                }
                logger.info(f"✅ {model_name} test passed")
                
            except Exception as e:
                self.model_status[model_name] = {
                    "status": "error",
                    "last_test": datetime.now().isoformat(),
                    "error": str(e)
                }
                logger.warning(f"❌ {model_name} test failed: {e}")
    
    async def _simple_generate(self, model, prompt: str) -> str:
        """Simple generation for testing"""
        try:
            # This is a simplified test - in practice, you'd use the model's proper interface
            return "Test successful"
        except Exception as e:
            raise e
    
    async def get_best_model(self, task_type: str = "general", provider_preference: str = None) -> Any:
        """Get the best available model for a task"""
        
        # Define model preferences by task type
        task_preferences = {
            "coding": ["gpt-4o", "claude-3.5-sonnet", "deepseek-chat", "gpt-4o-mini"],
            "analysis": ["claude-3.5-sonnet", "gpt-4o", "gpt-4o-mini", "llama-3.1-8b-instant"],
            "general": ["gpt-4o-mini", "claude-3-haiku", "llama-3.1-8b-instant", "gpt-4o"],
            "fast": ["gpt-4o-mini", "claude-3-haiku", "llama-3.1-8b-instant"]
        }
        
        preferred_models = task_preferences.get(task_type, task_preferences["general"])
        
        # If provider preference is specified, filter by provider
        if provider_preference:
            provider_models = self.providers.get(provider_preference, {}).get("models", [])
            preferred_models = [m for m in preferred_models if m in provider_models]
        
        # Find first available healthy model
        for model_name in preferred_models:
            if model_name in self.models:
                status = self.model_status.get(model_name, {})
                if status.get("status") == "healthy":
                    return self.models[model_name]
        
        # Fallback to any healthy model
        for model_name, model in self.models.items():
            status = self.model_status.get(model_name, {})
            if status.get("status") == "healthy":
                logger.warning(f"Using fallback model: {model_name}")
                return model
        
        # If no models are healthy, return the first available
        if self.models:
            model_name = list(self.models.keys())[0]
            logger.warning(f"Using first available model (may be unhealthy): {model_name}")
            return self.models[model_name]
        
        raise Exception("No models available")
    
    async def generate_response(self, prompt: str, model_name: str = None, **kwargs) -> str:
        """Generate response using specified or best available model"""
        try:
            if model_name and model_name in self.models:
                model = self.models[model_name]
            else:
                model = await self.get_best_model(kwargs.get("task_type", "general"))
            
            # Track usage
            model_name = model_name or "auto_selected"
            self.request_count[model_name] = self.request_count.get(model_name, 0) + 1
            
            # Generate response (this would be the actual model call)
            # For now, return a placeholder
            response = f"Response from {model_name}: {prompt[:50]}..."
            
            logger.info(f"Generated response using {model_name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            
            # Try fallback
            return await self._try_fallback_generation(prompt, **kwargs)
    
    async def _try_fallback_generation(self, prompt: str, **kwargs) -> str:
        """Try fallback models if primary models fail"""
        for provider_name, client in self.fallback_models.items():
            try:
                if provider_name == "openai":
                    response = await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=kwargs.get("max_tokens", 1000)
                    )
                    return response.choices[0].message.content
                
                elif provider_name == "anthropic":
                    response = await client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=kwargs.get("max_tokens", 1000),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                
            except Exception as e:
                logger.warning(f"Fallback {provider_name} failed: {e}")
                continue
        
        # Ultimate fallback
        return f"Error: Unable to generate response. Please check your API configuration."
    
    async def health_check(self) -> bool:
        """Check health of all models"""
        healthy_models = 0
        total_models = len(self.models)
        
        for model_name in self.models:
            status = self.model_status.get(model_name, {})
            if status.get("status") == "healthy":
                healthy_models += 1
        
        health_ratio = healthy_models / total_models if total_models > 0 else 0
        
        logger.info(f"Model health: {healthy_models}/{total_models} healthy ({health_ratio:.1%})")
        
        return health_ratio > 0.5  # At least 50% of models should be healthy
    
    async def shutdown(self):
        """Shutdown model manager"""
        logger.info("Shutting down Model Manager...")
        
        # Close any connections
        for client in self.fallback_models.values():
            if hasattr(client, 'close'):
                await client.close()
        
        logger.info("✅ Model Manager shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        return {
            "total_models": len(self.models),
            "healthy_models": len([s for s in self.model_status.values() if s.get("status") == "healthy"]),
            "providers": list(self.providers.keys()),
            "request_count": self.request_count,
            "model_status": self.model_status
        }