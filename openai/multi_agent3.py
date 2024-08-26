import os
from dotenv import load_dotenv
from swarms import GPT4VisionAPI, Agent

import base64
import requests
import os
api_key = os.environ.get("OPENAI_API_KEY")
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def check_image(image_path):
    #image_path = "front.jpg"
    #image_path = "right.jpg"
    #image_path = "left.jpg"
    base64_image = encode_image(image_path)
    prompt = "この写真は車が写っています。車が汚れていないかどうか確認してください。若干のホコリは気にしないでください。どうか鳥のフンは要注意でお願いします。"
    headers = {
       "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
    #    "model": "gpt-4-vision-preview",
      "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1200
    }
    response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
    out = response.json()['choices'][0]['message']['content']
    #print(response.json())
    print(out)
    return out

out1 = check_image("front.jpg")
out2 = check_image("left.jpg")
out3 = check_image("right.jpg")
print(out1)
print(out2)
print(out3)

from swarms import Agent, SequentialWorkflow, OpenAIChat
import os
# Initialize the language model agent (e.g., GPT-3)
api_key = os.getenv("OPENAI_API_KEY")
model = OpenAIChat(    api_key=api_key, model_name="gpt-4o", temperature=0.1   )
# Initialize agents for individual tasks
agent1 = Agent(
    agent_name="check1",    system_prompt="Please answer by placing a check mark in the column for **Front** in the table written in markdown. if there is a dirt, please fill the reason in NG instead." + out1,
    llm=model,    max_loops=1,    dashboard=False,    tools=[],
)
agent2 = Agent(
    agent_name="check2",    system_prompt="Please answer by placing a check mark in the column for **Left** in the table written in markdown. if there is a dirt, please fill the reason in NG instead." + out2,
    llm=model,    max_loops=1,    dashboard=False,    tools=[],
)
agent3 = Agent(
    agent_name="check3",    system_prompt="Please answer by placing a check mark in the column for **Right** in the table written in markdown. if there is a dirt, please fill the reason in NG instead." + out3,
    llm=model,    max_loops=1,    dashboard=False,    tools=[],
)
# Create the Sequential workflow
workflow = SequentialWorkflow(    agents=[agent1, agent2, agent3], max_loops=1, verbose=False   )

# Run the workflow
out = workflow.run(
    "Check List.\
    ## Item\
    - **Front**: [] OK  [ ] NG reason --> []\
    - **Left** : [] OK  [ ] NG reason --> []\
    - **Right**: [] OK  [ ] NG reason --> []"
)
print(out)