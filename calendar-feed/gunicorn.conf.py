# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 2
worker_class = "gevent"
worker_connections = 1000
timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"
