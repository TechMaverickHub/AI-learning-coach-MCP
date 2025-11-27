"""
MCP Server configuration.
"""
import os

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

