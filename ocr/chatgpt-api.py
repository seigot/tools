import openai

openai.api_key = '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'

response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {'role': 'user', 'content': 'ハローワールド！！'}],
                temperature=0.0,
)

print(response['choices'][0]['message']['content'])