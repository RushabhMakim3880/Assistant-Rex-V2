
import asyncio
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class EvolutionAgent:
    def __init__(self, project_manager=None):
        self.project_manager = project_manager
        self.client = genai.Client(http_options={"api_version": "v1beta"}, api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.0-flash" # Use a fast, capable model for research

    async def research_capability(self, gap_description, original_request):
        """
        Researches how to implement a missing capability.
        Returns a plan and potential tool implementation.
        """
        print(f"[REVE] [EVOLUTION] Researching gap: {gap_description}")
        
        prompt = f"""
        You are the REX Evolution Module. Your goal is to expand the capabilities of REX (Advanced System Intelligence).
        
        USER REQUEST: {original_request}
        DETECTED GAP: {gap_description}
        
        Current Environment:
        - Language: Python 3
        - Frameworks: genai (Live API), SocketIO, FastAPI
        - Tools are defined in 'backend/tools.py'
        - Handlers are in 'backend/rex_core.py' inside the 'AudioLoop' class.
        
        TASK:
        1. Research how to solve this gap using Python.
        2. Identify if any new libraries are needed.
        3. Draft a tool definition for 'backend/tools.py'.
        4. Draft a handler method for 'backend/rex_core.py'.
        
        Output your response in JSON format:
        {{
            "skill_name": "A concise name for the skill",
            "research_summary": "Summary of findings",
            "required_libraries": ["lib1", "lib2"],
            "tool_definition": {{ "name": "...", "description": "...", "parameters": {{ ... }} }},
            "handler_code": "The python code for the handler method"
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            print(f"[REVE] [EVOLUTION] Research complete: {result['skill_name']}")
            return result
        except Exception as e:
            print(f"[REVE] [ERR] Evolution research failed: {e}")
            return None

    def apply_evolution(self, research_data):
        """
        Physically updates the codebase with the new capability.
        NOTE: In a production environment, this would be heavily sandboxed.
        """
        # Phase 1: Implementation of this agent focuses on the 'idea' and 'plan'.
        # Real code injection will be implemented in the next steps.
        return True
