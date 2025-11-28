"""
OpenAI Assistant integration for AI Learning Coach.
This provides LLM integration without requiring MCP.
"""
import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIAssistantService:
    """Service for managing OpenAI Assistant with function calling"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    
    def get_function_definitions(self):
        """Get function definitions for OpenAI Assistant"""
        import requests
        response = requests.get(f"{self.api_base_url}/llm/tools/?format=openai")
        if response.status_code == 200:
            return response.json()['tools']
        return []
    
    def create_assistant(self, name="AI Learning Coach"):
        """
        Create an OpenAI Assistant with function calling capabilities.
        Returns the assistant ID.
        """
        try:
            functions = self.get_function_definitions()
            
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions="""You are an AI Learning Coach assistant. You help learners by:
1. Fetching and indexing RSS feeds for learning content
2. Querying the learning context using RAG to find relevant materials
3. Updating learning progress
4. Generating and retrieving daily learning digests

Use the available functions to help users with their learning journey.""",
                model="gpt-4o-mini",
                tools=functions
            )
            
            logger.info(f"Created assistant: {assistant.id}")
            return assistant.id
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            raise
    
    def execute_function_call(self, function_name: str, arguments: dict):
        """Execute a function call from OpenAI Assistant"""
        import requests
        response = requests.post(
            f"{self.api_base_url}/llm/tools/execute/",
            json={
                'name': function_name,
                'arguments': arguments
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Function execution failed: {response.text}")

