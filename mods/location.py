#essential
import _thread as thread
from queue import *
import re

#mod
import time
import random
from geopy.distance import vincenty
import json

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
        self.running_games_guesses_names = {} #per group, save all guesses
        self.POINTTHRESHOLD = 1000.0
        self.scoreboard_name = "./locationgame/scoreboard.json"
        self.scoreboard = self.load_scores(self.scoreboard_name)
        #self.resttime=0
        #self.lastcmd=0

    def load_scores(self,fname):
        try:
            with open(fname) as f:
                return json.loads(f.read())
        except Exception as e:
            print("Load scores exception: {}".format(e))
        return {}

    def save_scores(self,fname):
        try:
            with open(fname,"w") as fw:
                fw.write(json.dumps(self.scoreboard))
        except Exception as e:
            print("Write scores exception: {}".format(e))

    def print_scores(self,chat_id):
        reply ="`==================`\n"
        reply+="`===Hall=of=Fame===`\n"
        reply+="`==================`\n"
        if chat_id in self.scoreboard:
            data = self.scoreboard[chat_id]
            data_sorted = sorted(data.items(), key=lambda x:x[1]['score'])
            for d in data_sorted[::-1]:
                r=d[1]
                print(r)
                #r = d[d.keys()[0]]
                reply+="{}: {} (played *{}* {}, average: {:.2f})\n".format(r['name'],r['score'],r['times'],"times" if r['times']!=1 else 'time',r['score']*1.0/r['times'])
            return reply
        else:
            return ""

    def run(self):
        while 1: 
            msg=self.queue_in.get() # get() is blocking
            chat_id=str(msg.get_chat_id())
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
                    url = self.running_games[chat_id][-1]
                    reply = "*New game started*... Guess, where this picture was taken: {}".format(url)
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
                    #print(self.running_games[chat_id][-1])
                    #self.bot.sendPhoto(chat_id,self.running_games[chat_id][-1])
            elif re.search(r'^(?:/|!)lscores$', text):
                reply = self.print_scores(chat_id)
                if reply:
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
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
                        from_id_guess = self.running_games_guesses[chat_id][guesser]['from_id']
                        results[kilometers] = [name,from_id_guess]
                    #print(results)
                    reply+="Location: *{}*\n\nResults:\n".format(self.running_games[chat_id][1])
                    participants = len(results)
                    if chat_id not in self.scoreboard:
                        self.scoreboard[chat_id] = {}
                    for i,key in enumerate(sorted(results)):
                        guesser_name = results[key][0]
                        guesser_id = str(results[key][1])
                        if participants>=3: #only if 3 or more play
                            guesser_score = 0
                            if not guesser_id in self.scoreboard[chat_id]:
                                self.scoreboard[chat_id][guesser_id] = {}
                                self.scoreboard[chat_id][guesser_id]['score'] = 0
                                self.scoreboard[chat_id][guesser_id]['times'] = 0
                            self.scoreboard[chat_id][guesser_id]['name'] = guesser_name #set this one each time
                            #scoreboard
                            if i == 0: #best one
                                self.scoreboard[chat_id][guesser_id]['score'] += 1
                                guesser_score+=1
                            if key < self.POINTTHRESHOLD: #still okay
                                self.scoreboard[chat_id][guesser_id]['score'] += 1
                                guesser_score+=1
                            if participants-1 == i: #last one
                                self.scoreboard[chat_id][guesser_id]['score'] -= 1
                                guesser_score-=1
                            self.scoreboard[chat_id][guesser_id]['times']+=1 #increment 1 for each game played
                            reply+="{0}: *{1:.2f}* km (scored *{2}*)\n".format(guesser_name,key,guesser_score)
                        else:
                            reply+="{0}: *{1:.2f}* km\n".format(guesser_name,key)
                    self.bot.sendMessage(chat_id,reply,parse_mode="Markdown")
                    self.bot.sendLocation(chat_id,dist_target[0],dist_target[1])
                    self.save_scores(self.scoreboard_name)
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
                        if from_id not in self.running_games_guesses[chat_id]:
                            self.running_games_guesses[chat_id][from_id] = {"name":name,"lat":lat,"lon":lon, "from_id":str(from_id)} #using from_id, so namechanges do not matter
                            self.bot.sendMessage(chat_id,"Thanks for your guess, {}!".format(name))

                        #print(self.running_games_guesses[chat_id][from_id])


    def enqueue(self,msg):
        self.queue_in.put(msg)
