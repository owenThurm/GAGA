from ..models import Promo_Account, User
from .user_service import UserService
from .. import serializers
from random import randint
from django.utils.functional import cached_property

class PromoAccountService:

  @cached_property
  def queue_functions(self):
    from .. import utils

    return utils

  def _get_promo_account(self, promo_username):
    return Promo_Account.objects.get(promo_username=promo_username)

  def get_promo_account_id(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.id

  def promo_is_queued(self, promo_username):
    return self._get_promo_account(promo_username).is_queued

  def get_promo_proxy(self, promo_username):
    return self._get_promo_account(promo_username).proxy

  def get_promo_password(self, promo_username):
    return self._get_promo_account(promo_username).promo_password

  def _get_promo_set(self):
    return Promo_Account.objects.all()

  def get_promo_set(self):
    promo_set = self._get_promo_set()
    promo_set_data = serializers.GetPromoSerializer(promo_set, many=True).data
    return promo_set_data

  def get_promo_account_data(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_total_comments = self.get_promo_total_comments_num(promo_username)
    promo_comment_level = self.get_promo_comment_level(promo_username)
    promo_data = {
      "promo_username": promo_account.promo_username,
      "promo_is_activated": promo_account.activated,
      "promo_proxy": promo_account.proxy,
      "promo_target_accounts": promo_account.target_accounts,
      "promo_owner": promo_account.user.username,
      "promo_comment_rounds_today": promo_account.comment_rounds_today,
      "promo_is_queued": promo_account.is_queued,
      "promo_under_review": promo_account.under_review,
      "promo_comments_until_sleep": promo_account.comments_until_sleep,
      "promo_is_liking": promo_account.is_liking,
      "promo_total_comments": promo_total_comments,
      "promo_comment_level": promo_comment_level,
      "promo_is_disabled": promo_account.is_disabled,
    }
    return promo_data

  def get_promo_targets(self, promo_username):
    return self._get_promo_account(promo_username).target_accounts

  def get_next_promo_target(self, promo_username):
    return self.get_promo_targets(promo_username)[0] if self.get_promo_targets(promo_username) else ''

  def set_promo_targeting_list(self, promo_username, target_accounts):
    promo_account = self._get_promo_account(promo_username)
    promo_account.target_accounts = target_accounts
    promo_account.save()

  def rotate_promo_targets(self, promo_username):
    promo_targets = self.get_promo_targets(promo_username)
    rotated_promo_targets = []
    rotated_target = promo_targets[0]
    for i in range(0, len(promo_targets)-1):
      rotated_promo_targets.append(promo_targets[i+1])
    rotated_promo_targets.append(rotated_target)
    self.set_promo_targeting_list(promo_username, rotated_promo_targets)

  def get_next_target_account_and_rotate(self, promo_username):
    target_account = self.get_next_promo_target(promo_username)
    self.rotate_promo_targets(promo_username)
    return target_account

  def get_all_promo_accounts(self):
    return Promo_Account.objects.all()

  def activate_promo_account(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    if not promo_account.activated:
      promo_account.activated = True
      promo_account.save()
    return promo_account

  def deactivate_promo_account(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    if promo_account.activated:
      promo_account.activated = False
      promo_account.save()
    return promo_account

  def deactivate_all_promo_accounts(self):
    promo_accounts = self.get_all_promo_accounts()
    for promo_account in promo_accounts:
      self.deactivate_promo_account(promo_account.promo_username)

  def dequeue_promo_account(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    if promo_account.is_queued:
      promo_account.is_queued = False
      promo_account.activated = False
      promo_account.save()

    return promo_account

  def delete_promo_account(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_account.delete()

  def _get_promo_account_owner(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.user

  def get_promo_account_owner_username(self, promo_username):
    return self._get_promo_account_owner(promo_username).username

  def get_promo_account_owner_id(self, promo_username):
    return self._get_promo_account_owner(promo_username).id

  def _get_user_from_username(self, user_username):
    return User.objects.get(username=user_username)

  def get_user_id_from_username(self, user_username):
    return self._get_user_from_username(user_username).id

  def create_promo_account(self, promo_username, promo_password, promo_target, promo_owner_username):
    promo_owner = self._get_user_from_username(promo_owner_username)
    promo_account = Promo_Account(promo_username=promo_username, promo_password=promo_password,
                                 target_account=promo_target, user=promo_owner)
    promo_account.save()
    return promo_account

  def update_promo_account(self, old_promo_username, new_promo_username, new_promo_password, new_promo_targets):
    promo_account = self._get_promo_account(old_promo_username)
    if promo_account.promo_username != new_promo_username:
      promo_account.promo_username = new_promo_username
    if promo_account.promo_password != new_promo_password:
      promo_account.promo_password = new_promo_password
    if promo_account.target_accounts != new_promo_targets:
      promo_account.target_accounts = new_promo_targets
    if promo_account.activated == True:
      promo_account.activated = False
    if promo_account.under_review == False:
      promo_account.under_review = True
    if promo_account.is_queued == True:
      promo_account.is_queued = False
    promo_account.save()
    return promo_account

  def get_accounts_already_commented_on(self, promo_username):
    commented_on_account_list = []
    for commented_on_account in list(self._get_promo_account_owner(promo_username).commented_on_account_set.all()):
      commented_on_account_list.append(commented_on_account.commented_on_account_username)
    return commented_on_account_list

  def get_comment_rounds_today(self, promo_username):
    return self._get_promo_account(promo_username).comment_rounds_today

  def get_custom_comments(self, promo_username):
    user_service = UserService()
    promo_owner_username = self.get_promo_account_owner_username(promo_username)
    return user_service.get_user_custom_comments_text(promo_owner_username)

  def promo_account_is_activated(self, promo_username):
    return self._get_promo_account(promo_username).activated

  def increment_comment_rounds_today(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_account.comment_rounds_today += 1
    promo_account.save()
    return promo_account.comment_rounds_today

  def reset_daily_comment_round_count(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_account.comment_rounds_today = 0
    promo_account.save()
    return promo_account.comment_rounds_today

  def get_promo_comment_level(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.comment_level

  def _get_promo_number_of_comments_done(self, promo_account):
    return len(promo_account.commented_on_account_set.all())

  def update_promo_comment_level(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_account_number_comments_done = self._get_promo_number_of_comments_done(promo_account)
    promo_increment_comment_level_comment_number = promo_account.increment_comment_level_comment_number
    promo_comment_level = promo_account.comment_level
    if promo_comment_level >= 12:
      return promo_comment_level
    if promo_account_number_comments_done > promo_increment_comment_level_comment_number:
      promo_increment_comment_level_comment_delta = promo_account.increment_comment_level_comment_delta
      promo_account.comment_level = promo_comment_level + 1
      promo_account.increment_comment_level_comment_number = promo_increment_comment_level_comment_number + promo_increment_comment_level_comment_delta
      promo_account.save()
      return promo_comment_level + 1
    return promo_comment_level

  def subtract_comments_from_comments_until_sleep(self, promo_username, commented_on_accounts_list):
    promo_account = self._get_promo_account(promo_username)
    number_of_comments_to_subtract = len(commented_on_accounts_list)
    promo_account_comments_until_sleep = promo_account.comments_until_sleep
    print(number_of_comments_to_subtract)
    promo_account.comments_until_sleep = promo_account_comments_until_sleep - number_of_comments_to_subtract
    promo_account.save()
    print(promo_account.comments_until_sleep)
    return promo_account.comments_until_sleep

  def promo_should_sleep_a_day(self, promo_username):
    return self.get_promo_comments_until_sleep(promo_username) <= 0

  def get_promo_comments_until_sleep(self, promo_username):
    return self._get_promo_account(promo_username).comments_until_sleep

  def reset_promo_comments_until_sleep(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    random_comments_until_sleep = randint(800, 1400)
    promo_account.comments_until_sleep = random_comments_until_sleep
    promo_account.save()
    return random_comments_until_sleep

  def promo_account_is_liking(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.is_liking

  def set_promo_is_liking(self, promo_username, is_liking):
    promo_account = self._get_promo_account(promo_username)
    if promo_account.is_liking != is_liking:
      promo_account.is_liking = is_liking
      promo_account.save()
    return is_liking

  def get_promo_total_comments_num(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return len(promo_account.commented_on_account_set.all())

  def _get_promo_commented_on_set(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.commented_on_account_set.all()

  def update_promo_disabled_status(self, promo_username, is_disabled):
    promo_account = self._get_promo_account(promo_username)
    promo_account.is_disabled = is_disabled
    promo_account.save()
    return is_disabled

  def promo_is_disabled(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.is_disabled

  def promo_is_under_review(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    return promo_account.under_review

  def activate_and_queue_promo_account(self, promo_username):
    promo_account = self._get_promo_account(promo_username)
    promo_account.activated = True
    if not promo_account.is_queued:
      self.queue_functions.add_to_queue(promo_username)
      promo_account.is_queued = True
    promo_account.save()
    return promo_username

  def set_promo_target_accounts_list(self, promo_username, promo_target_accounts_list):
    promo_account = self._get_promo_account(promo_username)
    if promo_account.target_accounts != promo_target_accounts_list:
      promo_account.target_accounts = promo_target_accounts_list
      promo_account.save()
    return promo_target_accounts_list