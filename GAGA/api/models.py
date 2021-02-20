from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime, timedelta

# Growth Automation Models

def default_start_time():
    now = datetime.now()
    return now + timedelta(days=1)

class UserManager(BaseUserManager):

  def create_user(self, email, username, brand_name, password, location):
    if not email:
      raise ValueError("Users must have an email")
    if not username:
      raise ValueError("Users must have a username")
    if not brand_name:
      raise ValueError("Users must have a brand name")
    if not password:
      raise ValueError("Users must have a password")

    user = self.model(email=self.normalize_email(email), username=username, brand_name=brand_name, location=location)

    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, username, password, location, brand_name='Genuine Apparel'):
    user = self.create_user(email=self.normalize_email(email), password=password,
                      username=username, brand_name=brand_name, location=location)
    user.is_admin = True
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)
    return user

  def set_password(self, username, password):
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    return user


class User(AbstractBaseUser):
  username = models.CharField(max_length=30, unique=True)
  password = models.CharField(max_length=300)
  email = models.EmailField(max_length=100, unique=True)
  date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
  last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
  is_admin = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  brand_name = models.CharField(max_length=30)
  location = models.CharField(max_length=30)
  using_custom_comments = models.BooleanField(default=False)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username", "brand_name", "password", "location"]

  objects = UserManager()

  def __str__(self):
    return self.email

  def has_perm(self, perm, obj=None):
    return self.is_admin

  def has_module_perms(self, app_label):
    return True

class Promo_Account(models.Model):
  promo_username = models.CharField(max_length=30, unique=True)
  promo_password = models.CharField(max_length=20)
  activated = models.BooleanField(default=False)
  proxy = models.CharField(max_length=120, default='0.0.0.0')
  target_accounts = ArrayField(models.CharField(max_length=30), size=8)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  comment_rounds_today = models.IntegerField(default=0)
  is_queued = models.BooleanField(default=False)
  under_review = models.BooleanField(default=True)
  comments_until_sleep = models.IntegerField(default=800)
  is_liking = models.BooleanField(default=True)

  REQUIRED_FIELDS = ["promo_username", "promo_password", "target_accounts", "user"]

  def __str__(self):
    return self.promo_username

class Commented_On_Account(models.Model):
  commented_on_account_username = models.CharField(max_length=30)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  promo_account = models.ForeignKey(Promo_Account, on_delete=models.CASCADE)

  def __str__(self):
    return self.commented_on_account_username

class CustomComment(models.Model):
  comment_text = models.CharField(max_length=100)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class ResetPasswordToken(models.Model):
  key = models.CharField(max_length=120)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  valid_until = models.DateTimeField(default=default_start_time)