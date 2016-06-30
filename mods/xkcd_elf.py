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
        self.description = """*/mensa* _<day>_ _<preference>_
*/zmensa* _<day>_ _<preference>_- outputs the mensa menu for _<day>_ and _<preference>_
where _<preference>_ can be fish, dessert, meat, vegan, veg (for vegetarian incl. vegan)"""
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


# {"month: 6, num: 1700, link: , year: 2016, news: , safe_title: New Bug,
# "transcript: , alt: There's also a unicode-handling bug in the URL request
# "library, and we're storing the passwords unsalted ... so if we salt them with
# "emoji, we can close three issues at once!, img:
# "http:\/\/imgs.xkcd.com\/comics\/new_bug.png, title: New Bug, day: 29}
