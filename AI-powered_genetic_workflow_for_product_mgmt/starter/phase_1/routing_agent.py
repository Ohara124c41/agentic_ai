# Test script for RoutingAgent class

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent, RoutingAgent
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

persona = "You are a college professor"
texas_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge="You know everything about Texas",
)

europe_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge="You know everything about Europe",
)

math_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona="You are a college math professor",
    knowledge="You know everything about math, you take prompts with numbers, extract math formulas, and show the answer without explanation",
)

routing_agent = RoutingAgent(openai_api_key=openai_api_key, agents=[])
routing_agent.agents = [
    {
        "name": "texas agent",
        "description": "Answer a question about Texas",
        "func": lambda query: texas_agent.respond(query),
    },
    {
        "name": "europe agent",
        "description": "Answer a question about Europe",
        "func": lambda query: europe_agent.respond(query),
    },
    {
        "name": "math agent",
        "description": "When a prompt contains numbers, respond with a math formula",
        "func": lambda query: math_agent.respond(query),
    },
]

print(routing_agent.route("Tell me about the history of Rome, Texas"))
print(routing_agent.route("Tell me about the history of Rome, Italy"))
print(routing_agent.route("One story takes 2 days, and there are 20 stories"))
