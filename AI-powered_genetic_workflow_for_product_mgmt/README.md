# AI-Powered Agentic Workflow for Project Management

In this repo, you will find all the files and instructions required to complete the project. You can find more information about the project inside the Udacity Classroom.

## Getting Started

The project needs to be completed in two phases and you will find starter code for both the phases inside the `starter` folder in this repo. 

## Dependencies

A `requirements.txt` file has been provided in this repo if you want to work on the project locally. Otherwise, the workspace provided in the Udacity classroom has been configured with all the required libraries. 

## Project Instructions

You will find instructions for each of the two phases of the project in the README file inside the folder for that phase.

## Evaluation

For logging the files, move to the `starter` folder and run these commands:

```
cd phase_1

python3 direct_prompt_agent.py               | tee ../logs/phase_1/direct_prompt_agent.txt
python3 augmented_prompt_agent.py            | tee ../logs/phase_1/augmented_prompt_agent.txt
python3 knowledge_augmented_prompt_agent.py  | tee ../logs/phase_1/knowledge_augmented_prompt_agent.txt
python3 evaluation_agent.py                  | tee ../logs/phase_1/evaluation_agent.txt
python3 routing_agent.py                     | tee ../logs/phase_1/routing_agent.txt
python3 action_planning_agent.py             | tee ../logs/phase_1/action_planning_agent.txt
python3 rag_knowledge_prompt_agent.py        | tee ../logs/phase_1/rag_knowledge_prompt_agent.txt   

cd ..

python3 -m phase_2.agentic_workflow          | tee logs/phase_2_workflow_output.txt
```

## License
[License](../LICENSE.md)
