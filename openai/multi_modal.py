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
    prompt = "この写真は車が写っています。車が汚れていないかどうか確認してください。若干のホコリは無視してください。どうか鳥のフンは要注意でお願いします。"
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

out = check_image("front.jpg")
#out = check_image("right.jpg")
#out = check_image("left.jpg")
print(out)

# Load the environment variables
load_dotenv()

# Initialize the language model
llm = GPT4VisionAPI(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    max_tokens=500,
)

# Initialize the task
task = ("Please explain the image.")

task2 = (
    "You are a professional inspector. The image is the exterior of the car. Check if there is any dirt on the car.If there is no dirt, please check the check box 正面. If there is any dirt, please write the reason. \
    Check list \
    ## items \
    - **Front**: [] OK  [ ] NG\
    - **Left** : [] OK  [ ] NG\
    - **Right**: [] OK  [ ] NG"
)
img = "front.jpg"

## Initialize the workflow
agent = Agent(
    agent_name = "Multi-ModalAgent",
    llm=llm, 
    max_loops="auto", 
    autosave=True, 
    dashboard=True, 
    multi_modal=True
)

# Run the workflow on a task
out = agent.run(task, img)

print(out)