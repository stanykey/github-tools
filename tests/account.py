import unittest
from pathlib import Path

from github_tools.internal.account import Account


class AccountTestCase(unittest.TestCase):
    def test_create(self) -> None:
        self.assertEqual(
            Account(name="first", cert_file=Path("./fake-cert-path")),
            Account.create(name="first", cert_file="./fake-cert-path"),
        )


if __name__ == "__main__":
    unittest.main()
