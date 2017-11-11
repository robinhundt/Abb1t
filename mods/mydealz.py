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
import os

class mydealz:
    url = "https://www.mydealz.de/freebies"
    try:
        min_temp = int(open("./mydealz/temperature").read())
    except:
        min_temp = 350
        print("[!] no min_temp for mydealz set, loading default: {}".format(min_temp))

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"""*/mydealz* - toggle to get freebie notifications, use */mydealztemp* to define a minimum heat of deals"""
        self.queue_in = Queue()
        self.chat_ids = []
        self.sent_already = [time.time()]
        self.freebies = []
        try:
            os.mkdir("mydealz")
        except OSError:
            pass #dir exists.
        self.filename = "./mydealz/mydealz_chat_ids"
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
            else:
                match = re.search(r'^(?:/|!)mydealztemp (\d{0,5})$', message_text)
                if match and match.group(1):
                    prev = mydealz.min_temp
                    new = int(match.group(1))
                    if new >= 0:
                        mydealz.min_temp = new
                        if prev != new: #something changed:
                            with open("./mydealz/temperature","w") as fw:
                                fw.write("{}".format(mydealz.min_temp))
                            self.bot.sendMessage(message.get_chat_id(), "Changed minimum temperature of freebies from *{}°* to *{}°*.".format(prev,mydealz.min_temp), parse_mode="Markdown")
                        else:
                            self.bot.sendMessage(message.get_chat_id(), "Minimum temperature is already at *{}°*!".format(mydealz.min_temp), parse_mode="Markdown")


    def save_ids(self):
        with open(self.filename,"w") as fw:
            fw.write(",".join(str(chat_id) for chat_id in self.chat_ids))


    def enqueue(self, msg):
        self.queue_in.put(msg)

    def get_xpath(self, url, xpath):
        try:
            page = requests.get(url)
            tree = html.fromstring(page.content)
            return tree.xpath(xpath)
        except:
            return []


    def update(self):
        while True:
            try:
                if self.chat_ids: # refresh only if someone needs the freebie...
                    freebies = []
                    temperatures = self.get_xpath(mydealz.url,"//strong[contains(@class,'vote-temp space--r-1')]")
                    for a,temp in zip(self.get_xpath(mydealz.url,'//*[contains(@class,"cept-tt thread-link linkPlain space--r-1")]'),temperatures):
                        if int(temp.text[:-1])>=mydealz.min_temp:
                            texttitle = a.text.strip("\n\t\r ")
                            freebies.append(texttitle)
                            if self.freebies and texttitle not in self.freebies: #set, and new freebie
                                if a.attrib['href'] not in self.sent_already:
                                    for chat_id in self.chat_ids: #this is not that performant... maybe change it in the future
                                        self.sent_already.append(a.attrib['href'])
                                        self.bot.sendMessage(chat_id, "New mydealz post (*{}*): *{}* [»here«]({})".format(temp.text,a.text,a.attrib['href']), parse_mode="Markdown")
                    self.freebies=freebies
                time.sleep(300) # sleep 5min
                if time.time()-self.sent_already[0]>24*3600: #deals may be resend each 24h
                    self.sent_already=[time.time()]
            except:
                pass

    @staticmethod
    def get_total_number():
        return int(requests.get(xkcd_latest).json()['num'])


