#essential
import _thread as thread
from queue import *

class help:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/help* - outputs this help message"
        self.config = bot
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            chat_type=msg.get_chat_type()
            reply=""
            if re.search(r'^(?:/|!)help$', msg.get_text().lower()):
                for m in self.config.mods:
                    if chat_id in self.config.whitelist:
                        if not type(m).__name__ in self.config.whitelist[chat_id]:
                            try:
                                if (m.description): # you are able to hide modules with this
                                    reply+="\n{}".format(m.description)
                            except AttributeError:
                                reply+="\nClass *{}* has no description yet".format(type(m).__name__)
                        else:
                            print("not allowed")
            if reply:
                self.bot.sendMessage(chat_id,"*Usable modules for this {}:*{}\n(Note: ! instead of / is possible as well.)".format(("group" if chat_type=="group" else "chat"),reply),parse_mode="Markdown")

    def enqueue(self,msg):
        self.queue_in.put(msg)