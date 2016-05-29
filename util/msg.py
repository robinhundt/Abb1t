class Msg:
    """docstring for msg"""
    def __init__(self, raw_msg):
        self.raw_msg=raw_msg


    """get the id of the person that sent the message"""
    def get_sent_id(self):
        try:
            return self.raw_msg['from']['id']
        except KeyError:
            return ''

    """get the id of the group/person that the message was sent in"""
    def get_chat_id(self):
        try:
            return self.raw_msg['chat']['id']
        except KeyError:
            return ''

    """get the text of the message"""
    def get_text(self):
        try:
            return self.raw_msg['text']
        except KeyError:
            return ''