# essential
import _thread as thread
from queue import *
import re

# other imports
from lxml import html
import re
import requests
import random
import tempfile
import time


class mydealz:
    url = "https://www.mydealz.de/freebies"

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"""*/mydealz* - toggle to get freebie notifications"""
        self.queue_in = Queue()
        self.chat_ids = []
        self.freebies = []
        self.filename = "mydealz_chat_ids"
        try: 
            with open(self.filename) as f:
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
            match = re.search(r'^(?:/|!)mydealz$', message_text)
            if match:
                print(self.chat_ids)
                if chat_id not in self.chat_ids:
                    self.chat_ids.append(message.get_chat_id())
                    self.bot.sendMessage(message.get_chat_id(), "Added your chat\_id to the *mydealz ticker*", parse_mode="Markdown")
                else:
                    self.chat_ids.remove(message.get_chat_id())
                    self.bot.sendMessage(message.get_chat_id(), "Deleted your chat\_id from the *mydealz ticker*", parse_mode="Markdown")
                self.save_ids()

    def save_ids(self):
        with open(self.filename,"w") as fw:
            fw.write(",".join(str(chat_id) for chat_id in self.chat_ids))


    def enqueue(self, msg):
        self.queue_in.put(msg)

    def get_xpath(self, url, xpath):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree.xpath(xpath)

    def update(self):
        while True:
            if self.chat_ids: # refresh only if someone needs the freebie...
                freebies = []
                for a in self.get_xpath(mydealz.url,'//*[@class="cept-tt linkPlain space--r-1 space--v-1"]'):
                    freebies.append(a.text)
                    if self.freebies and a.text not in self.freebies: #set, and new freebie
                        for chat_id in self.chat_ids: #this is not that performant... maybe change it in the future
                            self.bot.sendMessage(chat_id, "New mydealz post: *{}* [»here«]({})".format(a.text,a.attrib['href']), parse_mode="Markdown")
                self.freebies=freebies
            time.sleep(300) # sleep 4hr

    @staticmethod
    def get_total_number():
        return int(requests.get(xkcd_latest).json()['num'])


