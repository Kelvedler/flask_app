bind = "0.0.0.0:8000"
x_forwarded_for_header = "X-Real-IP"
accesslog = '-'
access_log_format = '%(t)s %({x-forwarded-for}i)s %(l)s "%(r)s" %(s)s "%(a)s"'
