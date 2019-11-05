import os
import random
import pprint
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)
pp = pprint.PrettyPrinter(indent=4)

"""
TODOs:

handle postback for get started
get id password from user in an elegant way
create a separate thread for user for scheduled scraper
write out the actual scheduled scraper and notifier
let user delete his/her credentials to never receive messages again
"""

@app.route("/webhook", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            pp.pprint(message)
            recipient_id = message['sender']['id']
            if message.get('message'):
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
            elif message.get('postback'):
                if message['postback']['payload'] == "get_started_postback_payload":
                    send_message(recipient_id, "Please, provide your Portal ID")

    return "Message Processed"


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    return random.choice(sample_responses)


def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run("0.0.0.0", 3000)