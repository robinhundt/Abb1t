#essential
import _thread as thread
from queue import *

#mod
import textblob

class translate:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/translate* _<message>_ - translates _<message>_ to german using textblob"
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            if re.search(r'^(?:/|!)translate ', msg.get_text().lower()) and len(msg.get_text().split(" "))>=2:
                foreign=msg.get_text().split(" ",1)[1]
                try:
                    b=textblob.TextBlob(foreign)
                    reply="{}".format(b.translate(to="de"))
                except textblob.exceptions.NotTranslated:
                    reply="Error while translation. (Are there smileys in some words?)"
                self.bot.sendMessage(chat_id,reply)

    def enqueue(self,msg):
        self.queue_in.put(msg)