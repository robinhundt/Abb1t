# essential
import _thread as thread
from queue import *
import re

# other imports
from lxml import html
import requests
import time

class keksseminar:
    def __init__(self, bot):
        # Initialize update timer and threshold.
        self.reply = ""
        self.last_update = 0
        self.threshold = 300

        self.bot = bot.bot
        self.description = """*/keksseminar* - outputs upcoming talks"""
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get() # get() is blocking
            if not re.search(r'^(?:/|!)keksseminar$', message.get_text().lower()):
                continue

            # Check if keksseminar could be requested again.
            if time.time() - self.last_update > self.threshold:
                # Update the topic update timer, ...
                self.last_update = time.time()

                # ... clear current backup ...
                self.reply = ""

                # ... and update the talks.
                talks = self.fetch_talks()
                for t in talks:
                    name = t[1] 
                    if name!="-": #only if a name is supplied, otherwise 
                        date = t[0] if t[0]!="-" else "Unknown date"
                        title= "with \"*{}*\"".format(t[2]) if t[2]!="-" else "(no title supplied so far)"
                        lang = "<{}>".format(t[3]) if t[3]!="-" else ""
                        if title:
                            self.reply += "_{0}_\n*{1}* {2} {3}\n\n".format(date,name,title,lang)
                if not self.reply: # no talks exists
                    self.reply = "No talks to show."
                else:
                    self.reply = "Upcoming *Keksseminar* talks:\n"+self.reply
                self.bot.sendMessage(message.get_chat_id(), self.reply, parse_mode="Markdown")
            
    def fetch_talks(self):
        talks = []
        for table in self.get_xpath("https://wiki.fg.informatik.uni-goettingen.de/content/verantwortungsbereich/keksseminar", '//*/table'):
            if "Seminar Date" in table.text_content():
                (thead,tbody)=[x for x in table]
                #talks.append([td.text for td in thead[0]]) #head not needed atm
                for tr in tbody:
                    talks.append([td.text for td in tr])
                break #no need to parse further tables.
        return talks

    def get_xpath(self, url, xpath):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree.xpath(xpath)

    def enqueue(self, msg):
        self.queue_in.put(msg)
