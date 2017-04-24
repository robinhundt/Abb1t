#essential
import _thread as thread
from queue import *
import re

#mod
import time
import random
from geopy.distance import vincenty

class location:
    def __init__(self, bot):
        self.bot = bot.bot
        self.description = "*/lgame* - guess the location of a random photo, */lstop* to post results"
        self.queue_in=Queue()
        #self.queue_out=Queue()
        thread.start_new_thread(self.run,())
        self.locations = open("./locationgame/locations.csv").read().strip(" \n\r").splitlines() #id,name,lat,lon,url
        self.running_games = {} #per group, one at a time...
        self.running_games_guesses = {} #per group, save all guesses
        #self.resttime=0
        #self.lastcmd=0

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=msg.get_chat_id()
            from_id=msg.get_from_id()
            text = msg.get_text().lower()
            if re.search(r'^(?:/|!)lgame$', text):
                reply=""
                if chat_id in self.running_games:
                    reply = "Game still running..."
                else:
                    index = random.randint(0,len(self.locations)-1)
                    self.running_games[chat_id] = self.locations[index].split(";")
                    self.running_games_guesses[chat_id] = {} #each from_id has an own dict
                    reply = "*New game started*... Guess, where this picture was taken:"
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
                    #print(self.running_games[chat_id][-1])
                    self.bot.sendPhoto(chat_id,self.running_games[chat_id][-1])
            elif re.search(r'^(?:/|!)lstop$', text):
                if not chat_id in self.running_games:
                    reply = "Game not running..."
                else:
                    reply=""
                    results = {}
                    dist_target = (float(self.running_games[chat_id][2]),float(self.running_games[chat_id][3]))
                    for guesser in self.running_games_guesses[chat_id]:
                        #print(guesser, self.running_games_guesses[chat_id][guesser])
                        dist_guess = (self.running_games_guesses[chat_id][guesser]['lat'],self.running_games_guesses[chat_id][guesser]['lon'])
                        kilometers = vincenty(dist_target,dist_guess).meters / 1000.0
                        #print(kilometers)
                        name = self.running_games_guesses[chat_id][guesser]['name']
                        results[kilometers] = name
                    #print(results)
                    reply+="Location: *{}*\n\nResults:\n".format(self.running_games[chat_id][1])
                    for key in sorted(results):
                        reply+="{0}: *{1:.2f}* km\n".format(results[key],key)
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
                    self.bot.sendLocation(chat_id,reply,dist_target[0],dist_target[1])
                    del self.running_games[chat_id]
            else:
                if chat_id in self.running_games: #only take locations if game is running
                    if "location" in msg.raw_msg:
                        lat = msg.raw_msg["location"]["latitude"]
                        lon = msg.raw_msg["location"]["longitude"]
                        if "username" in msg.raw_msg["from"]:
                            name = "@{}".format(msg.get_from_username())
                        else:
                            fname = msg.get_from_first_name()
                            lname = msg.get_from_last_name()
                            name = "{} {}".format(fname,lname)
                        #print(name)
                        self.running_games_guesses[chat_id][from_id] = {"name":name,"lat":lat,"lon":lon} #using from_id, so namechanges do not matter
                        #print(self.running_games_guesses[chat_id][from_id])


    def enqueue(self,msg):
        self.queue_in.put(msg)