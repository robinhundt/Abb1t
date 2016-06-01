#essential
import _thread as thread
from queue import *

#mod
import urbandict as ud

class urbandict:
    def __init__(self, bot):
        self.bot = bot.bot
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0
        self.output_example=False

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            if msg.get_text()[:len("/ud")]=="/ud" and len(msg.get_text().split(" "))>=2:
                term=msg.get_text().split(" ",1)[1]
                term_ud=ud.define(term)
                def_ud=term_ud[0]["def"]
                def_ex=""
                if def_ud.find("There aren't any definitions")==-1:  #there is a def
                    reply=def_ud.strip("\n\r ")
                    if self.output_example:
                        reply+="\nExample: %s"%def_ex
                else: 
                    reply="No definition found."
                self.bot.sendMessage(chat_id,reply)

    def enqueue(self,msg):
        self.queue_in.put(msg)