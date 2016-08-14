#essential
import _thread as thread
from queue import *
import re

#mod
import gtts
import tempfile

class voice:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/voice* _<message>_ - using gTTS a voice message of _<message>_ is created"
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            if re.search(r'^(?:/|!)voice ', msg.get_text().lower()) and len(msg.get_text().split(" "))>=2:
                tts=msg.get_text().split(" ",1)[1].lower().replace("Ä","ae").replace("ä","ae").replace("Ü","ue").replace("ü","ue").replace("Ö","oe").replace("ö","oe").replace("ß","ss")
                with tempfile.TemporaryFile() as temporaryfile:
                    gtts.gTTS(text=tts,lang="de").write_to_fp(temporaryfile)
                    temporaryfile.seek(0)
                    self.bot.sendAudio(chat_id,temporaryfile,title="Abb1tvoice")

    def enqueue(self,msg):
        self.queue_in.put(msg)
