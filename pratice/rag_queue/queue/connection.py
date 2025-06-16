# https://python-rq.org/

from redis import Redis
from rq import Queue

queue = Queue(connection=Redis())
