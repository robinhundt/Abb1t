# Abb1t
**Modular-telegram-bot** (formerly known as Abb0t or Abbot) 

### Why?

If you are using Telegram you might have seen, that bots are omnipresent and able to simplify tasks and lookups. Abb1t is such a bot, that is implemented in python3. It is designed to be modular. So it is easy to create a new mod without changing anything within other files. Please have a look at `./mods/template.py` which demonstrates a template mod/plugin.

### How?

Just clone or download the repository. Afterwards, configure the `config.ini`. Here's an example:

```
[DEFAULT]
API-key=135792468:ABCDE1_2abcdefghiJK3_45abcdef
mods=curtime,log,sub,mensa,translate,voice,urbandict,help
whitelist={123456789:[],-987654321:["curtime"]}
overseer=1234567
```

The `API-key` is created by using the Telegram BotFather (Have a look at https://core.telegram.org/bots).

`mods` clarify which mods are supposed to be loaded on startup.

Furthermore, the `whitelist` is a list, to allow specific Telegram IDs to use mods. If the array to the corresponding ID is empty, it is allowed to use **all** mods. So it is a blacklist within a whitelist. If the bot is added to a group, it will automatically leave, if it is not listed in the whitelist. 

*All* not permitted usages will be reported to the `overseer` as well as "private" messages to the bot.

Finally, you are able to run it with:

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

### TL;DR

Clone, edit `./config.ini`, `$ python3 ./main.py`.

### FAQ

Why is only python3 support?
> http://pythonclock.org/
