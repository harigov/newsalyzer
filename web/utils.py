import os

from logger import Logger

class RetryHandler(object):
    # Retry method calls so as to improve reliability
    @staticmethod
    def retry(func, max_retries=3):
        numTries = 0
        while numTries < max_retries:
            numTries += 1
            try:
                return func()
            except Exception, e:
                Logger.LogWarning('%s retry failed with exception: %s' % (func.__name__, str(e)))
                if numTries > max_retries:
                    raise