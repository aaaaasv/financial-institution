import base64

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import BankAccount

User = get_user_model()


class TestBankAPIViews(TestCase):
    fixtures = ['user-data.json']

    def setUp(self):
        self.client_unauthorized = APIClient()
        self.client = APIClient()
        self.client_superuser = APIClient()
        self.client_staffuser = APIClient()

        self.client = self.create_authenticated_client(username='georginahazel', password='123245')
        self.client_superuser = self.create_authenticated_client(username='admin', password='12345')
        self.client_staffuser = self.create_authenticated_client(username='staffuser', password='123457')

    @staticmethod
    def create_authenticated_client(username, password):
        client = APIClient()

        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8'))
        client.credentials(HTTP_AUTHORIZATION='Basic {}'.format(credentials.decode('utf-8')))

        return client

    @staticmethod
    def create_bank_account(user, initial_balance):
        return BankAccount.objects.create(user=user, balance=initial_balance)

    def test_get_bank_accounts_with_staff_success(self):
        response = self.client_staffuser.get(reverse('bankaccount-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BankAccount.objects.count(), 0)
        self.assertEqual(len(response.data['results']), BankAccount.objects.count())
        BankAccount.objects.create(user=User.objects.first(), balance=2.3)
        cache.clear()

        response = self.client_staffuser.get(reverse('bankaccount-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BankAccount.objects.count(), 1)
        self.assertEqual(len(response.data['results']), BankAccount.objects.count())

        BankAccount.objects.create(user=User.objects.last(), balance=123.2)
        cache.clear()

        response = self.client_staffuser.get(reverse('bankaccount-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BankAccount.objects.count(), 2)
        self.assertEqual(len(response.data['results']), BankAccount.objects.count())

    def test_get_bank_accounts_with_not_staff_forbidden(self):
        response = self.client.get(reverse('bankaccount-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_bank_accounts_with_unauthorized(self):
        response = self.client_unauthorized.get(reverse('bankaccount-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_staff_user_with_staff_fail(self):
        staff_data = {
            'username': 'staffname1',
            'password': 'passw',
            'is_staff': 'true'
        }

        response = self.client_staffuser.post(reverse('user-list'), staff_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=staff_data['username']).exists())
        self.assertFalse(User.objects.get(username=staff_data['username']).is_staff)

    def test_create_staff_user_with_superuser_success(self):
        staff_data = {
            'username': 'staffname1',
            'password': 'passw',
            'is_staff': 'true'
        }

        response = self.client_superuser.post(reverse('user-list'), staff_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=staff_data['username']).exists())
        self.assertTrue(User.objects.get(username=staff_data['username']).is_staff)

    def test_create_multiply_bank_accounts(self):
        user = User.objects.first()
        initial_balance = 30.21

        self.assertEqual(user.bankaccount_set.count(), 0)
        bankaccount_data = {
            'user': user.id,
            'balance': initial_balance
        }

        response = self.client_staffuser.post(reverse('bankaccount-list'), bankaccount_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.bankaccount_set.count(), 1)

        response = self.client_staffuser.post(reverse('bankaccount-list'), bankaccount_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.bankaccount_set.count(), 2)

    def test_transfers_between_different_user_accounts(self):
        user1 = User.objects.first()
        user2 = User.objects.last()

        user1_init_balance = 50.25
        user2_init_balance = 2.5

        bank_account1 = self.create_bank_account(user1, user1_init_balance)
        bank_account2 = self.create_bank_account(user2, user2_init_balance)

        transfer_data = {'amount': 12.5, 'transferee': bank_account2.pk}
        response = self.client_staffuser.post(
            reverse('transfer', kwargs={'pk': bank_account1.pk}),
            transfer_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bank_account1.refresh_from_db()
        bank_account2.refresh_from_db()
        self.assertEqual(bank_account1.balance, user1_init_balance - transfer_data['amount'])
        self.assertEqual(bank_account2.balance, user2_init_balance + transfer_data['amount'])

    def test_transfers_between_different_user_accounts_fail_money_lack(self):
        user1 = User.objects.first()
        user2 = User.objects.last()

        user1_init_balance = 50.25
        user2_init_balance = 2.5

        bank_account1 = self.create_bank_account(user1, user1_init_balance)
        bank_account2 = self.create_bank_account(user2, user2_init_balance)

        transfer_data = {'amount': 55.5, 'transferee': bank_account2.pk}
        response = self.client_staffuser.post(
            reverse('transfer', kwargs={'pk': bank_account1.pk}),
            transfer_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        bank_account1.refresh_from_db()
        bank_account2.refresh_from_db()
        self.assertEqual(bank_account1.balance, user1_init_balance)
        self.assertEqual(bank_account2.balance, user2_init_balance)

    def test_transfers_between_same_user_accounts(self):
        user1 = User.objects.first()

        account1_init_balance = 50.25
        account2_init_balance = 2.5

        bank_account1 = self.create_bank_account(user1, account1_init_balance)
        bank_account2 = self.create_bank_account(user1, account2_init_balance)

        transfer_data = {'amount': 12.5, 'transferee': bank_account2.pk}
        response = self.client_staffuser.post(
            reverse('transfer', kwargs={'pk': bank_account1.pk}),
            transfer_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bank_account1.refresh_from_db()
        bank_account2.refresh_from_db()
        self.assertEqual(bank_account1.balance, account1_init_balance - transfer_data['amount'])
        self.assertEqual(bank_account2.balance, account2_init_balance + transfer_data['amount'])

    def check_balance_history_length(self, bank_account_pk, history_length):
        response = self.client_staffuser.get(reverse('balance-history', kwargs={'pk': bank_account_pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cache.clear()
        self.assertEqual(len(response.data['results']), history_length)

    def test_get_transaction_history(self):
        user1 = User.objects.first()
        user2 = User.objects.last()

        bank_account1 = self.create_bank_account(user1, 50.2)
        bank_account2 = self.create_bank_account(user2, 12.6)

        self.assertEqual(bank_account1.balanceaction_set.count(), 0)
        self.assertEqual(bank_account2.balanceaction_set.count(), 0)

        response = self.client_staffuser.post(
            reverse('transfer', kwargs={'pk': bank_account1.pk}),
            {'amount': 1.3, 'transferee': bank_account2.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(bank_account1.balanceaction_set.count(), 1)
        self.check_balance_history_length(bank_account1.pk, 1)
        self.assertEqual(bank_account2.balanceaction_set.count(), 1)
        self.check_balance_history_length(bank_account2.pk, 1)

        response = self.client_staffuser.post(
            reverse('transfer', kwargs={'pk': bank_account1.pk}),
            {'amount': 1.3, 'transferee': bank_account2.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(bank_account1.balanceaction_set.count(), 2)
        self.check_balance_history_length(bank_account1.pk, 2)
        self.assertEqual(bank_account2.balanceaction_set.count(), 2)
        self.check_balance_history_length(bank_account2.pk, 2)


class TestAuth(TestCase):
    fixtures = ['user-data.json']

    def setUp(self):
        self.client = APIClient()

    @staticmethod
    def get_user_data(username):
        password = '12345pass_'
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return {'username': username, 'password': password}

    def obtain_jwt_token(self, username):
        user_data = self.get_user_data(username)
        response = self.client.post(reverse('token_obtain_pair'), user_data)
        return response

    def test_jwt_obtain_token_success(self):
        response = self.obtain_jwt_token('admin')
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        response = self.client.post(reverse('token_verify'), {'token': response.data['access']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_obtain_token_fail_wrong_password(self):
        wrong_user_data = {
            'username': 'admin',
            'password': 'somewrongpassword'
        }
        response = self.client.post(reverse('token_obtain_pair'), wrong_user_data)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_use_by_superuser(self):
        token = self.obtain_jwt_token('admin').data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        user_data = {
            'username': 'newteststaffuser',
            'password': '12345ab',
            'is_staff': 'true'
        }

        self.assertFalse(User.objects.filter(username=user_data['username']).exists())
        response = self.client.post(reverse('user-list'), user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=user_data['username']).exists())

    def test_jwt_token_use_by_customer(self):
        token = self.obtain_jwt_token('arishabarron').data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        user_data = {
            'username': 'newteststaffuser',
            'password': '12345ab',
        }

        self.assertFalse(User.objects.filter(username=user_data['username']).exists())
        response = self.client.post(reverse('user-list'), user_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username=user_data['username']).exists())
