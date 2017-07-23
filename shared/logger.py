import os

class Logger(object):
    def __init__(self):
        pass

    @staticmethod
    def LogDebug(msg):
        Logger._Log('[D] ' + msg)

    @staticmethod
    def LogInformation(msg):
        Logger._Log('[I] ' + msg)
    
    @staticmethod
    def LogWarning(msg):
        Logger._Log('[W] ' + msg)

    @staticmethod
    def LogError(msg):
        Logger._Log('[E] ' + msg)

    @staticmethod
    def _Log(msg):
        print(msg)
