from django.urls import path, include
from rest_framework import routers

from accounts import views

router = routers.DefaultRouter()
router.register('bankaccounts', views.BankAccountViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bankaccounts/<int:pk>/transfer_to/<int:to_account_pk>/', views.TransferApiView.as_view()),
    path('bankaccounts/<int:pk>/history/', views.BalanceHistoryApiView.as_view()),
]
