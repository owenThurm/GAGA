from ..models import Promo_Account, User
from .user_service import UserService

class PromoAccountService:

  def _get_promo_account(self, promo_username):
    return Promo_Account.objects.get(promo_username=promo_username)

  def promo_is_queued(self, promo_username):
    return self._get_promo_account(promo_username).is_queued

  def get_promo_proxy(self, promo_username):
    return self._get_promo_account(promo_username).proxy

  def get_promo_password(self, promo_username):
    return self._get_promo_account(promo_username).promo_password

  def get_promo_targets(self, promo_username):
    return self._get_promo_account(promo_username).target_accounts

  def get_next_promo_target(self, promo_username):
    return self.get_promo_targets(promo_username)[0]

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
      commented_on_account_list.push(commented_on_account.commented_on_account_username)
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