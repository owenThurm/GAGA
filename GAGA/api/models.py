from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Growth Automation Models

class UserManager(BaseUserManager):

  def create_user(self, email, username, brand_name, password):
    if not email:
      raise ValueError("Users must have an email")
    if not username:
      raise ValueError("Users must have a username")
    if not brand_name:
      raise ValueError("Users must have a brand name")
    if not password:
      raise ValueError("Users must have a password")

    user = self.model(email=self.normalize_email(email), username=username, brand_name=brand_name)

    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, username, password, brand_name='Genuine Apparel'):
    user = self.create_user(email=self.normalize_email(email), password=password,
                      username=username, brand_name=brand_name)
    user.is_admin = True
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)
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

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username", "brand_name", "password"]

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
  proxy = models.CharField(max_length=120, default=1)
  target_account = models.CharField(max_length=30)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  comment_rounds_today = models.IntegerField(default=0)
  is_queued = models.BooleanField(default=False)

  def __str__(self):
    return self.promo_username

class Commented_On_Account(models.Model):
  commented_on_account_username = models.CharField(max_length=30)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.commented_on_account_username
