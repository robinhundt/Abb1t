import telepot
import logging
from util.msg import Msg

class Telegrambot:
    def __init__(self, api_key, mods_):
        self.api_key = api_key
        self.bot = telepot.Bot(self.api_key)
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

        self.bot.message_loop(self.recv)
        while True:
            pass
        pass

    def recv(self,msg):
        logging.debug(msg)
        for m in self.mods:
            m.enqueue(Msg(msg))






def main(args):
    ### Set debugging level ###
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # the configparser depends on the python version...
    try: 
        import configparser #python3
    except ImportError:
        import ConfigParser as configparser #python2

    ### Reading out config file ###
    config = configparser.ConfigParser()
    config.read(args.config)
    if not args.section in config.sections():
        logging.warning("Section unexistent. Switching to default.")
        args.section="DEFAULT" # default is used anyway..

    logging.debug("Starting up.")
    try:
        api_key=config.get(args.section,"API-Key")
    except configparser.NoOptionError:
        logging.critical("No API-key set. Please create one and save it to config.ini.".format(args.config))
        return
    logging.debug(" -- using API-key: {}".format(api_key))

    try:
        mods=config.get(args.section,"Mods").split(',')
    except configparser.NoOptionError:
        logging.critical("No mods set. Please create one and save it to {}.".format(args.config))
        return
    logging.debug(" -- using mods: {}".format(mods))

    ### Start up ###
    bot=Telegrambot(api_key, mods)




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", type=str, help="name of the config file", required=False, default="config.ini")
    parser.add_argument("-s","--section", type=str, help="section to be used out of the config", required=False, default="DEFAULT")
    parser.add_argument("-d","--debug", action='store_true', help='enable debug messages', required=False)
    args=parser.parse_args()
    main(args)