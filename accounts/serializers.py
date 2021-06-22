from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import BankAccount, BalanceAction

User = get_user_model()


class BankAccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False
    )

    class Meta:
        model = BankAccount
        fields = ('url', 'id', 'user', 'balance')

        read_only_fields = ('id',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'id',)

        read_only_fields = ('id',)


class BalanceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceAction
        fields = '__all__'
