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
    BalanceActionSerializer
)
from accounts.services import (
    transfer_money
)

User = get_user_model()


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    http_method_names = ['get', 'post', 'head']

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(BankAccountViewSet, self).list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head']

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(UserViewSet, self).list(request, *args, **kwargs)


class TransferApiView(views.APIView):

    def post(self, request, pk, to_account_pk):
        from_account_pk = pk
        transfer_amount = self.request.data.get('amount', 0)
        content, status = transfer_money(from_account_pk, to_account_pk, transfer_amount)
        return Response(content, status=status)


class BalanceHistoryApiView(generics.ListAPIView):
    serializer_class = BalanceActionSerializer

    def get_queryset(self):
        return BalanceAction.objects.filter(bank_account_id=self.kwargs.get('pk'))

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super(BalanceHistoryApiView, self).list(request, *args, **kwargs)
