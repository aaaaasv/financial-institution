from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import BankAccount, BalanceAction


class BankAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BankAccount
        fields = ('url', 'id', 'user', 'balance')

        read_only_fields = ('id',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'id',)

        read_only_fields = ('id',)


class BalanceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceAction
        fields = '__all__'
