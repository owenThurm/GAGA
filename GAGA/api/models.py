from django.db import models

# Create your models here.
class User(models.Model):
  username = models.CharField(max_length=15, unique=True, default=1)
  password = models.CharField(max_length=15)
  email = models.EmailField(max_length=100, unique=True)

  def __str__(self):
    return self.username

class Promo_Account(models.Model):
  promo_username = models.CharField(max_length=20, unique=True)
  promo_password = models.CharField(max_length=20)
  to_run_at = models.DateTimeField()
  activated = models.BooleanField(default=False)
  proxy = models.CharField(max_length=120)
  target_account = models.CharField(max_length=20)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.username

class Commented_On_Account(models.Model):
  username = models.CharField(max_length=20)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.username