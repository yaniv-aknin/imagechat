#!/usr/bin/env python
import time
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import requests
import os

app = Flask(__name__)
client = OpenAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def process_messages():
    prompt = "\n".join(request.json['messages'])
    api_response = client.images.generate(
      model="dall-e-3",
      prompt=prompt,
      size="1024x1024",
      quality="standard",
      n=1,
    )
    return jsonify({
        "rewrittenPrompt": api_response.data[0].revised_prompt,
        "imageUrl": api_response.data[0].url,
    })

if __name__ == '__main__':
    app.run(debug=True)
