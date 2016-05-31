#essential
import _thread as thread
from queue import *

#mod
import gzip, os
import json

class log:
    def __init__(self, bot):
        self.bot = bot
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0
        self.logdir="logs"

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            try:
                os.mkdir(self.logdir)
            except:
                pass # exists already
            chat_id=msg.get_chat_id() # will be the name of the gz
            with gzip.open("{}.gz".format(os.path.join(self.logdir,str(chat_id))),"at") as fw:
                fw.write("{}\n".format(json.dumps(msg.raw_msg)))

    def enqueue(self,msg):
        self.queue_in.put(msg)