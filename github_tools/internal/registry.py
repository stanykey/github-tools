"""Simple registry based on ini/cfg files."""
from configparser import ConfigParser
from dataclasses import asdict
from typing import Self
from typing import TextIO

from github_tools.internal.account import Account


Database = ConfigParser


class RegistryError(Exception):
    pass


class Registry:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = dict()

    @classmethod
    def load(cls, io: TextIO) -> Self:
        """Load registry from stream."""
        registry = cls()

        db = Database()
        db.read_file(io)
        for account_name in db.sections():
            account = Account.create(account_name, **db[account_name])
            if not registry.add(account):
                raise RegistryError("Registry file is corrupted")

        return registry

    def save(self, io: TextIO) -> None:
        """Dump the registry to the stream in ini-format."""
        db = Database()
        for account in self._accounts.values():
            self._dump_account(account, db)
        db.write(io)

    def add(self, account: Account, rewrite: bool = False) -> bool:
        """Add the account to the registry or replace the existing one if a *rewrite* is set to **True**."""
        if account.name in self._accounts and not rewrite:
            return False

        self._accounts[account.name] = account
        return True

    def remove(self, account: str | Account) -> bool:
        """Remove the account from the registry if present."""
        name = self._get_name(account)
        if name not in self._accounts:
            return False

        del self._accounts[name]
        return True

    def __len__(self) -> int:
        return len(self._accounts)

    def __contains__(self, account: str | Account) -> bool:
        name = self._get_name(account)
        return name in self._accounts

    @property
    def accounts(self) -> list[Account]:
        """Return list of accounts."""
        return list(self._accounts.values())

    @staticmethod
    def _get_name(account: str | Account) -> str:
        return account if isinstance(account, str) else account.name

    @staticmethod
    def _dump_account(account: Account, db: Database) -> None:
        # asdict isn't the best choice, but we don't care about performance for now
        record = {field: str(value) for field, value in asdict(account).items() if field != "name" and value}
        db[account.name] = record
