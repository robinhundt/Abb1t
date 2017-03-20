# essential
import _thread as thread
from queue import *
import re

# mod
import wikipedia

class wiki:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/wiki* _<term>_ - defines _<term>_ using wikipedia"
        self.queue_in = Queue()
        thread.start_new_thread(self.run, ())
        # self.output_example = False

    def run(self):
        while True:
            msg = self.queue_in.get()  # get() is blocking
            match = re.search(r'^(?:/|!)wiki (.*)$', msg.get_text().lower())
            if match:
                reply = ""
                try:
                    related_entries = wikipedia.search(match.group(1))
                    w = wikipedia.page(match.group(1))
                    reply1 = "*{}*\n".format(w.title)
                    reply2= "{}\n".format(w.summary)
                    reply3= "\n*related topics*:\n-{}".format("\n- ".join(related_entries))

                    if len(reply1+reply2+reply3)>4096:
                        reply = reply1 + reply2[:4092-len(reply1)-len(reply3)]+"...\n" + reply3 # shortening to 4096 characters
                    else:
                        reply = reply1+reply2+reply3
                except:
                    reply = "No matches returned for this request."
                if reply:
                    self.bot.sendMessage(msg.get_chat_id(), reply, parse_mode="Markdown")

    def enqueue(self, msg):
        self.queue_in.put(msg)