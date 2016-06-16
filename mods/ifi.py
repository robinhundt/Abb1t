# essential
import _thread as thread
from queue import *

# other imports
from lxml import html
import requests
import time

class ifi:
    def __init__(self, bot):
        # Initialize update timer and threshold.
        self.reply = ""
        self.last_update = 0
        self.threshold = 300

        self.bot = bot.bot
        self.description = """*/ifi*_- outputs currently running lectures"""
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get() # get() is blocking
            if not re.search(r'^/ifi', message.get_text()):
                continue

            # Check if ifi could be requested again.
            if time.time() - self.last_update > self.threshold:
                # Update the topic update timer, ...
                self.last_update = time.time()

                # ... clear current backup ...
                self.reply = ""

                # ... and update the lectures.
                lectures = fetch_lectures()
                for lecture in lectures:
                    self.reply += "{0} *{1}* {2} {3}\n".format(
                        lecture[0], lecture[1], lecture[2], lecture[3])

            self.bot.sendMessage(message.get_chat_id(), self.reply, parse_mode="Markdown")
            
    def fetch_lectures(self):
        lectures = []

        for tr in self.get_xpath("http://display.informatik.uni-goettingen.de/events.html", 
             '//*[@id="id_content"]/table')[0]:
            if len(tr) == 4:
                lectures.append(self.process_lecture(tr))

        return lectures

    def process_lecture(self, tr):
        return [ ' '.join(td.text_content().split()) for td in tr ]

    def get_xpath(self, url, xpath):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree.xpath(xpath)

    def enqueue(self, msg):
        self.queue_in.put(msg)