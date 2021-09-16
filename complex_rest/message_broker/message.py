class Message(str):
    def __new__(cls, *args, **kwargs):
        # add key property
        key = None
        if 'key' in kwargs:
            key = kwargs['key']
            del kwargs['key']
        message = str.__new__(cls, *args, **kwargs)
        message.key = key
        return message




