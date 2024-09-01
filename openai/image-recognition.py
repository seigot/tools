import openai
import base64
import os

# 画像から数値を取得する関数
# image_path: 画像のパス
# return: 数値
# 準備: OPENAI_API_KEYを環境変数に設定しておく
def image2num(image_path):
    # openai.api_key="OPENAI_API_KEY"
    api_key = os.environ.get("OPENAI_API_KEY")
    def encode_image(image_path):
      with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = encode_image(image_path)

    response = openai.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
            "role": "system",
            "content": "画像に数字が書かれています。画像を解析して、数字のみを回答してください。"
        },
        {
            "role": "user",
            "content": [
            {"type": "text", "text": "画像に数字が書かれています。画像を解析して、数字のみを回答してください。"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            ]
        }
    ],
    max_tokens=300
    )
    return response

# 実行
response = image2num("75.jpg")
print("number : " + response.choices[0].message.content)
