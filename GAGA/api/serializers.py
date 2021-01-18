from rest_framework import serializers
from .models import User, Promo_Account, Commented_On_Account

class UserSerializer(serializers.ModelSerializer):
  """Serializes a Genuine Apparel User"""

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'brand_name', 'password')

  def create(self, validated_data):
    user = User.objects.create_user(
      validated_data['email'],
      validated_data['username'],
      validated_data['brand_name'],
      validated_data['password']
    )

    return user

class PromoSerializer(serializers.ModelSerializer):
  """Serializes a User's Promo Account"""
  class Meta:
    model = Promo_Account
    fields = ('promo_username', 'promo_password', 'activated', 'proxy', 'target_account', 'user', 'to_run_at')

class CommentedAccountsSerializer(serializers.Serializer):
  """Serializes accounts commented on for a given user"""
  promo_username = serializers.CharField(max_length=30)
  commented_on_accounts = serializers.ListSerializer(child=serializers.CharField())

class CommentedAccountSerializer(serializers.ModelSerializer):
  """Serializes a commented on account"""
  class Meta:
    model = Commented_On_Account
    fields = ('commented_on_account_username', 'user')

class AuthenticationSerializer(serializers.Serializer):
  """Serializes authentication request bodies"""
  email = serializers.CharField(max_length=30)
  password = serializers.CharField(max_length=15)

  class ActivationSerializer(serializers.Serializer):
    """Serializers a promo account acitvation/deactivation call"""
    promo_username = serializers.CharField(max_length=30)