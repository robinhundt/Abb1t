class Msg:
    """docstring for msg"""
    def __init__(self, raw_msg):
        self.raw_msg=raw_msg

    def get_recv_id(self):
        try:
            return self.raw_msg['from']['id']
        except KeyError:
            return ''

    def get_text(self):
        try:
            return self.raw_msg['text']
        except KeyError:
            return ''