import time

def timer(f):
	def decorated(*args, **kw):
		ts = time.time()
		result = f(*args, **kw)
		te = time.time()
		print 'Function took %s seconds' %(te - ts)
		return result

	return decorated

