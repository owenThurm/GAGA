from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from .serializers import UserSerializer, PromoSerializer
from . import models
from .utils import add_to_queue
from datetime import datetime
import pytz


# Create your views here.

class UserAPIView(views.APIView):
  """APIView for Users"""

  serializer_class = UserSerializer

  def get_queryset(self):
    return models.User.objects.all()

  def get(self, request, format=None):
    try:
      user_id = request.query_params['id']
      if(user_id != None):
        user = models.User.objects.get(id=user_id)
        serializer = UserSerializer(user)
    except Exception as e:
      print(e)
      users = self.get_queryset()
      serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



  def post(self, request, format=None):
    print('called post, request: ', request.data)
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'saved', 'data': serializer.data})
    else:
      return Response({"message": "invalid user", "data": serializer.data})

class PromoAPIView(views.APIView):
  """APIView for Promo Accounts"""

  serializer_class = PromoSerializer

  def get_queryset(self):
    return models.Promo_Account.objects.all()

  def get(self, request, format=None):
    try:
      promo_id = request.query_params['id']
      if(promo_id != None):
        promo_account = models.Promo_Account.objects.get(id=promo_id)
        serializer = PromoSerializer(promo_account)
    except Exception as e:
      print(e)
      promo_accounts = self.get_queryset()
      serializer = PromoSerializer(promo_accounts, many=True)
    return Response(serializer.data)


  def post(self, request, format=None):
    '''post a promo and add it to the recurring queue.
    to_run_at must be in utc time!'''
    serializer = PromoSerializer(data=request.data)
    time_to_run = datetime.strptime(request.data['to_run_at'], '%Y-%m-%dT%H:%M')
    add_to_queue(request.data['username'], request.data['password'],
     request.data['target_account'], request.data['proxy'],
      time_to_run)

    if serializer.is_valid():
      serializer.save()
      return Response({"message": "saved", "data": serializer.data})
    else:
      return Response({"message": "invalid", "data": serializer.errors})
