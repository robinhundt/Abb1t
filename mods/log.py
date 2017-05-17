#essential
import _thread as thread
from queue import *

#mod
import gzip, os
import json
import re

class log:
    def __init__(self, bot):
        self.bot = bot.bot
        self.overseer = bot.overseer
        self.description = ""
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0
        self.logdir="logs"

        # if you restart too often, better make it permanent:
        self.message_ids = {}

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            text=msg.get_text().lower()
            from_id = msg.get_from_id()

            chat_id=msg.get_chat_id() # will be the name of the gz
            message_id=msg.get_message_id()

            try:
                os.mkdir(self.logdir)
            except:
                pass # exists already

            with gzip.open("{}.gz".format(os.path.join(self.logdir,str(chat_id))),"at") as fw:
                fw.write("{}\n".format(json.dumps(msg.raw_msg)))

            if re.search(r'^(?:/|!)undelete ', text):# and int(from_id) == int(self.overseer): # undelete messages
                try:
                    number = int(text.split(" ",1)[1])
                except Exception as e:
                    print(e)
                    continue
                self.bot.forwardMessage(chat_id,chat_id,self.message_ids[chat_id][-number])

            #append it afterwards, so the undelete message does not count
            if chat_id not in self.message_ids:
                self.message_ids[chat_id]=[]
            self.message_ids[chat_id].append(message_id)

    def enqueue(self,msg):
        self.queue_in.put(msg)
