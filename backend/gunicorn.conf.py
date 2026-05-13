bind = "127.0.0.1:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
keepalive = 5
accesslog = "/var/log/okr-app/access.log"
errorlog = "/var/log/okr-app/error.log"
loglevel = "info"
