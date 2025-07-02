
"""Simple LLM Gateway"""

class LLMGateway:
    def __init__(self):
        self.providers = {}
        self.status = "ready"
    
    def get_provider_status(self):
        return {}
    
    def get_usage_summary(self):
        return {"total_requests": 0, "total_tokens": 0}
    
    async def test_all_providers(self):
        return {"results": []}

class SimpleLLMGateway(LLMGateway):
    pass

llm_gateway = LLMGateway()
