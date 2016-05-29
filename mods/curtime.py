#essential
import _thread as thread
from queue import *

class curtime(object):
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
            recv_id=msg.get_recv_id()
            if msg.get_text()=="/time":
                self.bot.sendMessage(recv_id,"Current time is {}".format((time.strftime("%H:%M:%S"))))

    def enqueue(self,msg):
        self.queue_in.put(msg)