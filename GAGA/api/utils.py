import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GAGA.settings')
django.setup()

from redis import Redis
from datetime import datetime, timedelta
import pytz
from pytz import timezone
from rq import Queue
from random import randint
import requests
from .models import User
from .models import Promo_Account
from .models import Commented_On_Account

LAMBDA_URL = 'https://7r2oqaxnxb.execute-api.us-east-1.amazonaws.com/default/InstaBot'

redis_server = Redis()
queue = Queue(connection=redis_server)

def add_to_queue(promo_username, promo_password, promo_target, promo_proxy, to_run_at):
  print(f'adding {promo_username} to queue at ', to_run_at)

  print('TO RUN AT: >>>', to_run_at)
  queue.enqueue_in(timedelta(minutes=0), comment_round, promo_username, promo_password, promo_target, promo_proxy)




def comment_round(promo_username, promo_password, promo_target, promo_proxy):
  print('called func<<<<<<')
  print(f'''Comment round for {promo_username} with password: {promo_password},
  targeting: {promo_target}, with proxy: {promo_proxy}''')

  promo_account = Promo_Account.objects.get(promo_username=promo_username)
  print(promo_account.user)

  accounts_already_commented_on = promo_account.user.commented_on_account_set.all()
  print(accounts_already_commented_on)
  print(list(accounts_already_commented_on))


  #to run at = response from aws -> get the finish time from the last comment
  promo_attributes = {
    'username': promo_username,
    'password': promo_password,
    'target': promo_target,
    'proxy': promo_proxy
  }

  #requests.post(LAMBDA_URL, json=promo_attributes)

  continue_queue(promo_username, promo_password, promo_target, promo_proxy)

def continue_queue(promo_username, promo_password, promo_target, promo_proxy):
  print('continuing queue')
  queue.enqueue_in(timedelta(minutes=randint(160,200)), comment_round, promo_username, promo_password, promo_target, promo_proxy)

