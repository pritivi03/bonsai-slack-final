from email import message
import json
from re import A
from matplotlib.pyplot import text
import slack
import os
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import requests
from slack_bolt import App

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
from slack_bolt.async_app import AsyncApp
import time
import aiohttp
from responses import responses_arr
import random

load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=os.environ["SLACK_SIGNING_SECRET"],name="Bonsai Bot")

async def getAnswer(question):
     #take the question and send through api
    api_url = os.getenv("API_URL")
    async with aiohttp.ClientSession() as session:
        request_data = {
            'question': question
        }
        async with session.post(api_url + "/getAnswer/123", data=request_data) as resp:
            json_response = await resp.json()
            answer = json_response['answer']
            return answer    

@app.event("message")
async def handle_message_events(body, say, logger):
    event = body['event']
    print(body)
    print(event)
    if 'text' in event:
        question = event['text']
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Was this helpful?",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "👍"
                        },
                        "style": "primary",
                        "value": "click_me_123",
                        "action_id": "approve_button"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "👎"
                        },
                        "style": "danger",
                        "value": "click_me_123",
                        "action_id": "decline_button"
                    }
                ]
            }
        ]
        await say({'thread_ts': event['ts'], 'text': random.choice(responses_arr)})
        answer = await getAnswer(question)
        await say({'thread_ts': event['ts'], 'text': answer})
        if answer != 'No information found. Try rephrasing.':
            #ask for feedback if the answer was given
            await say({'thread_ts': event['ts'], 'blocks': blocks})
    return

@app.action("approve_button")
async def handle_some_action(ack, body, logger):
    await ack()
    logger.info(body)
    print("HELLO WORLD")

@app.action("decline_button")
async def handle_some_action(ack, body, logger):
    await ack()
    logger.info(body)

def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    #main()
    app.start(5001)