from swarms import Agent, SequentialWorkflow, OpenAIChat
import os

# Initialize the language model agent (e.g., GPT-3)
# Get the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
# export OPENAI_API_KEY=xxxxx

# Create an instance of the OpenAIChat class
model = OpenAIChat(
    api_key=api_key, model_name="gpt-4o", temperature=0.1
)

# Initialize agents for individual tasks
agent1 = Agent(
    agent_name="resident1",
    system_prompt="Please answer by placing a check mark in the column for resident 1 in the table written in markdown.",
    llm=model,
    max_loops=1,
    dashboard=False,
    tools=[],
)
agent2 = Agent(
    agent_name="resident2",
    system_prompt="Please answer by placing a check mark in the column for resident 2 in the table written in markdown.",
    llm=model,
    max_loops=1,
    dashboard=False,
    tools=[],
)
agent3 = Agent(
    agent_name="resident3",
    system_prompt="Please answer by placing a check mark in the column for resident 3 in the table written in markdown.",
    llm=model,
    max_loops=1,
    dashboard=False,
    tools=[],
)

# Create the Sequential workflow
workflow = SequentialWorkflow(
    agents=[agent1, agent2, agent3], max_loops=1, verbose=False
)

# Run the workflow
out = workflow.run(
    "You are the leader of the residents of an apartment. \
    Information is shared through circular boards. \
    When the circular board is handed over, you must check the appropriate box before passing it on to the next person. \
    Please encourage residents to check the circular board in turn and ask them to check the appropriate box in the markdown table below. \
    | resident No. | answer | \
    | ---- | ---- | \
    | resident1 |  | \
    | resident2 |  | \
    | resident3 |  | "
)
print(out)