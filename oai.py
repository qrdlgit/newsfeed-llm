import openai
import requests
import json
import os
import shutil

# Set up the OpenAI API

def get_response(prompt, key):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0]['message']['content']



