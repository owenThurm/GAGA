from rest_framework import serializers
from .models import User, Promo_Account, Commented_On_Account

class UserSerializer(serializers.ModelSerializer):
  """Serializes a Genuine Apparel User"""

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'brand_name', 'password', 'location')

  def create(self, validated_data):
    user = User.objects.create_user(
      validated_data['email'],
      validated_data['username'],
      validated_data['brand_name'],
      validated_data['password'],
      validated_data['location']
    )

    return user

class PostPromoSerializer(serializers.ModelSerializer):
  """Serializes a User's Promo Account"""
  class Meta:
    model = Promo_Account
    fields = ('promo_username', 'promo_password', 'target_account', 'user')

class GetPromoSerializer(serializers.ModelSerializer):
  """Serializes a User's Promo Account"""
  class Meta:
    model = Promo_Account
    fields = ('promo_username', 'promo_password', 'target_account',
     'user', 'activated', 'under_review', 'comment_rounds_today', 'is_queued')

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

class PromoUsernameSerializer(serializers.Serializer):
  """Serializers a promo account acitvation/deactivation call"""
  promo_username = serializers.CharField(max_length=30)

class AddProxySerializer(serializers.Serializer):
  """Serializes an add proxy/review request"""
  promo_username = serializers.CharField(max_length=30)
  proxy = serializers.CharField(max_length=120)

class GetUserPromoAccountsSerializer(serializers.Serializer):
  """Serializes a request to get the promo accounts associated with a given user"""
  username = serializers.CharField(max_length=30)

class ResetPasswordSerializer(serializers.Serializer):
  """
    Serializes a growth automation user username
    and a new growth automation user password
  """
  username = serializers.CharField(max_length=30)
  new_password = serializers.CharField(max_length=30)
