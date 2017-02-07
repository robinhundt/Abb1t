import telepot
import logging
from util.msg import Msg
from util.core import yn
import time
import sys

class Telegrambot:
    def __init__(self, api_key, mods_, whitelist, overseer):
        self.api_key = api_key
        self.bot = telepot.Bot(self.api_key)
        self.overseer = overseer
        logging.debug(self.bot.getMe())
        self.reactiontime = 10 # messages older than this won't be answered

        self.mods=[]
        for m in mods_:
            exec("import mods.{}".format(m)) # totally insecure
            logging.debug("exec mod=mods.{0}.{0}(self)".format(m))
            exec("mod=mods.{0}.{0}(self)".format(m))
            self.mods.append(locals()['mod'])
            # if feedback from the mod is needed
            # start a thread here, e.g.
            # thread.start_new_thread(self.modHandling,(mod,))
            # to use this, use queue_out in each mod
        import ast #json would require strings as keys
        self.whitelist=ast.literal_eval(whitelist)


        self.bot.message_loop(self.recv)

    def recv(self,msg):
        logging.debug(msg)

        # the util msg is created once! for all mods.
        # please copy it in the mod before editing
        util_msg = Msg(msg)

        chat_id = util_msg.get_chat_id()
        chat_type = util_msg.get_chat_type()
        msg_date = util_msg.get_date()
        message_id = util_msg.get_message_id()

        if chat_id in self.whitelist:
            if self.overseer and chat_type=="private":
                # report messages to overseer
                self.bot.sendMessage(self.overseer,msg)
                self.bot.forwardMessage(self.overseer,chat_id,message_id)
            for m in self.mods:
                if type(m).__name__ not in self.whitelist[chat_id]:
                    if time.time()-msg_date<self.reactiontime:
                        m.enqueue(util_msg)

        # whitelist set, but not empty
        elif self.whitelist:
            if self.overseer:
                # report messages to overseer
                self.bot.sendMessage(self.overseer,msg)
            if chat_type != "private":
                # leave the chat, you're not allowed to be in there
                self.bot.leaveChat(chat_id)
                return
            else:
                # maybe learn how often someone tries to talk to you
                # block if over threshold
                pass

        #simply allow everything, autoleave disabled therefore.
        else:
            if time.time()-msg_date<self.reactiontime:
                for m in self.mods:
                    m.enqueue(util_msg)

def save_config(config, name):
    with open(name,"w") as fw:
        config.write(fw)

def main(args):
    ### Set debugging level ###
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    import configparser #python3

    ### Reading out config file ###
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.section:
        if not args.section in config.sections():
            logging.warning("Section {} unexistent. Adding it.".format(args.section))
            config.add_section(args.section)
            save_config(config, args.config)
    else:
        args.section="DEFAULT"


    logging.debug("Starting up.")
    try:
        api_key=config[args.section]["API-key"] # note that configs are case INsensitive
        logging.debug(" -- using API-key: {}".format(api_key))
    except KeyError:
        api_key=input("No api-key set. Please create one and enter it now: ")
        config.set(args.section,"API-key",api_key)
        save_config(config, args.config)

    try:
        mods=config[args.section]["mods"].split(',')
        logging.debug(" -- using mods: {}".format(mods))
    except KeyError:
        mods=input("No modules set to be loaded. Please list them separated by commas, e.g.: mod1,mod2,mod3:\n").replace(" ","").strip(",")
        config.set(args.section,"mods",mods)
        mods=mods.split(",")
        save_config(config, args.config)

    # this is a blacklist within a whitelist
    # if the id is in the list, it is allowed to use the mods
    # if a mod is listed in the whitelist, it is blacklisted
    # {id:[]} would therefore allow usage of all mods for id
    whitelist="{}"
    try:
        whitelist=config[args.section]["whitelist"]
        logging.debug(" -- using whitelist: {}".format(whitelist))
    except KeyError:
        config.set(args.section,"whitelist",whitelist)
        save_config(config, args.config)
        logging.critical("No whitelist set. Allowing all messages for now. This message won't be shown again for section {}.".format(args.section))

    overseer=0
    try:
        overseer=config[args.section]["overseer"]
        logging.debug(" -- using overseer: {}".format(overseer))
    except KeyError:
        logging.critical("No overseer set. Starting the bot to set this.")
        b=telepot.Bot(api_key)
        try:
            b.getMe()
        except (telepot.exception.UnauthorizedError, telepot.exception.BadHTTPResponse):
            logging.critical("API-key is wrong. Please save the correct one in your {} !".format(args.config))
            if yn("Erase old one for the next time?"):
                config.remove_option(args.section, "api-key")
                save_config(config, args.config)
            return
        logging.critical("To register your ID, simply -private- message the bot now. You have got 65535 seconds to do so...")
        msgs=b.getUpdates(timeout=65535)
        m=Msg(msgs[0]["message"])
        while not yn("Is this your Telegram name? \"{} {}\"".format(m.get_from_first_name(),m.get_from_last_name())):
            logging.critical("ACKing all messages, retrying. Send a new message please (Timeout again 65535 secs.)")
            m=Msg(b.getUpdates(offset=msgs[~0]["update_id"]+1,timeout=65535)[0]["message"])
        overseer=m.get_from_id()
        config.set(args.section,"overseer",str(overseer))
        save_config(config, args.config)

    ### Start up ###
    bot=Telegrambot(api_key, mods, whitelist, overseer)

    while True:
        try:
            cmd = input("> ")
            if cmd == "exit":
                return
            elif cmd == "help":
                print("Commands available:")
                print("\texit\t\texits the python script")
                print("\thelp\t\tshows this help")
        except (EOFError, KeyboardInterrupt, SystemError):
            sys.exit("\nGoodbye.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", type=str, help="name of the config file", required=False, default="config.ini")
    parser.add_argument("-s","--section", type=str, help="section to be used out of the config", required=False, default="")
    parser.add_argument("-d","--debug", action='store_true', help='enable debug messages', required=False)
    args=parser.parse_args()
    main(args)
