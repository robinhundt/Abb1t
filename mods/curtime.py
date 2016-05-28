#essential
try:
    import thread #python2
except ImportError:
    import _thread as thread #python3
try:
    from Queue import * #python2
except ImportError:
    from queue import * #python3
import time


class curtime(object):
    def __init__(self, bot):
        self.bot = bot
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        self.resttime=0
        self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            recv_id=msg['from']['id']
            if msg['text']=="/time":
                self.bot.sendMessage(recv_id,"Current time is {}".format((time.strftime("%H:%M:%S"))))

    def enqueue(self,msg):
        self.queue_in.put(msg)