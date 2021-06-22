from django.urls import path, include
from rest_framework import routers

from accounts.views import BankAccountViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('bankaccounts', BankAccountViewSet)
router.register('users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
