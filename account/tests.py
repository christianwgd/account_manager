from django.test import TestCase
from django.contrib import auth
from faker import Faker

from account.models import Account, Tenant

user_model = auth.get_user_model()

class BaseTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.tenant = Tenant.objects.create(
            name=self.fake.company(),
            domain=self.fake.domain_name(),
        )
        self.tenant.manager.add(self.user)
        self.account = Account.objects.create(
            tenant=self.tenant,
        )


class TenantModelTests(BaseTest):

    def test_tenant_str(self):
        self.assertEqual(str(self.tenant), self.tenant.name)

    def test_tenant_st_no_name(self):
        self.tenant.name = None
        self.tenant.save()
        self.assertEqual(str(self.tenant), 'Tenant')


class AccountModelTests(BaseTest):

    def test_account_str_no_name(self):
        self.assertEqual(str(self.account), 'no name')

    def test_account_str_from_username(self):
        self.account.username = self.fake.email()
        self.account.save()
        self.assertEqual(str(self.account), self.account.username)

    def test_account_str_from_name(self):
        self.account.name = self.fake.name()
        self.account.save()
        self.assertEqual(str(self.account), self.account.name)

    def test_account_full_name_no_name(self):
        self.assertEqual(self.account.full_name, 'no name')

    def test_account_full_name(self):
        self.account.first_name = self.fake.first_name()
        self.account.last_name = self.fake.last_name()
        self.account.save()
        self.assertEqual(
            self.account.full_name,
            f'{self.account.first_name} {self.account.last_name}'
        )

    def test_account_has_date(self):
        self.assertIsNotNone(self.account.date)