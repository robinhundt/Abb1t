#essential
import _thread as thread
from queue import *
import re

#mod
import time
import json
import os
import util.core
import datetime

class reminder:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/remind <time> <text>* - set reminder at specified time; time has to be in the following format: dd.mm.yyyy-HH.MM, unix timestamp _or_  seconds."
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        util.core.mkdir(bot.mod_data)
        self.mod_data = os.path.join(bot.mod_data,"{}".format(self.__class__.__name__))
        util.core.mkdir(self.mod_data)
        self.reminders = self.load_reminders(self.mod_data)
        self.lowest_time = -1
        if self.reminders:
            self.remindthread=thread.start_new_thread(self.remind,())
        #self.resttime=0
        #self.lastcmd=0

    def load_reminders(self,dir):
        ret = {}
        files = os.listdir(dir)
        for f in files:
            ret[f]=json.loads(open(os.path.join(dir,f)).read())
        return ret

    def save_reminders(self,chat_id):
        try:
            with open(os.path.join(self.mod_data,chat_id),"w") as fw:
                fw.write(json.dumps(self.reminders[chat_id]))
        except Exception as e:
            print("Write reminders exception: {}".format(e))

    def find_next(self):
        lowest_time = -1
        for chat in self.reminders:
            for t in self.reminders[chat]:
                if int(t)<lowest_time or lowest_time==-1:
                    lowest_time = int(t)
                    remind_chat = chat
                    remind_for = self.reminders[chat][t]
        if lowest_time!=-1:
            return [lowest_time,remind_for,remind_chat]
        else:
            return [-1,-1,-1]

    def remind(self):
        while True:
            (self.lowest_time,remind_for,chat) = self.find_next()
            if self.lowest_time!=-1:
                sleep_for = self.lowest_time - time.time()
                if (sleep_for<=0):
                    reply="Should have reminded you for \"`{}`\" on {}, sorry...".format("`\" and \"`".join(self.reminders[chat][str(self.lowest_time)]),time.strftime("%d.%m.%Y - %H:%M:%S",time.localtime(self.lowest_time)))
                    self.bot.sendMessage(chat,reply,parse_mode="Markdown")
                    self.reminders[chat].pop(str(self.lowest_time))
                    self.save_reminders(chat)
                else:
                    time.sleep(sleep_for)
                    if self.remindthread==thread.get_ident():
                        reply="Reminder for \"`{}`\". It is now {}.".format("`\" and \"`".join(self.reminders[chat][str(self.lowest_time)]),time.strftime("%d.%m.%Y - %H:%M:%S",time.localtime(self.lowest_time)))
                        self.bot.sendMessage(chat,reply,parse_mode="Markdown")
                        self.reminders[chat].pop(str(self.lowest_time))
                        self.save_reminders(chat)
                    else:
                        # other thread took over...
                        return
            else:
                #no reminder left
                return

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=str(msg.get_chat_id())
            from_id=msg.get_from_id()
            msg_id=int(msg.get_message_id())
            text = msg.get_text().lower()
            max_length = 300
            if re.search(r'^(?:/|!)remind',text):
                ret = re.search(r'^(?:/|!)remind (\S+|\d) ([^\t\n\r\f\v]+)$', text) #*_\[\]
                if ret:
                    if len(text)>max_length:
                        reply="Please shorten your reminder. Max length is currently {} symbols.".format(max_length)
                    else:
                        reply=""
                        groups = ret.groups()
                        date = groups[0]
                        is_number = True
                        try:
                            stamp = int(date)
                        except ValueError:
                            is_number=False
                        #text = groups[1].replace("`","")#.replace("*","\*").replace("_","\_").replace("[","\[").replace("]","\]").replace("`","\`")
                        text = msg.get_text().split(" ",2)[-1].replace("`","")
                        if is_number:
                            sstamp = str(stamp)
                        else:
                            try:
                                stamp = int(time.mktime(datetime.datetime.strptime(date, "%d.%m.%Y-%H:%M").timetuple()))
                                sstamp = str(stamp)
                            except ValueError:
                                reply="No valid dateform."
                        if not reply: # error received, print it.
                            if stamp>time.time()+365*24*3600:
                                reply="Not able to safe further than one year away"
                            elif stamp<time.time() and stamp>24*3600:
                                reply="That is not in the future..."
                            elif stamp<30:
                                reply="At least 30 seconds away."
                            else:
                                if stamp<24*3600: #in stamp seconds
                                    stamp = int(time.time()+stamp)
                                    sstamp = str(stamp)
                                reply="Added your reminder \"`{}`\" for {}".format(text,time.strftime("%d.%m.%Y - %H:%M:%S",time.localtime(stamp)))
                                if chat_id not in self.reminders:
                                    self.reminders[chat_id]={}
                                if sstamp not in self.reminders[chat_id]:
                                    self.reminders[chat_id][sstamp]=[]
                                self.reminders[chat_id][sstamp].append(text)
                                self.save_reminders(chat_id)
                                if stamp<self.lowest_time or self.lowest_time==-1: #when lower, we need to start a new thread
                                    self.remindthread=thread.start_new_thread(self.remind,())
                            ##print(time.strftime("%d.%m.%Y-%H:%M",time.localtime(stamp)))
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
                    pass

    def enqueue(self,msg):
        self.queue_in.put(msg)
