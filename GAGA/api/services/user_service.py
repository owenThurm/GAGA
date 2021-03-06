from ..models import User, CustomComment, EmailValidationToken, UserManager, CommentFilter
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
from datetime import datetime
from .. import serializers
from django.utils.functional import cached_property
import pytz
import smtplib

utc = pytz.UTC

class UserService():

  @cached_property
  def promo_account_service(self):
    from .promo_account_service import PromoAccountService

    return PromoAccountService()

  def _get_user_by_username(self, user_username):
    return User.objects.get(username=user_username)

  def _get_user_by_email(self, user_email):
    return User.objects.get(email=user_email)

  def _get_user_by_id(self, user_id):
    return User.objects.get(id=user_id)

  def _get_user_set(self):
    return User.objects.all()

  def get_user_set(self):
    users = self._get_user_set()
    user_set_serializer = serializers.UserSerializer(users, many=True)
    user_set = user_set_serializer.data
    return user_set

  def get_user_id_from_username(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.id

  def get_user_username_from_email(self, user_email):
    return self._get_user_by_email(user_email).username

  def update_user_comment_pool_setting(self, user_username, using_custom_comments):
    user = self._get_user_by_username(user_username)
    user.using_custom_comments = using_custom_comments
    user.save()
    return user.using_custom_comments

  def user_is_using_custom_comment_pool(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.using_custom_comments

  def user_is_custom_comment_eligible(self, user_username):
    user_custom_comment_pool = self.get_user_custom_comment_pool(user_username)
    return len(user_custom_comment_pool) >= 25

  def get_user_custom_comment_pool(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.customcomment_set.all()

  def get_user_custom_comments_text(self, user_username):
    comment_pool = self.get_user_custom_comment_pool(user_username)
    comment_pool_text = []
    for comment in comment_pool:
      comment_pool_text.append(comment.comment_text)
    return comment_pool_text

  def get_user_custom_comment_id(self, user_username, custom_comment_text):
    user_custom_comment_pool = self.get_user_custom_comment_pool(user_username)
    for custom_comment in user_custom_comment_pool:
      if custom_comment.comment_text == custom_comment_text:
        return custom_comment.id
    return None

  def add_to_user_custom_comment_pool(self, user_username, new_custom_comments):
    for custom_comment_text in new_custom_comments:
      self.add_custom_comment(user_username, custom_comment_text)

  def add_custom_comment(self, user_username, custom_comment_text):
    user = self._get_user_by_username(user_username)
    custom_comment = CustomComment(user=user, comment_text=custom_comment_text)
    custom_comment.save()
    return custom_comment.comment_text

  def _get_custom_comment_by_id(self, id):
    return CustomComment.objects.get(id=id)

  def _get_user_custom_comment(self, user_username, custom_comment_text):
    user_custom_comment_pool = self.get_user_custom_comment_pool(user_username)
    for custom_comment in user_custom_comment_pool:
      if custom_comment.comment_text == custom_comment_text:
        return custom_comment

  def delete_custom_comment(self, user_username, custom_comment_text):
    custom_comment = self._get_user_custom_comment(user_username, custom_comment_text)
    custom_comment_id = custom_comment.id
    custom_comment.delete()
    return custom_comment_id

  def update_custom_comment_text(self, user_username, old_custom_comment_text, new_custom_comment_text):
    custom_comment = self._get_user_custom_comment(user_username, old_custom_comment_text)
    custom_comment.comment_text = new_custom_comment_text
    custom_comment.save()
    return custom_comment.comment_text

  def comments_are_unique(self, user_username, new_custom_comments):
    user_custom_comment_pool = self.get_user_custom_comment_pool(user_username)
    user_custom_comment_set = set()
    for custom_comment in user_custom_comment_pool:
      user_custom_comment_set.add(custom_comment.comment_text.replace(" ", ""))
    for new_custom_comment in new_custom_comments:
      new_custom_comment = new_custom_comment.replace(" ", "")
      if new_custom_comment in user_custom_comment_set:
        return False
      else:
        user_custom_comment_set.add(new_custom_comment)
    return True

  def comment_is_empty(self, custom_comment_text):
    return custom_comment_text == '' or custom_comment_text == None

  def any_comments_are_empty(self, custom_comments_text):
    for custom_comment_text in custom_comments_text:
      if self.comment_is_empty(custom_comment_text):
        return True
    return False

  def authenticate_user(self, user_email, user_password):
    if authenticate(email=user_email, password=user_password):
      return self.get_user_username_from_email(user_email)
    else:
      return None

  def get_duplicate_comment(self, user_username, new_custom_comments):
    user_custom_comment_pool = self.get_user_custom_comment_pool(user_username)
    user_custom_comment_set = set()
    for custom_comment in user_custom_comment_pool:
      user_custom_comment_set.add(custom_comment.comment_text.replace(" ", ""))
    for new_custom_comment in new_custom_comments:
      new_custom_comment = new_custom_comment.replace(" ", "")
      if new_custom_comment in user_custom_comment_set:
        return new_custom_comment
      else:
        user_custom_comment_set.add(new_custom_comment)
    return None

  def generate_token(self, user_username):
    user = self._get_user_by_username(user_username)
    auth_token = Token.objects.get_or_create(user=user)
    return auth_token[0].key

  def get_identity_from_token(self, user_token):
    token = Token.objects.get(key=user_token)
    user_id = token.user_id
    user = self._get_user_by_id(user_id)
    return (user.username, user.email)

  def token_matches_email(self, email, user_token):
    (user_username, user_email) = self.get_identity_from_token(user_token)
    if email == user_email:
      return user_username
    else:
      return None

  def _get_email_validation_token_from_key(self, email_validation_token_key):
    return EmailValidationToken.objects.get(key=email_validation_token_key)

  def generate_email_validation_token_for_user(self, user_username):
    user = self._get_user_by_username(user_username)
    random_token_string = get_random_string(length=32)
    email_validation_token = EmailValidationToken(user=user, key=random_token_string)
    email_validation_token.save()
    return random_token_string

  def email_validation_token_is_valid(self, email_validation_token_key):
    token = self._get_email_validation_token_from_key(email_validation_token_key)
    current_time = datetime.now().replace(tzinfo=utc)
    valid_until_time = token.valid_until.replace(tzinfo=utc)
    return current_time < valid_until_time

  def get_user_username_from_email_validation_token(self, email_validation_token_key):
    token = self._get_email_validation_token_from_key(email_validation_token_key)
    return token.user.username

  def reset_user_password(self, user_username, new_password):
    user_manager = UserManager()
    user_manager.set_password(user_username, new_password)
    return new_password

  def delete_email_validation_token(self, email_validation_token_key):
    token = self._get_email_validation_token_from_key(email_validation_token_key)
    token.delete()
    return email_validation_token_key

  def get_user_stats(self, user_username):
    all_time_num_comments = self.get_user_all_time_num_comments(user_username)
    user_promo_accounts_comment_level = self.get_user_promo_accounts_with_comment_levels(user_username)

    return {
      "all_time_num_comments": all_time_num_comments,
      "user_promo_accounts_comment_level": user_promo_accounts_comment_level
    }

  def _get_user_commented_on_accounts(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.commented_on_account_set.all()

  def get_user_all_time_num_comments(self, user_username):
    return len(self._get_user_commented_on_accounts(user_username))

  def _get_user_promo_accounts(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.promo_account_set.all()

  def get_user_promo_accounts_usernames(self, user_username):
    user_promo_accounts = self._get_user_promo_accounts(user_username)
    promo_account_usernames = []
    for promo_account in user_promo_accounts:
      promo_account_usernames.append(promo_account.promo_username)
    return promo_account_usernames

  def get_user_promo_accounts_with_comment_levels(self, user_username):
    user_promo_accounts = self.get_user_promo_accounts_usernames(user_username)

    promo_accounts_with_comment_levels = map(
      self._make_promo_account_comment_level_tuple, user_promo_accounts
    )
    return promo_accounts_with_comment_levels

  def _make_promo_account_comment_level_tuple(self, promo_account):
    promo_account_comment_level = self.promo_account_service.get_promo_comment_level(promo_account)
    return (promo_account, promo_account_comment_level)

  def _get_user_comment_filter(self, user):
    comment_filter = CommentFilter.objects.get(user=user)
    return {
      'account_min_followers': comment_filter.account_min_followers,
      'account_max_followers': comment_filter.account_max_followers,
      'account_min_number_following': comment_filter.account_min_number_following,
      'account_max_number_following': comment_filter.account_max_number_following,
      'account_description_avoided_key_phrases': comment_filter.account_description_avoided_key_phrases,
      'post_min_number_of_comments': comment_filter.post_min_number_of_comments,
      'post_max_number_of_comments': comment_filter.post_max_number_of_comments,
      'post_min_number_of_likes': comment_filter.post_min_number_of_likes,
      'post_max_number_of_likes': comment_filter.post_max_number_of_likes,
      'post_description_avoided_key_phrases': comment_filter.post_description_avoided_key_phrases,
    }

  def _get_user_email_validated(self, user):
    return user.validated_email

  def get_user_email_validated(self, user_username):
    user = self._get_user_by_username(user_username)
    return user.validated_email

  def get_user_data(self, user_username):
    user = self._get_user_by_username(user_username)
    user_promo_accounts = self.get_user_promo_accounts(user_username)
    user_total_comments = self.get_user_all_time_num_comments(user_username)
    user_custom_comments = self.get_user_custom_comments_text(user_username)
    user_comment_filter = self._get_user_comment_filter(user)
    user_email_validated = self._get_user_email_validated(user)
    user_data = {
      "user_username": user.username,
      "user_email": user.email,
      "user_date_joined": user.date_joined,
      "user_last_login": user.last_login,
      "user_is_admin": user.is_admin,
      "user_is_superuser": user.is_superuser,
      "user_is_staff": user.is_staff,
      "user_is_active": user.is_active,
      "user_brand_name": user.brand_name,
      "user_location": user.location,
      "user_using_custom_coments": user.using_custom_comments,
      "user_total_comments": user_total_comments,
      "user_custom_comment_pool": user_custom_comments,
      "user_comment_filter": user_comment_filter,
      "user_promo_accounts": user_promo_accounts,
      "user_email_validated": user_email_validated,
    }
    return user_data

  def get_user_promo_accounts(self, user_username):
    user = self._get_user_by_username(user_username)
    user_promo_accounts = user.promo_account_set.all()
    user_promo_objects = map(self._get_promo_object, user_promo_accounts)
    return user_promo_objects

  def _get_promo_object(self, promo_account):
    promo_username = promo_account.promo_username
    promo_total_comments = self.promo_account_service.get_promo_total_comments_num(promo_username)
    promo_comment_level = self.promo_account_service.get_promo_comment_level(promo_username)
    return {
      "promo_username": promo_account.promo_username,
      "promo_password": promo_account.promo_password,
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

  def get_username_from_email(self, user_email):
    user = self._get_user_by_email(user_email)
    return user.username

  def update_user_comment_filter(self, user_username, new_comment_filter):
    user = self._get_user_by_username(user_username)
    comment_filter = CommentFilter.objects.get(user=user)
    comment_filter_object = self._get_user_comment_filter(user)
    if comment_filter_object != new_comment_filter:
      comment_filter.account_min_followers = new_comment_filter['account_min_followers']
      comment_filter.account_max_followers = new_comment_filter['account_max_followers']
      comment_filter.account_min_number_following = new_comment_filter['account_min_number_following']
      comment_filter.account_max_number_following = new_comment_filter['account_max_number_following']
      comment_filter.account_description_avoided_key_phrases = new_comment_filter['account_description_avoided_key_phrases']
      comment_filter.post_min_number_of_comments = new_comment_filter['post_min_number_of_comments']
      comment_filter.post_max_number_of_comments = new_comment_filter['post_max_number_of_comments']
      comment_filter.post_min_number_of_likes = new_comment_filter['post_min_number_of_likes']
      comment_filter.post_max_number_of_likes = new_comment_filter['post_max_number_of_likes']
      comment_filter.post_description_avoided_key_phrases = new_comment_filter['post_description_avoided_key_phrases']
      comment_filter.save()
    return new_comment_filter

  def get_user_comment_filter(self, user_username):
    user = self._get_user_by_username(user_username)
    comment_filter_object = CommentFilter.objects.get(user=user)
    return {
      'account_min_followers': comment_filter_object.account_min_followers,
      'account_max_followers': comment_filter_object.account_max_followers,
      'account_min_number_following': comment_filter_object.account_min_number_following,
      'account_max_number_following': comment_filter_object.account_max_number_following,
      'account_description_avoided_key_phrases': comment_filter_object.account_description_avoided_key_phrases,
      'post_min_number_of_comments': comment_filter_object.post_min_number_of_comments,
      'post_max_number_of_comments': comment_filter_object.post_max_number_of_comments,
      'post_min_number_of_likes': comment_filter_object.post_min_number_of_likes,
      'post_max_number_of_likes': comment_filter_object.post_max_number_of_likes,
      'post_description_avoided_key_phrases': comment_filter_object.post_description_avoided_key_phrases,
    }

  def create_default_comment_filter_for_user(self, user_username):
    #no-op if a user already has a comment filter
    user = self._get_user_by_username(user_username)
    try:
      comment_filter = CommentFilter.objects.get(user=user)
    except Exception as e:
      comment_filter = CommentFilter(user=user)
      comment_filter.save()
    return comment_filter

  def add_commented_on_accounts(self, user_username, promo_username, commented_on_accounts):
    promo_account_id = self.promo_account_service.get_promo_account_id(promo_username)
    user_id = self.get_user_id_from_username(user_username)
    for account in commented_on_accounts:
      commented_on_account_data = {
          'commented_on_account_username': account,
          'promo_account': promo_account_id,
          'user': user_id
        }
      commented_on_account_serializer = serializers.CommentedAccountSerializer(data=commented_on_account_data)
      if commented_on_account_serializer.is_valid():
        commented_on_account_serializer.save()
      else:
        print('invalid', commented_on_account_data)
        print(commented_on_account_serializer.data, commented_on_account_serializer.errors)
    return commented_on_accounts

  def _get_email_validation_token_object(self, email_validation_token):
    return EmailValidationToken.objects.get(key=email_validation_token)

  def email_validation_token_matches_user_email(self, user_email, email_validation_token):
    user_username = self.get_user_username_from_email(user_email)
    email_validation_token_object = self._get_email_validation_token_object(email_validation_token)
    email_validation_token_user_username = email_validation_token_object.user.username
    return email_validation_token_user_username == user_username

  def send_register_email_validation_email(self, user_email):
    user_username = self.get_user_username_from_email(user_email)
    email_validation_token = self.generate_email_validation_token_for_user(user_username)
    user_login_with_email_validation_url = 'https://growthautomation.netlify.com/login?token='+email_validation_token
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login('genuineapparelsuccess@gmail.com', 'ntdqiwzyasuvpruo')

      subject = 'Growth Automation Email Verification'
      body = f'Follow this link to verify your email!\n{user_login_with_email_validation_url}'

      msg = f'Subject: {subject}\n\n{body}'

      smtp.sendmail('genuineapparelsuccess@gmail.com', user_email, msg)

  def set_email_validated(self, user_username, email_validated):
    user = self._get_user_by_username(user_username)
    user.email_validated = email_validated
    user.save()
    return email_validated