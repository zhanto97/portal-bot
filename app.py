import logging
import os
import pprint
import random
import scraper
import threading
import time
from flask import Flask, request
from pymessenger.bot import Bot
from users import User

app = Flask(__name__)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
# print("access token: " + ACCESS_TOKEN)
# print("verify token: " + VERIFY_TOKEN)
bot = Bot(ACCESS_TOKEN)
users = {}
pp = pprint.PrettyPrinter(indent=4)

"""
TODOs:

let user delete his/her credentials to never receive messages again
"""

def thread_notifier(user):
    notices = scraper.scrape(user.portal_id, user.portal_password)
    user.last_href = notices[0][0]
    # logging.info("last href: " + user.last_href)
    while True:
        if user.stop:
            break
        notices = scraper.scrape(user.portal_id, user.portal_password)
        pp.pprint(notices)
        if isinstance(notices, str):
            break

        for notice in notices:
            if notice[0] == user.last_href:
                break
            else:
                bot.send_text_message(user.messenger_id,
                    "New notice:\n" + notice[1])
        user.last_href = notices[0][0]
        # logging.info("last href: " + user.last_href)
        
        # Sleep 5 minutes
        time.sleep(300)
    bot.send_text_message(user.messenger_id, "Notice sending stopped")


@app.route('/')
def index():
    return "<h1>Welcome to portal-bot!</h1>"

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
                    received = message['message'].get('text')
                    pp.pprint(received)
                    user = users[recipient_id]
                    if user.get_id() == None:
                        user.update_id(received)
                        bot.send_text_message(recipient_id,
                            "Please, provide your Portal password")
                    elif user.get_password() == None:
                        user.update_password(received)
                        if user.check_credentials():
                            bot.send_text_message(recipient_id,
                                "Correct credentials! New notices will be sent from now on. To stop receiving notices, send \"Stop\"")
                            t = threading.Thread(target=thread_notifier,
                                args=(user,))
                            user.thread = t
                            t.start()
                        else:
                            user.update_id(None)
                            user.update_password(None)
                            bot.send_text_message(recipient_id,
                                ("Login unsuccessful. Try again by "
                                 "providing Portal ID"))
                    elif received == "Stop":
                        logging.info("last href: " + user.last_href)
                        user.update_id(None)
                        user.update_password(None)
                        user.stop = True
            elif message.get('postback'):
                if message['postback']['payload'] == "get_started_postback_payload":
                    users[recipient_id] = User(recipient_id)
                    bot.send_text_message(recipient_id, "Please, provide your Portal ID")

    return "Message Processed"


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


if __name__ == "__main__":
    app.run("0.0.0.0", 3000)