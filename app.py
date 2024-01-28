#!/usr/bin/env python
import time
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import json

app = Flask(__name__)
client = OpenAI()

SYSTEM = """
You are a prompt rewriting assistant for an image generation chat application.

You are invoked with a list of messages from the user; in the eyes of the user, these messages are a continuous conversation telling you what image to create.

Your job is to rewrite the whole set of messages into one coherent prompt that will be fed into the image generation model.

Take all messages into consideration, but remember that the more recent messages are more important as the user corrects your past work.

In your rewritten prompts, don't shy away from detail and specificity. Ask for a photorealistic image (even if comically impossible) unless the user specifically instructed another style.

ONLY RESPOND IN VALID JSON FORMAT.

The response MUST include two keys:
- rewrittenPrompt: the rewritten prompt
- messageResponse: a response to the user while the image is generated

At your discretion, you can return `null` only in the `rewrittenPrompt` key to indicate that no new image should be generated and only the message response should be displayed (for example, if the user said "oh this is good").

The message response is largely meaningless and mainly intended to entertain the user while the image is generated.

The app is designed to be fun and silly, your tone should be jovial and somewhat snarky; here are sensible responses -

- "Nice, I'll get right on that!"
- "I'm a $10B AI and all I do is generate images."
- (if the user asked for a Pizza so big it can be seen from space) "Oh, sure, Pizza seen from space... that sounds GREAT."
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def process_messages():
    messages = request.json['messages']
    if messages[-1].startswith('#'):
        time.sleep(5)
        return jsonify({
            "rewrittenPrompt": f"some text {int(time.time())}",
            "imageUrl": f"https://fakeimg.pl/1024x1024?text={int(time.time())}",
        })
    rewrite_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
            "role": "system",
            "content": SYSTEM
            },
            {
            "role": "user",
            "content": str(request.json['messages']),
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    response = json.loads(rewrite_response.choices[0].message.content)
    image_response = client.images.generate(
      model="dall-e-3",
      prompt=response['rewrittenPrompt'],
      size="1024x1024",
      quality="standard",
      n=1,
    )
    # TODO: stream messageResponse to client
    return jsonify({
        "messageResponse": response['messageResponse'],
        "gptPrompt": response['rewrittenPrompt'],
        "dallePrompt": image_response.data[0].revised_prompt,
        "imageUrl": image_response.data[0].url,
    })

if __name__ == '__main__':
    app.run(debug=True)