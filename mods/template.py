#essential
import _thread as thread
from queue import *

class template:
    def __init__(self, bot):
        self.bot = bot
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            if msg.get_text()=="/test":
                self.bot.sendMessage(chat_id,"Hello World!")

    def enqueue(self,msg):
        self.queue_in.put(msg)