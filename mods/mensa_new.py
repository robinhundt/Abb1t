# essential
import _thread as thread
from queue import *

# other imports
from lxml import html
import re
import requests

weekday_index = {d : i for i, d in enumerate(
    ["sunday",
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday"]
)}

class mensa_new:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = """*/mensa* _<day>_ _<preference>_
*/zmensa* _<day>_ _<preference>_- outputs the mensa menu for _<day>_ and _<preference>_
where _<preference>_ can be fish, dessert, meat, vegan, veg (for vegetarian incl. vegan)"""
        self.queue_in=Queue()
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            message = self.queue_in.get() # get() is blocking
            if not re.search(r'^/[zt]?mensa', message.get_text()):
                continue

            chat_id = message.get_chat_id()
            data, filtr = compute_query(message.get_text())
            reply = ""
            for meal in filter(filtr, meal_list(data)):
                reply += "*" + meal.title + "*\n"
                reply += meal.description + "\n\n"

            if reply == "":
                reply = "Sadly you will have to starve :-("

            self.bot.sendMessage(chat_id, reply, parse_mode="Markdown")

    def enqueue(self,msg):
        self.queue_in.put(msg)

### Helper functions and classes for the bot
class Meal:
    """docstring for Meal"""
    __slots__ = ["title", "description", "religion"]
    def __init__(self, title, description, religion):
        self.title = re.sub(r'\([^)]*\)', '', title).strip()
        self.description = re.sub(r' \([^)]*\)', '', description).strip()

        # this order has meaning
        if 'Vegan' in title + description:
            self.religion = 'vegan'
        elif 'Dessert' in title:
            self.religion = 'dessert'
        elif 'fleischlos' in religion:
            self.religion = 'vegetarian'
        elif 'Fisch' in religion or 'MSC' in religion:
            self.religion = 'fish'
        elif 'mit Fleisch' in religion:
            self.religion = 'meat'
        else:
            self.religion = 'omnivor'


def get_xpath(url, data, xpath):
    page = requests.get(url, data)
    tree = html.fromstring(page.content)
    return tree.xpath(xpath)


def compute_query(message):
    mensa = re.search(r'^/[zt]?mensa', message)
    day   = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', message)
    filtr = re.search(r'(vegan|veg|meat|fish|dessert)', message)

    mensa  = {'/zmensa' : 'Zentralmensa', '/mensa' : 'Nordmensa', '/tmensa' : 'Mensa am Turm'}[mensa.group(0)]
    day    = weekday_index[day.group(0)] if day else 31415 # if > 7 mensa return today
    select = lambda a: filtr.group(0) in a.religion if filtr else lambda a: True

    return {"selectmensa" : mensa, "push" : 0, "day" : day}, select


def meal_list(data):
    for tr in get_xpath("http://www.studentenwerk-goettingen.de/speiseplan.html",
                    data, '//*[@id="speise-main"]/table')[0]:
        menu = tr[0][0].text

        # there is nothing to eat on sundays
        if data['day'] == weekday_index['sunday']:
            return

        # check if we don't want to parse this row of the table
        if any(word in menu for word in [
                'Öffnungszeiten',
                'Last Minute',
                'Salatbuffet',
                'Pastapoint',
                'Studentenfutter',
                'Fitnesscenter',
                'Beilagen']):
            continue

        # parsing the description field
        # this code is weird because the Mensa Speiseplan is weird
        description = [x.strip() for x in tr[1][0].text_content().strip().split("\r\n\t\t\r\n\t\t")]
        if len(description) == 1: # For dessert and other not changing dishes
            title = menu
            description = description[0].replace(", ", "\n")
        else: # len(description) == 2 -- here comes everything else
            title, description = description

        religion = tr[2][0].attrib['title']

        yield Meal(title, description, religion)
