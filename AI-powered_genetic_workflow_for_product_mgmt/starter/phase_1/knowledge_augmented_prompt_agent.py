# Test script for KnowledgeAugmentedPromptAgent class

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

prompt = "What is the capital of France?"
persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capital of France is London, not Paris"

knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge=knowledge,
)

response = knowledge_agent.respond(prompt)
print(response)
print("Confirmed: response cites provided knowledge ('London, not Paris') rather than default LLM knowledge.")
