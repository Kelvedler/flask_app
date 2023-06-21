bind = "0.0.0.0:8000"
x_forwarded_for_header = "X-Real-IP"
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = 'debug'
