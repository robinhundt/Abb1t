#essential
import _thread as thread
from queue import *
import re

#mod
from util.msg import Msg
import os
import gzip
import json
from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine

class abb1t:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*abb1t* - talk with me by using my name (or abb0t/abbit/abbot)"
        self.queue_in=Queue()
        self.logpath="logs"
        self.archives = [int(f.replace(".gz","")) for f in os.listdir(self.logpath) if os.path.isfile(os.path.join(self.logpath, f)) and not f=="example.gz"]
        self.blacklist = ["voted so far"]
        #self.vectorizer = TfidfVectorizer(min_df=1)
        self.create_speech() # creates self.speech and self.mat, could be returned if you think its more beautiful
        #self.queue_out=Queue()
        #self.resttime=0
        #self.lastcmd=0
        thread.start_new_thread(self.run,())

    def generate_answer(self, msg_text, chat_id):
        minimum_index=[1-(10**(-5)),-1] # min value / minimum index
        t=self.vectorizer[chat_id].transform([msg_text]).toarray()[0]
        for i,t2 in enumerate(self.mat[chat_id].toarray()):
            w=cosine(t,t2)
            if abs(w)<=minimum_index[0]:
                if minimum_index[0] == abs(w): # equal weight, lets take the longer message
                    if len(self.speech[chat_id][0][i]) > len(self.speech[chat_id][0][minimum_index[1]]):
                        minimum_index[1] = i
                else: #not equal, take the lower weight
                    minimum_index[0] = w
                    minimum_index[1] = i

        if minimum_index[1]==-1 or minimum_index[0]>0.85: # no message found or score too bad
            return ""

        from_sent_id = self.speech[chat_id][1][minimum_index[1]]
        for i in range(1,5):
            try:
                if from_sent_id != self.speech[chat_id][1][minimum_index[1]+i]:
                    return self.speech[chat_id][0][minimum_index[1]+i]
            except IndexError:
                return ""
        return ""


    def find_name(self, msg_text):
        return msg_text.find("abb1t")>=0 or msg_text.find("abbit")>=0 or msg_text.find("abb0t")>=0 or msg_text.find("abbot")>=0

    def is_blacklisted(self, text):
        for b in self.blacklist:
            if b.lower() in text:
                return True
        return False

    def replace_name(self, msg_text):
        return msg_text.replace("abb1t","").replace("abbit","").replace("abb0t","").replace("abbot","")

    def create_speech(self):
        self.speech = dict.fromkeys(self.archives,[]) 
        #blacklist=[] # ids to be ignored, not implemented yet
        self.vectorizer = dict.fromkeys(self.archives,[])
        self.mat = dict.fromkeys(self.archives,[])
        for key in self.speech:
            self.speech[key]=[[],[]] # messages / ids / (maybe timestamps?)
            self.vectorizer[key]=CountVectorizer(min_df=1)
            if key >=0:
                continue # why create dictionaries for private messages right now...
            logfile="{}.gz".format(os.path.join(self.logpath,str(key)))
            try:
                ziplines=gzip.open(logfile).read().decode("utf-8").strip("\r\n").split("\n")[-15000:]
            except IOError:
                print("{} not found".format(logfile))
                continue
            prev_id = -1
            for msg_line in ziplines:
                msg = Msg(json.loads(msg_line))
                text=msg.get_text()
                chat_id=msg.get_chat_id()
                if (key != chat_id):
                    input("Error in your logfile!")
                sent_id=msg.get_sent_id()
                if text and text[0] not in ["/","!"]  and msg.get_edit_date()==0 and not self.is_blacklisted(text) and (not self.find_name(text)) and chat_id and sent_id: #sadly, @like will come through
                    if sent_id == prev_id:
                        self.speech[key][0][-1]+="\n{}".format(text)
                    else:
                        self.speech[key][0].append(text)
                        self.speech[key][1].append(sent_id)
                    prev_id = sent_id
            self.mat[key]=self.vectorizer[key].fit_transform(self.speech[key][0])

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            chat_type=msg.get_chat_type()
            msg_text=msg.get_text().lower()
            if self.find_name(msg_text) and chat_id and chat_type!="private":
                reply = self.generate_answer(self.replace_name(msg_text),chat_id)
                if reply:
                    self.bot.sendMessage(chat_id,reply,reply_to_message_id= msg.get_message_id())

    def enqueue(self,msg):
        self.queue_in.put(msg)
