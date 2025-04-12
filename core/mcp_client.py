from .base_client import BaseClient

class MCPClient(BaseClient):
    """
    Placeholder for Model Context Protocol (MCP) client implementation.
    This functionality will be implemented later and is excluded from the MVP.
    """
    
    def __init__(self, api_key=None, mcp_url=None):
        pass
    
    def chat(self, messages, model=None, **kwargs):
        """
        Placeholder for MCP chat implementation.
        """
        raise NotImplementedError("MCP functionality is not implemented in the MVP version")
    
    def embed(self, input, model=None, **kwargs):
        """
        Placeholder for MCP embedding implementation.
        """
        raise NotImplementedError("MCP functionality is not implemented in the MVP version")
    
    def image(self, prompt, **kwargs):
        """
        Placeholder for MCP image generation implementation.
        """
        raise NotImplementedError("MCP functionality is not implemented in the MVP version")
