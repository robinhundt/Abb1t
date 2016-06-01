#essential
import _thread as thread
from queue import *

#mod
import urllib.request
import html.parser
import re

class mensa:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/mensa* _<day>_\n*/zmensa* _<day>_ - outputs the mensa menu for _<day>_"
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0
        self.days=["week", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        self.htmlparser=html.parser.HTMLParser()

    def format_mensa(self, content, mensa):
        app=content.split('<td class="ext_sits_speiseplan_rechts"><span class="ext_sits_essen">')
        dishes=[]
        fruits=[]
        ret = ""
        if len(app)>1:
            for i in range(1,len(app)):
                if len(app[i].split("<strong>")[1].split("</strong>")[0]): # meals
                    mens=self.htmlparser.unescape(app[i].split("<strong>")[1].split("</strong>")[0])
                    mens=''.join(mens)
                    ret+="*{}*\n".format(str(re.sub("\(.*\)","",mens)).strip(" \r\n\t"))
                if len(app[i].split("</strong>")[1].split("</span>")[0].strip("\r\n\t")) and mensa=="Nordmensa": #side dishes
                    dish=self.htmlparser.unescape(app[i].split("</strong>")[1].split("</span>")[0].strip("\r\n\t"))
                    dish=''.join(dish)
                    if dish.lower().find("verschiedene salat-")==-1 and dish.lower().find("nur solange der vor")==-1 and dish.lower().find("allergene")==-1:
                        ret+=str(re.sub("\(.*\)","",dish).replace(" ,",",")).strip(" \r\n\t")+"\n\n"
        else:
            ret+="Nothing to eat _(anymore)_ 😕"
        return ret

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            reply=""
            mensa="Nordmensa" if msg.get_text().find("/zmensa")==-1 else "Zentralmensa"
            if msg.get_text() in ["/mensa","/zmensa"]:
                reply+="*todays menu:*\n"
                link="http://www.studentenwerk-goettingen.de/speiseplan.html?selectmensa=%s"%mensa
                pagecontent=urllib.request.urlopen(link).read().decode(encoding='utf-8').strip('\n\r')
                reply+=self.format_mensa(pagecontent, mensa)
                self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
            elif msg.get_text()[:len("/mensa")]=="/mensa" or msg.get_text()[:len("/zmensa")]=="/zmensa":
                day = msg.get_text().split(" ")[1].lower()
                if day == "sunday":
                    reply+="sunday? are you serious?"
                elif day in self.days:
                    push = 0
                    day_index = self.days.index(day)
                    link="http://www.studentenwerk-goettingen.de/speiseplan.html?selectmensa=%s&push=%d&day=%d"%(mensa,push,day_index)
                    pagecontent=urllib.request.urlopen(link).read().decode(encoding='utf-8').strip('\n\r')
                    reply+="*%ss menu*:\n"%day
                    reply+=self.format_mensa(pagecontent, mensa)
                if reply:
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")

    def enqueue(self,msg):
        self.queue_in.put(msg)