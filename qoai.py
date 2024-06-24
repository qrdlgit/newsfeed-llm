import openai
import requests
import json
import os
import shutil

# Set up the OpenAI API
openai.api_key = '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'

def get_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0]['message']['content']



import sys
print(get_response(open(sys.argv[1]).read()))
