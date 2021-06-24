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
        fields = ('url', 'username', 'id', 'password', 'is_staff', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {
                'write_only': True,
                'help_text': ''
            }
        }

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        is_staff = False
        if user.is_superuser:
            is_staff = validated_data.get('is_staff', False)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=is_staff
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class BalanceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceAction
        fields = '__all__'


class TransferSerializer(serializers.Serializer):
    transferee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=False
    )
    amount = serializers.DecimalField(max_digits=8, decimal_places=2)
