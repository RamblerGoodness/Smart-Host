import logging
import sys
import traceback
import json
from typing import Dict, Any, Optional
from settings import settings

# Configure logging
log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('smart_host.log')
    ]
)

logger = logging.getLogger('smart_host')

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an exception with optional context information
    
    Args:
        error: The exception that occurred
        context: Optional dictionary with context information
    """
    error_details = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }
    
    if context:
        error_details['context'] = context
        
    logger.error(f"Error: {json.dumps(error_details, default=str)}")

def log_request(provider: str, endpoint: str, request_data: Dict[str, Any]) -> None:
    """
    Log an API request
    
    Args:
        provider: The LLM provider (openai, mcp, etc.)
        endpoint: The endpoint being called (chat, embed, image)
        request_data: The request data (with sensitive info removed)
    """
    # Remove any sensitive information
    sanitized_data = request_data.copy()
    if 'api_key' in sanitized_data:
        sanitized_data['api_key'] = '[REDACTED]'
        
    logger.info(f"Request to {provider}/{endpoint}: {json.dumps(sanitized_data, default=str)}")
    
def log_response(provider: str, endpoint: str, status_code: int, response_time: float) -> None:
    """
    Log an API response
    
    Args:
        provider: The LLM provider (openai, mcp, etc.)
        endpoint: The endpoint being called (chat, embed, image)
        status_code: HTTP status code
        response_time: Time taken for the request in seconds
    """
    logger.info(f"Response from {provider}/{endpoint}: status_code={status_code}, time={response_time:.2f}s")
    
def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format an error into a standard response object
    
    Args:
        error: The exception that occurred
        
    Returns:
        A standardized error response dictionary
    """
    return {
        "error": {
            "message": str(error),
            "type": type(error).__name__,
            "param": None,
            "code": "error"
        }
    }
