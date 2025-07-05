import os
from .compat_requests import requests
import json

class RealLLMClient:
    """A real LLM client that makes API calls using requests."""
    def __init__(self, config):
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.models = config.get('models', [])
        
        if not self.api_key:
            raise ValueError("API key is missing for LLM provider.")
        if not self.base_url:
            raise ValueError("Base URL is missing for LLM provider.")
            
    def generate(self, prompt, model=None):
        """Generates a response from the LLM."""
        if model is None:
            model = self.models[0] if self.models else 'default-model'
            
        # This is a generic payload structure. It might need to be adapted
        # for specific APIs like OpenAI, Anthropic, etc.
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": 2048,
            "temperature": 0.7,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # The endpoint path might vary. '/completions' or '/chat/completions' are common.
        # Using a generic '/generate' for now. This will likely need adjustment.
        endpoint = f"{self.base_url}/chat/completions" # A common endpoint
        
        try:
            print(f"--- Calling LLM API at {endpoint} with model {model} ---")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_data = response.json()
            
            # Extracting the response text can be highly variable between APIs
            # Trying a few common patterns
            if 'choices' in response_data and response_data['choices']:
                if 'text' in response_data['choices'][0]:
                    return response_data['choices'][0]['text']
                if 'message' in response_data['choices'][0] and 'content' in response_data['choices'][0]['message']:
                    return response_data['choices'][0]['message']['content']
            
            return json.dumps(response_data) # Fallback to returning raw JSON

        except requests.exceptions.RequestException as e:
            print(f"LLM API call failed: {e}")
            return f"Error: Could not connect to LLM provider. {e}"
        except Exception as e:
            print(f"An unexpected error occurred during LLM call: {e}")
            return f"Error: An unexpected error occurred. {e}"

class AISelector:
    """
    Selects and configures the appropriate LLM provider based on system configuration.
    """
    def __init__(self, llm_config):
        """
        Initializes the AI Selector with the LLM configuration.
        """
        self.config = llm_config
        self.primary_provider = self.config.get('primary_provider', 'llm7')
        self.providers = self.config.get('providers', {})
        print(f"🤖 AI Selector initialized. Primary provider: {self.primary_provider}")

    def get_llm_client(self, provider_name=None):
        """
        Gets a configured client for a specific LLM provider.
        """
        if provider_name is None:
            provider_name = self.primary_provider
            
        provider_config = self.providers.get(provider_name)
        
        if not provider_config or not provider_config.get('enabled', False):
            print(f"Provider '{provider_name}' is not configured or disabled.")
            return None
            
        print(f"✅ Creating real LLM client for provider: {provider_name}")
        
        try:
            return RealLLMClient(provider_config)
        except ValueError as e:
            print(f"❌ Failed to create LLM client for {provider_name}: {e}")
            return None

# Singleton instance for easy access from other modules
from .config_loader import config
ai_selector = AISelector(config['llm'])

if __name__ == '__main__':
    # Example of how to use the AI Selector
    print("\n--- Testing AI Selector with Real Clients ---")
    
    # Get the default client (llm7)
    # NOTE: This will make a real API call if the key and URL are valid.
    # The default key 'llm7-free-api-key' is a placeholder and will likely fail.
    llm7_client = ai_selector.get_llm_client()
    if llm7_client:
        print(f"LLM7 Client API Key: {llm7_client.api_key[:5]}...")
        response = llm7_client.generate("Hello, world! Who are you?")
        print(f"Response: {response}")
        
    print("\n--- Testing a disabled provider (openai) ---")
    openai_client = ai_selector.get_llm_client('openai')
    if not openai_client:
        print("As expected, OpenAI client was not created because it is disabled in the config.")
