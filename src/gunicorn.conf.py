bind = "0.0.0.0:8000"
workers = 4
x_real_ip_header = "X-Real-IP"
accesslog = '-'
access_log_format = '%(t)s %({x-real-ip}i)s %(l)s "%(r)s" %(s)s "%(a)s"'
