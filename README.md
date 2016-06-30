# Abb1t / Abbit
**Modular-telegram-bot** (formerly known as Abb0t or Abbot) 

### Why?

If you are using Telegram you might have seen, that bots are omnipresent and able to simplify tasks and lookups. Abb1t is such a bot, that is implemented in python3. It is designed to be modular. So it is easy to create a new mod without changing anything within other files. Please have a look at `./mods/template.py` which demonstrates a template mod/plugin.

### How?

##### Dependencies

Be sure, that you have the python library called `telepot` (version 7.1) installed. This can be done by using

```
# pip3 install 'telepot==7.1'
```

Libraries used by different modules are: `urbandict`, `textblob`, `gtts`, `sklearn`(including `scipy`). Be sure to install them, if you want to use the corresponding modules.


##### Installation

Just clone or download the repository. Afterwards, create an `API-key` by using the Telegram BotFather (Have a look at https://core.telegram.org/bots).

Now run it with:

```
$ python3 ./main.py
```
    
It uses argparse, so that you can easily change between configs, e.g.:

```
$ python3 ./main.py -h
  
usage: main.py [-h] [-c CONFIG] [-s SECTION] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        name of the config file
  -s SECTION, --section SECTION
                        section to be used out of the config
  -d, --debug           enable debug messages
```

All settings of the config will be asked on startup. However, this is how a `config.ini` could look like:

```
[DEFAULT]
API-key=135792468:ABCDE1_2abcdefghiJK3_45abcdef
mods=curtime,log,sub,mensa,translate,voice,urbandict,help
whitelist={123456789:[],-987654321:["curtime"]}
overseer=1234567
```

`mods` clarify which mods are supposed to be loaded on startup.

Furthermore, the `whitelist` is a list, to allow specific Telegram IDs to use mods. If the array to the corresponding ID is empty, it is allowed to use **all** mods. So it is a blacklist within a whitelist. If the bot is added to a group, it will automatically leave, if it is not listed in the whitelist. 

*All* unpermitted usages will be reported to the `overseer` as well as "private" messages to the bot.

### TL;DR

Clone repo and start with `$ python3 ./main.py`.

### FAQ

Why is only python3 supported?
> http://pythonclock.org/

### ToDo-List

- add xkcd ticker
- add voice language support

