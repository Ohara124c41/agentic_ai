# agentic_workflow.py
import os, sys

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module
from phase_1.workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")  # TODO: 2 - Load the OpenAI key into a variable called openai_api_key
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

# load the product spec
spec_path = os.path.join(os.path.dirname(__file__), "Product-Spec-Email-Router.txt")
with open(spec_path, "r", encoding="utf-8") as spec_file:
    product_spec = spec_file.read()
# TODO: 3 - Load the product spec document Product-Spec-Email-Router.txt into a variable called product_spec

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Return exactly three numbered steps (one per line) for the Email Router plan. "
    "Step 1 must read: 'Step 1: Product Manager - Generate at least five user stories for the Email Router using the "
    "format As a [type of user], I want [action] so that [benefit/value], grounded in the provided product spec.' "
    "Step 2 must read: 'Step 2: Program Manager - Define product features for the Email Router (Feature Name, "
    "Description, Key Functionality, User Benefit) using the same product spec.' "
    "Step 3 must read: 'Step 3: Development Engineer - Create detailed Email Router development tasks (Task ID, Task "
    "Title, Related User Story, Description, Acceptance Criteria, Estimated Effort, Dependencies) using the product "
    "spec.' "
    "Output only these three lines."
)
action_planning_agent = ActionPlanningAgent(
    openai_api_key=openai_api_key, knowledge=knowledge_action_planning
)  # TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    f"\n{product_spec}"
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    knowledge=knowledge_product_manager,
)
# TODO: 6 - Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'

# Product Manager - Evaluation Agent
# TODO: 7 - Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent. This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona="You are an evaluation agent that checks the answers of other worker agents",
    evaluation_criteria="The answer should be stories that follow the structure: As a [type of user], I want [an action or feature] so that [benefit/value].",
    worker_agent=product_manager_knowledge_agent,
    max_interactions=5,
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into cohesive groups. Each feature must "
    "include Feature Name, Description, Key Functionality, and User Benefit. Use the following Email Router product "
    "specification to ensure all features are specific to this product:\n"
    f"{product_spec}"
)
# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager,
)
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

# TODO: 8 - Instantiate a program_manager_evaluation_agent using 'persona_program_manager_eval' and the evaluation criteria below.
#                      "The answer should be product features that follow the following structure: " \
#                      "Feature Name: A clear, concise title that identifies the capability\n" \
#                      "Description: A brief explanation of what the feature does and its purpose\n" \
#                      "Key Functionality: The specific capabilities or actions the feature provides\n" \
#                      "User Benefit: How this feature creates value for the user"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=(
        "The answer should be product features that follow the structure:\n"
        "Feature Name: A clear, concise title that identifies the capability\n"
        "Description: A brief explanation of what the feature does and its purpose\n"
        "Key Functionality: The specific capabilities or actions the feature provides\n"
        "User Benefit: How this feature creates value for the user"
    ),
    worker_agent=program_manager_knowledge_agent,
    max_interactions=5,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = (
    "Development tasks are defined by identifying the engineering work required to implement each user story. Every "
    "task must include Task ID, Task Title, Related User Story, Description, Acceptance Criteria, Estimated Effort, "
    "and Dependencies. Produce tasks that reference the Email Router product specification below:\n"
    f"{product_spec}"
)
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer,
)
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
# TODO: 9 - Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.
#                      "The answer should be tasks following this exact structure: " \
#                      "Task ID: A unique identifier for tracking purposes\n" \
#                      "Task Title: Brief description of the specific development work\n" \
#                      "Related User Story: Reference to the parent user story\n" \
#                      "Description: Detailed explanation of the technical work required\n" \
#                      "Acceptance Criteria: Specific requirements that must be met for completion\n" \
#                      "Estimated Effort: Time or complexity estimation\n" \
#                      "Dependencies: Any tasks that must be completed first"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=(
        "The answer should be tasks following this exact structure:\n"
        "Task ID: A unique identifier for tracking purposes\n"
        "Task Title: Brief description of the specific development work\n"
        "Related User Story: Reference to the parent user story\n"
        "Description: Detailed explanation of the technical work required\n"
        "Acceptance Criteria: Specific requirements that must be met for completion\n"
        "Estimated Effort: Time or complexity estimation\n"
        "Dependencies: Any tasks that must be completed first"
    ),
    worker_agent=development_engineer_knowledge_agent,
    max_interactions=5,
)

# Routing Agent
routing_agent = RoutingAgent(openai_api_key=openai_api_key, agents=[])
# TODO: 10 - Instantiate a routing_agent. You will need to define a list of agent dictionaries (routes) for Product Manager, Program Manager, and Development Engineer. Each dictionary should contain 'name', 'description', and 'func' (linking to a support function). Assign this list to the routing_agent's 'agents' attribute.

# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function should:
#   1. Take the input query (e.g., a step from the action plan).
#   2. Get a response from the respective Knowledge Augmented Prompt Agent.
#   3. Have the response evaluated by the corresponding Evaluation Agent.
#   4. Return the final validated response.

def product_manager_support_function(query: str):
    knowledge_response = product_manager_knowledge_agent.respond(query)
    result = product_manager_evaluation_agent.evaluate(
        initial_prompt=query, worker_response=knowledge_response
    )
    return result["final_response"]


def program_manager_support_function(query: str):
    knowledge_response = program_manager_knowledge_agent.respond(query)
    result = program_manager_evaluation_agent.evaluate(
        initial_prompt=query, worker_response=knowledge_response
    )
    return result["final_response"]


def development_engineer_support_function(query: str):
    knowledge_response = development_engineer_knowledge_agent.respond(query)
    result = development_engineer_evaluation_agent.evaluate(
        initial_prompt=query, worker_response=knowledge_response
    )
    return result["final_response"]


routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": "Define Email Router personas and user stories using the required format.",
        "keywords": ["product manager", "user stories"],
        "func": product_manager_support_function,
    },
    {
        "name": "Program Manager",
        "description": "Group validated user stories into cohesive Email Router product features with all required fields.",
        "keywords": ["program manager", "product features"],
        "func": program_manager_support_function,
    },
    {
        "name": "Development Engineer",
        "description": "Create detailed development tasks for the Email Router plan based on approved stories and features.",
        "keywords": ["development engineer", "development tasks"],
        "func": development_engineer_support_function,
    },
]

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "Create a comprehensive project plan for the Email Router product including user stories, key features, and development tasks."
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# TODO: 12 - Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
#   2. Initialize an empty list to store 'completed_steps'.
#   3. Loop through the extracted workflow steps:
#      a. For each step, use the 'routing_agent' to route the step to the appropriate support function.
#      b. Append the result to 'completed_steps'.
#      c. Print information about the step being executed and its result.
#   4. After the loop, print the final output of the workflow (the last completed step).
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
completed_steps = []

for step in workflow_steps:
    if not step.strip():
        continue
    print(f"\n--- Executing step: {step} ---")
    result = routing_agent.route(step)
    completed_steps.append(result)
    print("Step result:")
    print(result)

if completed_steps:
    print("\nFinal workflow output:\n")
    for idx, section in enumerate(completed_steps, start=1):
        print(f"Section {idx}:\n{section}\n")
else:
    print("\nNo workflow steps were completed.")
