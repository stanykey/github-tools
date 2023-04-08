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


if __name__ == "__main__":
    main()
