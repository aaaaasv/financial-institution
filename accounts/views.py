from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response

from accounts.models import BankAccount
from accounts.serializers import BankAccountSerializer, UserSerializer

User = get_user_model()


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    http_method_names = ['get', 'post', 'patch', 'head']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head']
