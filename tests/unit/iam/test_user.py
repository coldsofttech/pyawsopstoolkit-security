import unittest
from unittest.mock import patch

from pyawsopstoolkit_security.iam import User


class TestUser(unittest.TestCase):
    def setUp(self) -> None:
        from pyawsopstoolkit.account import Account
        from pyawsopstoolkit.session import Session

        self.profile_name = 'temp'
        self.account = Account('123456789012')
        self.session = Session(profile_name=self.profile_name)
        self.user = User(session=self.session)

    def test_initialization(self):
        self.assertEqual(self.user.session, self.session)

    def test_setters(self):
        from pyawsopstoolkit.session import Session

        new_session = Session(profile_name='sample')
        self.user.session = new_session
        self.assertEqual(self.user.session, new_session)

    def test_invalid_types(self):
        invalid_session = 123

        with self.assertRaises(TypeError):
            User(session=invalid_session)
        with self.assertRaises(TypeError):
            self.user.session = invalid_session

    @patch('boto3.Session')
    def test_users_without_permissions_boundary_no_iam_users_returned(self, mock_session):
        session_instance = mock_session.return_value
        session_instance.client.return_value.list_buckets.return_value = {}

        self.assertEqual(len(self.user.users_without_permissions_boundary()), 0)

    @patch('boto3.Session')
    @patch('pyawsopstoolkit_advsearch.iam.User')
    def test_users_without_permissions_boundary_no_users_matching_criteria(self, mock_iam, mock_session):
        from pyawsopstoolkit_models.iam.user import User
        from pyawsopstoolkit_models.iam.permissions_boundary import PermissionsBoundary

        session_instance = mock_session.return_value
        session_instance.client.return_value.list_buckets.return_value = {}

        mock_iam.return_value.search_users.return_value = [
            User(
                account=self.account,
                name='test_user',
                id='ABCDEFGH',
                arn=f'arn:aws:iam::{self.account.number}:user/test_user',
                permissions_boundary=PermissionsBoundary(
                    type='Policy',
                    arn=f'arn:aws:iam::{self.account.number}:policy/some_boundary'
                )
            )
        ]

        self.assertEqual(len(self.user.users_without_permissions_boundary()), 0)

    @patch('boto3.Session')
    @patch('pyawsopstoolkit_advsearch.iam.User')
    def test_users_without_permissions_boundary_some_users_matching_criteria(self, mock_iam, mock_session):
        from pyawsopstoolkit_models.iam.user import User
        from pyawsopstoolkit_models.iam.permissions_boundary import PermissionsBoundary

        session_instance = mock_session.return_value
        session_instance.client.return_value.list_buckets.return_value = {}

        mock_iam.return_value.search_users.return_value = [
            User(
                account=self.account,
                name='test_user1',
                id='ABCDEFGH',
                arn=f'arn:aws:iam::{self.account.number}:user/test_user1',
                permissions_boundary=PermissionsBoundary(
                    type='Policy',
                    arn=f'arn:aws:iam::{self.account.number}:policy/some_boundary'
                )
            ),
            User(
                account=self.account,
                name='test_user2',
                id='BCDGHEY',
                arn=f'arn:aws:iam::{self.account.number}:user/test_user2'
            ),
            User(
                account=self.account,
                name='test_user3',
                id='CDGHFYU',
                arn=f'arn:aws:iam::{self.account.number}:user/test_user3'
            )
        ]

        users = self.user.users_without_permissions_boundary()

        self.assertEqual(len(users), 2)
        self.assertTrue(all(user.permissions_boundary is None for user in users))


if __name__ == "__main__":
    unittest.main()
