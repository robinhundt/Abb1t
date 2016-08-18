# essential
import _thread as thread
from queue import *
import re

# other imports
from lxml import html
from requests.exceptions import Timeout
import re
import requests
import time


class bsmensa:
    weekday_index = {d: i for i, d in enumerate(
        ["su", "mo", "tu", "we", "th", "fr", "sa"]
    )}
    weekdays = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = """*/bsmensa([1-3]{1}|360)* _<day>_ - outputs the mensa menu for _<day>_"""
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get()  # get() is blocking
            if not re.search(r'^(?:/|!)bsmensa([1-3]{1}|360)', message.get_text()):
                continue

            to_match = re.search(r'timeout=(\d*\.?\d+)', message.get_text())
            timeout = float(to_match.group(1)) if to_match else 2

            chat_id = message.get_chat_id()
            message_text = message.get_text().lower()
            message_id = message.get_message_id()
            
            mensa = re.search(r'^(?:/|!)bsmensa([1-3]{1}|360)', message_text)
            if not mensa:
                continue

            day = re.search(r'\s(mo|tu|we|th|fr|sa|su)', message_text)
            mensa_name = mensa.group(0)[1:]
            if mensa_name == 'bsmensa1':
                self.bot.sendMessage(chat_id, "Not implemented yet, sorry 😕", parse_mode="Markdown", reply_to_message_id= message_id)
                continue
            if mensa_name == 'bsmensa3':
                mensa_name = 'bsmensa360'
            mensa_data = {
                'bsmensa1': ['http://www.stw-on.de/braunschweig/essen/menus/mensa-1', 2],
                'bsmensa2': ['http://www.stw-on.de/braunschweig/essen/menus/mensa-2', 1],
                'bsmensa': ['http://www.stw-on.de/braunschweig/essen/menus/mensa-2', 1],
                'bsmensa360': ['http://www.stw-on.de/braunschweig/essen/menus/360-2', 1],
                }[mensa_name]
            day = bsmensa.weekday_index[day.groups()[0]] if day else int(time.strftime("%w"))

            url = mensa_data[0]
            tables_per_day = mensa_data[1]

            reply = ""
            try:
                meals = self.meal_list(timeout, tables_per_day, day, url)
                if not meals:
                    reply = "Sadly you will have to starve :-("
                else:
                    reply = "*Mensa menu for {}*\n".format(bsmensa.weekdays[day])
                    for group, meals in meals.items():
                        reply += "*" + group + "*\n"
                        reply += " » {}\n\n".format("\n » ".join(meals))
            except Timeout:
                reply = "Mensa timed out."

            self.bot.sendMessage(chat_id, reply, parse_mode="Markdown", reply_to_message_id= message_id)

    def enqueue(self, msg):
        self.queue_in.put(msg)


    def get_xpath(self, url, data, xpath, timeout=None):
        page = requests.get(url, data, timeout=timeout)
        tree = html.fromstring(page.content)
        return tree.xpath(xpath)


    def meal_list(self, timeout, tables_per_day, day, url, data={}):
        if day in [0,6]: # saturday/sunday
            return {}
        xpath=self.get_xpath(url, data, '//*[@class="swbs_speiseplan"]', timeout)
        tables=[xpath[day-1]] #multiple tables per day possible
        meals = {}
        for i,table in enumerate(tables):
            for j,tr in enumerate(table):
                if j%2==0: # each second row is left blank
                    continue
                for td in tr:
                    if td.tag in ['td']:
                        for nobr in td:
                            if nobr.tag in ['nobr'] and nobr.text:
                                meal_group = re.sub(r'[0-9]*','',re.sub(r'\([^)]*\)', '', str(nobr.text)))
                                if meal_group:
                                    if meal_group not in meals:
                                        meals[meal_group]=[]
                                    last_group = meal_group
                        meal = td.text
                        if meal:
                            meals[last_group].append(meal.replace("Pizza ",""))
                            break #next meal
        return meals
