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

def add_to_queue(promo_username, promo_password, promo_target, promo_proxy):
  print(f'adding {promo_username} to queue at ')
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

  comment_rounds_today = promo_account.comment_rounds_today
  print('Comment Rounds Today: ', comment_rounds_today)

  #to run at = response from aws -> get the finish time from the last comment
  promo_attributes = {
    'promo_username': promo_username,
    'promo_password': promo_password,
    'target_account': promo_target,
    'proxy': promo_proxy
  }

  print(promo_account.activated)

  if promo_account.activated:
    print('comment round ran>>>')
    #requests.post(LAMBDA_URL, json=promo_attributes)

  promo_account.comment_rounds_today += 1
  promo_account.save()
  sleep_until_tomorrow = False
  if promo_account.comment_rounds_today >= 8:
    sleep_until_tomorrow = True
    promo_account.comment_rounds_today = 0
    promo_account.save()


  continue_queue(promo_username, promo_password, promo_target, promo_proxy, sleep_until_tomorrow)

def continue_queue(promo_username, promo_password, promo_target, promo_proxy, sleep_until_tomorrow):
  print('continuing queue')

  if sleep_until_tomorrow:
    queue.enqueue_in(timedelta(hours=16, minutes=randint(50,70)), comment_round, promo_username, promo_password, promo_target, promo_proxy)

  else:
    queue.enqueue_in(timedelta(minutes=randint(50,70)), comment_round, promo_username, promo_password, promo_target, promo_proxy)