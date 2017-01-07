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

class open_id:
    """ a decorator for passing files to save and load functions.

    Maybe this is an overkill, but I was bored.
    """
    def __init__(self, mode):
        self.mode = mode

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            try:
                fp = open(
                    os.path.join(args[0].data_dir, "chat_%d.txt" % args[1]),
                    self.mode
                )
                args = [args[0], fp] + list(args[2:])
                # Make function call and return value
                return func(*args, **kwargs)
            except IOError as err:
                io_action = 'read' if self.mode == 'r' else 'write to'
                print("Could not %s file: %s occured." % (io_action, err))
            finally:
                fp.close()
        return wrapped

class bday:

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = r"*/bday* (insert|remove) _<name>_ _<dd.mm>_ - Add or remove a person to the daily birthday reminder"
        self.queue_in = Queue()
        self.data_dir = 'bdays'
        self.chat_ids = []

        # runs for the first time
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(os.path.join(self.data_dir, "chat_ids.txt")):
            open(os.path.join(self.data_dir, "chat_ids.txt"), 'a').close()

        # load previously contacted chats
        self.load_chat_ids_bday()

        thread.start_new_thread(self.run, ())
        thread.start_new_thread(self.happy_birthday, ())

    def enqueue(self, msg):
        self.queue_in.put(msg)

    def run(self):
        while True:
            message = self.queue_in.get()  # get() is blocking
            message_text = message.get_text()
            chat_id = message.get_chat_id()
            regex = re.compile(r'^([!\/]bday) (insert|remove) ([\w ]{2,30}) ([\.0-9]{5})$')
            match = re.search(regex, message_text)
            if match and match.group(2) == 'insert':
                date = match.group(4)
                name = match.group(3).title()
                try:
                    time.strptime(date, '%d.%m')
                except ValueError as err:
                    self.bot.sendMessage(chat_id, "Wrong date format or date does not exist.")
                    continue

                # parsing was ok so we can continue
                if not chat_id in self.chat_ids:
                    self.add_chat_id(chat_id)
                bdays = self.load(chat_id)
                if not date in bdays:
                    bdays[date] = [name]
                else:
                    bdays[date].append(name)
                self.save(chat_id, bdays)
                self.bot.sendMessage(chat_id, "Got it.")

    def happy_birthday(self):
        while True:
            today = time.strftime("%d.%m")
            for chat_id in self.chat_ids:
                bdays = self.load(chat_id)
                if today in bdays:
                    bdmsg = "*{}* {} birthday today! 🍰🙌🎂🎈🎉🕯🎁".format(', '.join(bdays[today]),"has" if len(bdays[today])==1 else "have")
                    self.bot.sendMessage(chat_id, bdmsg, parse_mode="Markdown")
            time.sleep(seconds_until())  # sleep until 9 o'clock

    @open_id('r')
    def load(self, chat_id_file):
        bdays = {}
        for line in chat_id_file:
            date, names = line.strip().split(' = ')
            bdays[date] = names.split(',')
        return bdays

    @open_id('w')
    def save(self, chat_id_file, bdays):
        chat_id_file.write('\n'.join("%s = %s" % (d, ','.join(n)) for d, n in bdays.items()))

    def load_chat_ids_bday(self):
        with open(os.path.join(self.data_dir, "chat_ids.txt")) as f:
            self.chat_ids = [int(line) for line in f]

    def add_chat_id(self, chat_id):
        self.chat_ids.append(chat_id)
        open(os.path.join(self.data_dir, "chat_%d.txt" % chat_id), 'a').close()
        with open(os.path.join(self.data_dir, "chat_ids.txt"), 'a') as f:
            print(chat_id, file=f)
