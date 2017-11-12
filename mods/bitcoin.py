#essential
import _thread as thread
from queue import *
import re

#mod
import requests

class bitcoin:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/btc* - outputs the current bitcoin price"
        self.queue_in=Queue()
        self.btc_url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        #self.resttime=0
        #self.lastcmd=0

    def get_prices(self):
        try:
            ret = requests.get(self.btc_url).json()
        except Exception as e:
            return "Request failed: {}".format(e)
        if 'bpi' in ret:
            prices = ret['bpi']
            if 'EUR' in prices and 'USD' in prices:
                return "Current price is *{:.1f}* €  (*{:.1f}* $)".format(float(prices['EUR']['rate_float']),float(prices['USD']['rate_float']))
        return "Wrong or no json returned by API"
        

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            if re.search(r'^(?:/|!)btc$', msg.get_text().lower()):
                self.bot.sendMessage(chat_id,self.get_prices(),parse_mode="Markdown")

    def enqueue(self,msg):
        self.queue_in.put(msg)