from rest_framework import serializers
from .models import User, Promo_Account

class UserSerializer(serializers.ModelSerializer):
  """Serializes a Genuine Apparel User"""

  class Meta:
    model = User
    fields = ('id', 'username', 'password', 'email')

class PromoSerializer(serializers.ModelSerializer):
  """Serializes a User's Promo Account"""
  class Meta:
    model = Promo_Account
    fields = ('promo_username', 'password', 'activated', 'proxy', 'target_account', 'user', 'to_run_at')
