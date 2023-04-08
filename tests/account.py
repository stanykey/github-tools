from pathlib import Path
from unittest import main
from unittest import TestCase

from github_tools.internal.account import Account


class AccountTestCase(TestCase):
    def test_create(self) -> None:
        self.assertEqual(
            Account(name="first", cert_file=Path("./fake-cert-path")),
            Account.create(name="first", cert_file="./fake-cert-path"),
        )

    def test_integrity(self) -> None:
        self.assertFalse(Account.create("", "").is_valid())
        self.assertFalse(Account.create("test", "").is_valid())

        self.assertTrue(Account(name="test", cert_file=Path(__file__)).is_valid())
        self.assertTrue(Account.create("test", __file__).is_valid())

        self.assertFalse(Account.create("test", "/fake/test/path").is_valid())


if __name__ == "__main__":
    main()
