# essential
import _thread as thread
import re
from queue import *

# mod
import urbandict as ud


class urbandict:

    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/ud* _<term>_ - defines _<term>_ using the urbandictionary"
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())
        # self.output_example = False

    def run(self):
        while True:
            msg = self.queue_in.get()  # get() is blocking
            match = re.search(r'^\/ud (.*)$', msg.get_text().lower())
            if match:
                self.bot.sendMessage(msg.get_chat_id(), self.decide(match))

    @staticmethod
    def decide(match):
        definition = ud.define(match.group(1))[0]['def']
        if "There aren't any definitions for" in definition:
            return "No definition found."
        return definition

    def enqueue(self, msg):
        self.queue_in.put(msg)
