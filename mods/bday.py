# essential
import _thread as thread
from queue import *

# other imports
import os
import re
import time


def seconds_until(until=9):
    """ Counts the seconds until it is a certain hour again.

    Keyword Arguments:
        until (int): the hour we want to count to (default: {9})

    Returns:
        (float): how many seconds until the specified time.
    """
    now = time.localtime()
    now_sec = time.mktime(now)

    if now.tm_hour >= until:
        delta = (until * 60 * 60) \
            + (60 * 60 * (24 - now.tm_hour)) \
            - (60 * now.tm_min) \
            - (now.tm_sec)
    else:
        delta = (until * 60 * 60) \
            - (60 * 60 * now.tm_hour) \
            - (60 * now.tm_min) \
            - (now.tm_sec)

    then = time.localtime(now_sec + delta)
    return time.mktime(then) - time.time()


class bday:

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"bday insert <name> <dd.mm.yyyy>"
        self.queue_in = Queue()
        self.data_dir = 'bdays'
        self.chat_ids = []
        self.load_chat_ids_bday()

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        thread.start_new_thread(self.run, ())
        thread.start_new_thread(self.happy_birthday, ())

    def enqueue(self, msg):
        self.queue_in.put(msg)

    def run(self):
        while True:
            message = self.queue_in.get()  # get() is blocking
            message_text = message.get_text()
            chat_id = message.get_chat_id()
            regex = re.compile(r'^([!\/]bday) insert ([\w ]{2,30}) ((\d{2})[\/\.]?(\d{2})[\/\.]?(\d{4}))$')
            match = re.search(regex, message_text)
            if match:
                if not chat_id in self.chat_ids:
                    self.add_chat_id(chat_id)
                date = match.group(3)
                name = match.group(2)
                bdays = self.load(chat_id)
                if not date in bdays:
                    bdays[date] = [name]
                else:
                    bdays[date].append(name)
                self.save(chat_id, bdays)

                self.bot.sendMessage(message.get_chat_id(), "Got it.")

    def happy_birthday(self):
        while True:
            today = time.strftime("%d.%m.%Y")
            for chat_id in self.chat_ids:
                bdays = self.load(chat_id)
                if today in bdays:
                    bdmsg = "%s has/have birthday today! 🍰🙌🎂🎈🎉🕯🎁" % ', '.join(bdays[today])
                    self.bot.sendMessage(chat_id, bdmsg)
            time.sleep(seconds_until())  # sleep until 9 o'clock

    def load(self, chat_id):
        bdays = {}
        try:
            with open(os.path.join(self.data_dir, "chat_%d.txt" % chat_id), 'r') as f:
                for line in f:
                    date, names = line.strip().split(' = ')
                    bdays[date] = names.split(',')
        except IOError as e:
            print("Could not load file: %s occured." % e)
        return bdays

    def save(self, chat_id, bdays):
        with open(os.path.join(self.data_dir, "chat_%d.txt" % chat_id), 'w') as f:
            f.write('\n'.join("%s = %s" % (d, ','.join(n)) for d, n in bdays.items()))

    def load_chat_ids_bday(self):
        try:
            with open(os.path.join(self.data_dir, "chat_ids.txt")) as f:
                self.chat_ids = list(map(int, f))
        except IOError as e:
            print("Could not load chat_id file: %s occured." % e)

    def add_chat_id(self, chat_id):
        self.chat_ids.append(chat_id)
        open(os.path.join(self.data_dir, "chat_%d.txt" % chat_id), 'a').close()
        with open(os.path.join(self.data_dir, "chat_ids.txt"), 'a') as f:
            print(chat_id, file=f)
