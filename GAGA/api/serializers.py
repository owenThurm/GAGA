from rest_framework import serializers
from .models import User, Promo_Account, Commented_On_Account, CustomComment

class UserSerializer(serializers.ModelSerializer):
  """Serializes a Genuine Apparel User"""

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'brand_name', 'password', 'location', 'using_custom_comments')

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
    fields = ('promo_username', 'promo_password', 'target_accounts', 'user')

class GetPromoSerializer(serializers.ModelSerializer):
  """Serializes a User's Promo Account"""
  class Meta:
    model = Promo_Account
    fields = ('promo_username', 'promo_password', 'target_accounts',
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

class UpdatePromoSerializer(serializers.Serializer):
  """Serializes a request to update a promo account"""
  old_promo_username = serializers.CharField(max_length=30)
  new_promo_username = serializers.CharField(max_length=30)
  new_promo_password = serializers.CharField(max_length=20)
  new_promo_target = serializers.CharField(max_length=30)

class SetCommentPoolSerializer(serializers.Serializer):
  """Serializes a request to update the comment pool and account is using"""
  using_custom_comments = serializers.BooleanField()
  user_username = serializers.CharField(max_length=30)

class AddCustomCommentsSerializer(serializers.Serializer):
  """Serializes a request to add custom comments to the custom comment pool"""
  user_username = serializers.CharField(max_length=30)
  new_custom_comments = serializers.ListSerializer(child=serializers.CharField(max_length=100))

class DeleteCustomCommentSerializer(serializers.Serializer):
  """Serializes a request to delete a custom comment"""
  user_username = serializers.CharField(max_length=30)
  custom_comment_text = serializers.CharField(max_length=100)

class UpdateCustomCommentSerializer(serializers.Serializer):
  """Serializes a request to update a custom comment"""
  user_username = serializers.CharField(max_length=30)
  old_custom_comment_text = serializers.CharField(max_length=100)
  new_custom_comment_text = serializers.CharField(max_length=100)

class GetCustomCommentSerializer(serializers.ModelSerializer):
  """Serializes a response to get a custom comment"""

  class Meta:
    model = CustomComment
    fields = ('id', 'comment_text')