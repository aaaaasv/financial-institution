from decimal import Decimal
from rest_framework import status

from accounts.models import BankAccount


def transfer_money(from_account_pk, to_account_pk, amount):
    from_account = BankAccount.objects.get(pk=from_account_pk)
    to_account = BankAccount.objects.get(pk=to_account_pk)
    if from_account == to_account:
        return 'You cannot transfer money between the same bank account', status.HTTP_403_FORBIDDEN
    amount = Decimal(amount)

    available_balance = from_account.balance
    if amount > available_balance:
        return 'Not enough money available', status.HTTP_403_FORBIDDEN

    new_from_balance = available_balance - amount
    from_account.balance = new_from_balance
    from_account.save()

    new_to_balance = to_account.balance + amount
    to_account.balance = new_to_balance
    to_account.save()

    return {'New transferer balance': new_from_balance, 'New transferee balance': new_to_balance}, status.HTTP_200_OK
