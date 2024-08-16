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
    agent_name="Blog generator",
    system_prompt="Generate a blog post like stephen king",
    llm=model,
    max_loops=1,
    dashboard=False,
    tools=[],
)
agent2 = Agent(
    agent_name="summarizer",
    system_prompt="Sumamrize the blog post",
    llm=model,
    max_loops=1,
    dashboard=False,
    tools=[],
)

# Create the Sequential workflow
workflow = SequentialWorkflow(
    agents=[agent1, agent2], max_loops=1, verbose=False
)

# Run the workflow
out = workflow.run(
    "Generate a blog post on how swarms of agents can help businesses grow."
)
print(out)