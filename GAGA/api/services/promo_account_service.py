from ..models import Promo_Account

class PromoAccountService:

  def get_promo_account(self, promo_username):
    return Promo_Account.objects.get(promo_username=promo_username)

  def get_all_promo_accounts(self):
    return Promo_Account.objects.all()

  def activate_promo_account(self, promo_username):
    promo_account = self.get_promo_account(promo_username)
    if not promo_account.activated:
      promo_account.activated = True
      promo_account.save()
    return promo_account

  def deactivate_promo_account(self, promo_username):
    promo_account = self.get_promo_account(promo_username)
    if promo_account.activated:
      promo_account.activated = False
      promo_account.save()
    return promo_account

  def deactivate_all_promo_accounts(self):
    promo_accounts = self.get_all_promo_accounts()
    for promo_account in promo_accounts:
      self.deactivate_promo_account(promo_account.promo_username)

  def dequeue_promo_account(self, promo_username):
    promo_account = self.get_promo_account(promo_username)
    if promo_account.is_queued:
      promo_account.is_queued = False
      promo_account.activated = False
      promo_account.save()

    return promo_account

