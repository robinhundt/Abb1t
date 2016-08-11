class Msg:
    """docstring for msg"""
    def __init__(self, raw_msg):
        self.raw_msg=raw_msg


    """get the id of the person that sent the message"""
    def get_sent_id(self):
        return self.raw_msg['from'].get('id','')

    def get_from_id(self): # the same as sent_id, just a new alias
        return self.get_sent_id()

    """get the id of the group/person that the message was sent in"""
    def get_chat_id(self):
        return self.raw_msg['chat'].get('id','')

    """get the forename of the person that sent the message"""
    def get_from_first_name(self):
        return self.raw_msg['from'].get('first_name','')

    """get the surname of the person that sent the message"""
    def get_from_last_name(self):
        return self.raw_msg['from'].get('last_name','')

    """
    get the type of the chat that the message was sent in
    this can be 'private', 'group' or 'supergroup'
    """
    def get_chat_type(self):
        return self.raw_msg['chat'].get('type','')

    """get the message_id of the chat message, to reply to it"""
    def get_message_id(self):
        return self.raw_msg.get('message_id','')

    """get the timestamp of the chat message"""
    def get_date(self):
        return self.raw_msg.get('date','')

    """get the edit timestamp of the message"""
    def get_edit_date(self):
        return self.raw_msg.get('edit_date','')

    """get the text of the message"""
    def get_text(self):
        return self.raw_msg.get('text','')