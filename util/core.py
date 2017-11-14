import os

def yn(question):
    yn=""
    while not yn: # there is a library for this somewhere... too lazy right now
        try:
            yn=input("{} [y/N] ".format(question))
            if yn.lower()=="y":
                return True
            elif not yn.lower()=="n":
                yn="" #something different was entered, ask again
        except SyntaxError: #nothing entered => return False
            return False

def mkdir(dir):
    try:
        os.mkdir(dir)
    except Exception as e:
        pass #dir exists