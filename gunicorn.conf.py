bind = "127.0.0.1:9000"                   # Don't use port 80 becaue nginx occupied it already. 
errorlog = '/Users/captncarty/Desktop/Portfolio/MacCAFE/logs/gunicorn-error.log'  # Make sure you have the log folder create
accesslog = '/Users/captncarty/Desktop/Portfolio/MacCAFE/logs/gunicorn-access.log'
loglevel = 'debug'
workers = 2 
