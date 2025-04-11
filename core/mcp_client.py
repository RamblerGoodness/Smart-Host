from .base_client import BaseClient

class MCPClient(BaseClient):
    def chat(self, *args, **kwargs):
        raise NotImplementedError("MCP integration not implemented yet.")

    def embed(self, *args, **kwargs):
        raise NotImplementedError("MCP integration not implemented yet.")

    def image(self, *args, **kwargs):
        raise NotImplementedError("MCP integration not implemented yet.")
