import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GAGA.settings')
django.setup()

from .services.promo_account_service import PromoAccountService
from .services.user_service import UserService
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
user_service = UserService()
promo_account_service = PromoAccountService()

def add_to_queue(promo_username):
  logging.debug(f'adding {promo_username} to queue at ', datetime.now())
  queue.enqueue_in(timedelta(minutes=0), comment_round, promo_username)

def comment_round(promo_username):

  if not promo_account_service.promo_is_queued(promo_username):
    logging.debug(f'dequeueing {promo_username}')
    return

  promo_password = promo_account_service.get_promo_password(promo_username)
  promo_target = promo_account_service.get_next_target_account_and_rotate(promo_username)
  promo_proxy = promo_account_service.get_promo_proxy(promo_username)
  accounts_already_commented_on = promo_account_service.get_accounts_already_commented_on(promo_username)
  comment_rounds_today = promo_account_service.get_comment_rounds_today(promo_username)
  promo_owner_username = promo_account_service.get_promo_account_owner_username(promo_username)
  activated = promo_account_service.promo_account_is_activated(promo_username)
  number_of_comments_to_do = promo_account_service.get_promo_comment_level(promo_username)
  is_liking = promo_account_service.promo_account_is_liking(promo_username)
  is_disabled = promo_account_service.promo_is_disabled(promo_username)
  promo_target_accounts_list = promo_account_service.get_promo_targets(promo_username)
  try:
    user_comment_filter = user_service.get_user_comment_filter(promo_owner_username)
  except Exception as e:
    user_comment_filter = None
  if(user_service.user_is_using_custom_comment_pool(promo_owner_username)):
    account_custom_comment_pool = user_service.get_user_custom_comments_text(promo_owner_username)
  else:
    account_custom_comment_pool = []

  #to run at = response from aws -> get the finish time from the last comment
  promo_attributes = {
    'promo_username': promo_username,
    'promo_password': promo_password,
    'target_account': promo_target,
    'promo_target_accounts_list': promo_target_accounts_list,
    'proxy': promo_proxy,
    'accounts_already_commented_on': accounts_already_commented_on,
    'custom_comments': account_custom_comment_pool,
    'num_comments': number_of_comments_to_do,
    'is_liking': is_liking,
    'comment_filter': user_comment_filter,
  }

  logging.debug(f'''Comment round for {promo_username}, targeting {promo_target},
  with proxy: {promo_proxy}, with custom comments: {account_custom_comment_pool}, 
  at time: {datetime.now()}''')
  logging.debug('Comment Rounds Already Today: ', comment_rounds_today)


  if activated and not is_disabled:
    logging.debug('###Lambda Called###')
    requests.post(LAMBDA_URL, json=promo_attributes)

  comment_rounds_today = promo_account_service.increment_comment_rounds_today(promo_username)
  sleep_until_tomorrow = False
  if comment_rounds_today >= 10:
    sleep_until_tomorrow = True
    promo_account_service.reset_daily_comment_round_count(promo_username)

  continue_queue(promo_username, sleep_until_tomorrow)

def continue_queue(promo_username, sleep_until_tomorrow):
  logging.debug(f'continuing queue, will sleep until tomorrow: {sleep_until_tomorrow}')
  if sleep_until_tomorrow and promo_account_service.promo_should_sleep_a_day(promo_username):
    # is going to sleep tomorrow and time to rest for a day ->
    # rest for 34.5 hours
    logging.debug(f'{promo_username} is sleeping for a day')
    promo_account_service.reset_promo_comments_until_sleep(promo_username)
    queue.enqueue_in(timedelta(hours=34, minutes=randint(0,60)), comment_round, promo_username)
  elif sleep_until_tomorrow:
    queue.enqueue_in(timedelta(hours=9, minutes=randint(30,150)), comment_round, promo_username)
  else:
    queue.enqueue_in(timedelta(minutes=randint(80,100)), comment_round, promo_username)