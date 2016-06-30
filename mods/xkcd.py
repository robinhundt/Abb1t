# essential
import _thread as thread
from queue import *

# other imports
from lxml import html
import re
import requests
import random
import tempfile

xkcd_latest = "http://xkcd.com/info.0.json"
xkcd_number = "http://xkcd.com/{}/info.0.json"

class xkcd:

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"""^(\/xkcd) ?([1-9]\d+|rnd|rand|random|)$"""
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get()  # get() is blocking
            message_text = message.get_text()
            chat_id = message.get_chat_id()
            match = re.search(r'^(\/xkcd) ?([1-9]\d+|rnd|rand|random|)$', message_text)
            if not match:
                continue

            if not match.group(2):
                self.getXKCD(chat_id, getTotalNumber())
            elif 'nd' in match.group(2):
                random.seed()
                self.getXKCD(chat_id, random.randint(1, getTotalNumber()))
            elif int(match.group(2)) < getTotalNumber():
                self.getXKCD(chat_id, int(match.group(2)))
            else:
                self.bot.sendMessage(chat_id, "Sorry, this xkcd doesn't yet exist.")



    def enqueue(self, msg):
        self.queue_in.put(msg)

    def getXKCD(self, chat_id, number):
        r = requests.get(xkcd_number.format(number)).json()
        with tempfile.NamedTemporaryFile(suffix='png') as image:
            image.write(requests.get(r[u'img']).content)
            image.seek(0)
            self.bot.sendMessage(
                chat_id, "xkcd #{}: *{}*".format(r[u'num'], r[u'title']), parse_mode='Markdown')
            self.bot.sendPhoto(chat_id, image)
            self.bot.sendMessage(chat_id, r[u'alt'])


def getTotalNumber():
    return int(requests.get(xkcd_latest).json()['num'])


