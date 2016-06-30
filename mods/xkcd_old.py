# essential
import _thread as thread
from queue import *

# other imports
from lxml import html
import requests
import time
import re
import tempfile

class xkcd:
    def __init__(self, bot):
        # Initialize update timer and threshold.
        self.last_update = 0
        self.threshold = 300

        self.bot = bot.bot
        self.description = """*/xkcd* _<id|r[andom]>_ - outputs current, specific id or random xkcd comic"""
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get() # get() is blocking
            message_text = message.get_text().lower()
            url = ""
            if re.search(r'^/xkcd$', message_text): # current comic
                url = "http://xkcd.com/"
            elif re.search(r'^/xkcd r[andom]{0,5}$', message_text): # current comic
                url = "http://c.xkcd.com/random/comic/"
            elif re.search(r'^/xkcd (\d)', message_text): # message with numeric value
                comic_id = re.search(r'^/xkcd (\d*)$', message_text)
                print(comic_id.groups())
                if comic_id:
                    url = "http://xkcd.com/{}/".format(comic_id.group(1))
                else:
                    continue
            if url:
                comic=self.get_xpath(url,'//*[@id="comic"]/img')[0]
                img_src   = "http://{}".format(comic.get("src").strip('/'))
                img_title = comic.get("title")
                print(img_src,img_title)

                with tempfile.NamedTemporaryFile(suffix='.jpg') as temporaryfile:
                    temporaryfile.write(requests.get(img_src).content)
                    temporaryfile.seek(0)
                    if len(img_title)>200:
                        self.bot.sendPhoto(message.get_chat_id(),temporaryfile,caption="")
                        self.bot.sendMessage(message.get_chat_id(),img_title)
                    else:
                        self.bot.sendPhoto(message.get_chat_id(),temporaryfile,caption=img_title)
            
    def fetch_lectures(self):
        lectures = []

        for tr in self.get_xpath("http://display.informatik.uni-goettingen.de/events.html", 
             '//*[@id="comic"]/img')[0]:
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
