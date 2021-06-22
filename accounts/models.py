from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BankAccount(models.Model):
    """Store a single bank account entry for the user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=8, decimal_places=2)


class BalanceAction(models.Model):
    """Store a single balance action entry of bank account history"""
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    performed_at = models.DateTimeField(auto_now_add=True, editable=False)
    message = models.TextField()
