from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework import (
    viewsets,
    views,
    generics
)
from rest_framework.response import Response

from accounts.models import BankAccount, BalanceAction
from accounts.serializers import (
    BankAccountSerializer,
    UserSerializer,
    BalanceActionSerializer,
    TransferSerializer
)
from accounts.services import (
    transfer_money
)

User = get_user_model()


class BankAccountViewSet(viewsets.ModelViewSet):
    """
    list: Get list of all bank accounts.

    retrieve: Get information about single bank account entry with it's balance.

    create: Create a new bank account for the user.
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    http_method_names = ['get', 'post', 'head']

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(BankAccountViewSet, self).list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """
    list: Get list of all existing users.

    retrieve: Get information about specific user.

    create: Create new user-customer or user-staff (available only for superusers).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head']

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(UserViewSet, self).list(request, *args, **kwargs)


class TransferApiView(generics.CreateAPIView):
    """Make transfer between two users. Create transfer history entry."""
    serializer_class = TransferSerializer

    def post(self, request, *args, **kwargs):
        from_account_pk = kwargs.get('pk')
        transfer_amount = self.request.data.get('amount', 0)
        to_account_pk = self.request.data.get('transferee', None)
        try:
            from_account_pk, to_account_pk = int(from_account_pk), int(to_account_pk)
        except ValueError:
            from_account_pk, to_account_pk = None, None
        content, status = transfer_money(from_account_pk, to_account_pk, transfer_amount)
        return Response(content, status=status)


class BalanceHistoryApiView(generics.ListAPIView):
    """Return bank transfer history for a specific user."""
    serializer_class = BalanceActionSerializer

    def get_queryset(self):
        return BalanceAction.objects.filter(bank_account_id=self.kwargs.get('pk'))

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(BalanceHistoryApiView, self).list(request, *args, **kwargs)
