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
    "# 自治会総会の出欠連絡 \
    **概要**  \
    来月のお祭りに向けて、自治会総会を開催します。  \
    出欠欄の記入後、次の方へ回覧して下さい。  \
    **日時**: 2024年9月10日 18:00  \
    **場所**: 自治会館  \
    --- \
    ## 出欠欄 \
    - **住人1**: [ ] 出席  [ ] 欠席  \
    - **住人2**: [ ] 出席  [ ] 欠席  \
    - **住人3**: [ ] 出席  [ ] 欠席  \
    --- \
    **回覧板を次の方へお回しください。** "
)
print(out)