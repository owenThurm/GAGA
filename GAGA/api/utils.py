from redis import Redis
from datetime import datetime, timedelta
import pytz
from pytz import timezone
from rq import Queue
from random import randint
import requests

LAMBDA_URL = 'https://7r2oqaxnxb.execute-api.us-east-1.amazonaws.com/default/InstaBot'

redis_server = Redis()
queue = Queue(connection=redis_server)

def add_to_queue(promo_username, promo_password, promo_target, promo_proxy, to_run_at):
  print(f'adding {promo_username} to queue at ', to_run_at)

  print('TO RUN AT: >>>', to_run_at)
  queue.enqueue_in(timedelta(minutes=1), comment_round, promo_username, promo_password, promo_target, promo_proxy)




def comment_round(promo_username, promo_password, promo_target, promo_proxy):
  print('called func<<<<<<')
  print(f'''Comment round for {promo_username} with password: {promo_password},
  targeting: {promo_target}, with proxy: {promo_proxy}''')

  #to run at = response from aws -> get the finish time from the last comment
  promo_attributes = {
    'username': promo_username,
    'password': promo_password,
    'target': promo_target,
    'proxy': promo_proxy,
  }

  requests.post(LAMBDA_URL, json=promo_attributes)

  continue_queue(promo_username, promo_password, promo_target, promo_proxy)

def continue_queue(promo_username, promo_password, promo_target, promo_proxy):
  print('continuing queue')
  queue.enqueue_in(timedelta(minutes=randint(160,200)), comment_round, promo_username, promo_password, promo_target, promo_proxy)

