import os
import sys
import time
import datetime

from flask import request

class Monitor(object):
    _client = None

    @staticmethod
    def set_telemetry_client(client):
        Monitor._client = client

    @staticmethod
    def api():
        def decorator(method):
            def wrapper(*args, **kwargs):
                if Monitor._client == None: return method(*args, **kwargs)

                event_name = 'Web_%s' % method.__name__
                startTime = int(round(time.time() * 1000))
                success = True
                try:
                    result = method(*args, **kwargs)
                    return result
                except:
                    success = False
                    Monitor._client.track_exception(*sys.exc_info())
                    Monitor._client.flush()
                    raise
                finally:
                    endTime = int(round(time.time() * 1000))
                    Monitor._client.track_event(event_name, properties = {
                        'ClientIP': request.remote_addr,
                        'Duration': endTime-startTime,
                        'Success': success
                    })
            return wrapper
        return decorator

    @staticmethod
    def internal_api():
        def decorator(method):
            def wrapper(*args, **kwargs):
                if Monitor._client == None: return method(*args, **kwargs)

                # class methods aren't bound yet so the first argument gives
                # us the class name
                event_name = '%s_%s' % (args[0].__class__.__name__, method.__name__)
                startTime = int(round(time.time() * 1000))
                success = True
                try:
                    Monitor._client.track_event(event_name)
                    result = method(*args, **kwargs)
                    return result
                except:
                    success = False
                    Monitor._client.track_exception(*sys.exc_info())
                    Monitor._client.flush()
                    raise
                finally:
                    endTime = int(round(time.time() * 1000))
                    Monitor._client.track_metric(event_name + '_TimeTaken', endTime-startTime, properties = {
                        'Success' : success
                    })
            return wrapper
        return decorator
