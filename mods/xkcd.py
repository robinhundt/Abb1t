# essential
import _thread as thread
from queue import *

# other imports
from lxml import html
import re
import requests
import random
import tempfile
import time

xkcd_latest = "http://xkcd.com/info.0.json"
xkcd_number = "http://xkcd.com/{}/info.0.json"

class xkcd:

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"""/xkcd ?([1-9]\d+|rnd|rand|random|toggle|)$ - self explanatory, possibility to toggle for new xkcds"""
        self.queue_in = Queue()
        self.latest = xkcd.get_total_number()
        self.chat_ids = []
        try: 
            with open("xkcd_chat_ids") as f:
                chat_ids=f.read()
                if chat_ids:
                    self.chat_ids=[int(chat_id) for chat_id in chat_ids.split(",")]
        except FileNotFoundError:
            pass
        thread.start_new_thread(self.run, ())
        thread.start_new_thread(self.update, ())

    def run(self):
        while True:
            message = self.queue_in.get()  # get() is blocking
            message_text = message.get_text().lower()
            chat_id = message.get_chat_id()
            match = re.search(r'^(\/xkcd) ?([1-9]\d+|rnd|rand|random|)$', message_text)
            if match:
                if not match.group(2):
                    self.getXKCD(chat_id, xkcd.get_total_number())
                elif 'nd' in match.group(2):
                    random.seed()
                    self.getXKCD(chat_id, random.randint(1, xkcd.get_total_number()))
                elif int(match.group(2)) < xkcd.get_total_number():
                    self.getXKCD(chat_id, int(match.group(2)))
                else:
                    self.bot.sendMessage(chat_id, "Sorry, this xkcd doesn't yet exist.")
            elif re.search(r'^/xkcd toggle$', message_text):
                print(self.chat_ids)
                if chat_id not in self.chat_ids:
                    self.chat_ids.append(message.get_chat_id())
                    self.bot.sendMessage(message.get_chat_id(), "Added your chat\_id to the *xkcd ticker*", parse_mode="Markdown")
                else:
                    self.chat_ids.remove(message.get_chat_id())
                    self.bot.sendMessage(message.get_chat_id(), "Deleted your chat\_id from the *xkcd ticker*", parse_mode="Markdown")
                self.save_ids()

    def save_ids(self):
        with open("xkcd_chat_ids","w") as fw:
            fw.write(",".join(str(chat_id) for chat_id in self.chat_ids))


    def enqueue(self, msg):
        self.queue_in.put(msg)


    def update(self):
        while True:
            if self.chat_ids: # refresh only if someone needs the xkcd...
                current_latest = xkcd.get_total_number()
                if self.latest != current_latest: #new one available
                    self.latest = current_latest
                    self.getXKCD(chat_id, xkcd.get_total_number())
            time.sleep(900) # sleep 15min

    def getXKCD(self, chat_id, number):
        r = requests.get(xkcd_number.format(number)).json()
        with tempfile.NamedTemporaryFile(suffix='png') as image:
            image.write(requests.get(r[u'img']).content)
            image.seek(0)
            self.bot.sendMessage(
                chat_id, "xkcd #{}: *{}*".format(r[u'num'], r[u'title']), parse_mode='Markdown')
            self.bot.sendPhoto(chat_id, image)
            self.bot.sendMessage(chat_id, r[u'alt'])

    @staticmethod
    def get_total_number():
        return int(requests.get(xkcd_latest).json()['num'])


