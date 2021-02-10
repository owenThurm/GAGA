from ..models import User, CustomComment
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserService():

  def _get_user_by_username(self, user_username):
    return User.objects.get(username=user_username)

  def _get_user_by_email(self, user_email):
    return User.objects.get(email=user_email)

  def _get_user_by_id(self, user_id):
    return User.objects.get(id=user_id)

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
    print(user_email)
    print(user_password)
    print(authenticate(email=user_email, password=user_password))
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