import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GAGA.settings')
django.setup()

from .services.promo_account_service import PromoAccountService
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
import logging

LAMBDA_URL = 'https://7r2oqaxnxb.execute-api.us-east-1.amazonaws.com/default/InstaBot'

logging.basicConfig(filename='/logs/workerlogs', level=logging.DEBUG)

redis_server = Redis()
queue = Queue(connection=redis_server)

def add_to_queue(promo_username, promo_password, promo_target, promo_proxy):
  logging.debug(f'adding {promo_username} to queue at ')
  queue.enqueue_in(timedelta(minutes=0), comment_round, promo_username, promo_password, promo_target, promo_proxy)

def comment_round(promo_username, promo_password, promo_target, promo_proxy):
  logging.debug('called func<<<<<<')
  logging.debug(f'''Comment round for {promo_username} with password: {promo_password},
  targeting: {promo_target}, with proxy: {promo_proxy}''')

  promo_account = Promo_Account.objects.get(promo_username=promo_username)
  logging.debug('promo account user: ',  promo_account.user)

  if not promo_account.is_queued:
    return

  accounts_already_commented_on = []

  for commented_on_account in promo_account.user.commented_on_account_set.all():
    accounts_already_commented_on.append(commented_on_account.commented_on_account_username)

  comment_rounds_today = promo_account.comment_rounds_today
  logging.debug('Comment Rounds Today: ', comment_rounds_today)

  #to run at = response from aws -> get the finish time from the last comment
  promo_attributes = {
    'promo_username': promo_username,
    'promo_password': promo_password,
    'target_account': promo_target,
    'proxy': promo_proxy,
    'accounts_already_commented_on': accounts_already_commented_on
  }

  if promo_account.activated:
    logging.debug('comment round ran>>>')
    requests.post(LAMBDA_URL, json=promo_attributes)

  promo_account.comment_rounds_today += 1
  promo_account.save()
  logging.debug('comment rounds today: ', promo_account.comment_rounds_today)
  sleep_until_tomorrow = False
  if promo_account.comment_rounds_today >= 8:
    sleep_until_tomorrow = True
    promo_account.comment_rounds_today = 0
    promo_account.save()

  continue_queue(promo_username, promo_password, promo_target, promo_proxy, sleep_until_tomorrow)

def continue_queue(promo_username, promo_password, promo_target, promo_proxy, sleep_until_tomorrow):
  logging.debug('continuing queue')
  if sleep_until_tomorrow:
    queue.enqueue_in(timedelta(hours=13, minutes=randint(10, 50)), comment_round, promo_username, promo_password, promo_target, promo_proxy)

  else:
    queue.enqueue_in(timedelta(minutes=randint(80,100)), comment_round, promo_username, promo_password, promo_target, promo_proxy)
