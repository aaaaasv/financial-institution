from decimal import Decimal
from django.db import transaction
from rest_framework import status, exceptions

from accounts.models import (
    BankAccount,
    BalanceAction
)


def add_balance_action(bank_account, message):
    BalanceAction.objects.create(bank_account=bank_account, message=message)


def update_account_balance(account, add_amount):
    account.balance = account.balance + add_amount
    account.save()
    return account.balance


def transfer_money(from_account_pk, to_account_pk, amount):
    if from_account_pk == to_account_pk:
        raise exceptions.PermissionDenied(detail='You cannot transfer money between the same bank account')

    from_account = BankAccount.objects.select_related('user').get(pk=from_account_pk)
    to_account = BankAccount.objects.select_related('user').get(pk=to_account_pk)

    amount = Decimal(amount)

    available_balance = from_account.balance
    if amount > available_balance:
        raise exceptions.PermissionDenied(detail='Not enough money available')

    with transaction.atomic():
        new_from_balance = update_account_balance(from_account, -amount)
        new_to_balance = update_account_balance(to_account, amount)

        add_balance_action(from_account, f'Withdrawn {amount} for {to_account.user.username}#{to_account.id}')
        add_balance_action(to_account, f'Deposited {amount} by {from_account.user.username}#{from_account.id}')

    return {'New transferer balance': new_from_balance, 'New transferee balance': new_to_balance}
