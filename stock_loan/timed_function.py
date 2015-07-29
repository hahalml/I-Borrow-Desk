from __future__ import print_function
import time


def timer(f):
    def decorated(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f.__name__ + ' took %s seconds' % (te - ts))
        return result

    return decorated
