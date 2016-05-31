import telepot
import logging
from util.msg import Msg

class Telegrambot:
    def __init__(self, api_key, mods_, whitelist, overseer):
        self.api_key = api_key
        self.bot = telepot.Bot(self.api_key)
        self.overseer = overseer
        logging.debug(self.bot.getMe())

        self.mods=[]
        for m in mods_:
            exec("import mods.{}".format(m)) # totally insecure
            logging.debug("exec mod=mods.{0}.{0}(self.bot)".format(m))
            exec("mod=mods.{0}.{0}(self.bot)".format(m))
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

        # the util msg is create once! for all mods. 
        # please copy it in the mod before editing
        util_msg = Msg(msg)

        chat_id = util_msg.get_chat_id()
        chat_type = util_msg.get_chat_type()

        if chat_id in self.whitelist:
            for m in self.mods:
                if type(m).__name__ not in self.whitelist[chat_id]:
                    m.enqueue(util_msg)

        # whitelist set, but not empty
        elif self.whitelist:
            if self.overseer:
                #report messages to overseer
                self.bot.sendMessage(self.overseer,msg)
            if chat_type != "private":
                #leave the chat, you're not allowed to be in there
                self.bot.leaveChat(chat_id)
                return
            else:
                # maybe learn how often someone tries to talk to you
                # block if over threshold
                pass

        #simply allow everything, autoleave disabled therefore.
        else: 
            for m in self.mods:
                m.enqueue(util_msg)

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
    if not args.section in config.sections():
        logging.warning("Section unexistent. Switching to default.")
        args.section="DEFAULT" # default is used anyway..

    logging.debug("Starting up.")
    try:
        api_key=config[args.section]["API-key"]
        logging.debug(" -- using API-key: {}".format(api_key))
    except configparser.NoOptionError:
        logging.critical("No API-key set. Please create one and save it to config.ini.".format(args.config))
        return

    try:
        mods=config[args.section]["mods"].split(',')
        logging.debug(" -- using mods: {}".format(mods))
    except configparser.NoOptionError:
        logging.critical("No mods set. Please create one and save it to {}.".format(args.config))
        return

    # this is a blacklist within a whitelist
    # if the id is in the list, it is allowed to use the mods
    # if a mod is listed in the whitelist, it is blacklisted
    # {id:[]} would therefore allow usage of all mods for id
    whitelist="{}"
    try:
        whitelist=config[args.section]["whitelist"]
        logging.debug(" -- using whitelist: {}".format(whitelist))
    except KeyError:
        logging.critical("No whitelist set. Please create one and save it to {}.\nAllowing all messages for now.".format(args.config))

    overseer=0
    try:
        overseer=config[args.section]["overseer"]
        logging.debug(" -- using overseer: {}".format(whitelist))
    except KeyError:
        logging.critical("No overseer set. Please save your id to {}.".format(args.config))

    ### Start up ###
    bot=Telegrambot(api_key, mods, whitelist, overseer)

    while True:
        cmd=input("> ")
        if cmd=="exit":
            return
        elif cmd=="help":
            print("Commands available:")
            print("\texit\t\texits the python script")
            print("\thelp\t\tshows this help")
    pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", type=str, help="name of the config file", required=False, default="config.ini")
    parser.add_argument("-s","--section", type=str, help="section to be used out of the config", required=False, default="DEFAULT")
    parser.add_argument("-d","--debug", action='store_true', help='enable debug messages', required=False)
    args=parser.parse_args()
    main(args)