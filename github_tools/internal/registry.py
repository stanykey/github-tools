"""Simple registry based on ini/cfg files."""
from configparser import ConfigParser
from configparser import DuplicateSectionError
from configparser import ParsingError
from dataclasses import asdict
from enum import auto
from enum import IntEnum
from typing import Self
from typing import TextIO

from github_tools.internal.account import Account


Storage = ConfigParser


class ErrorCode(IntEnum):
    FileCorrupted = auto()
    DuplicateAccount = auto()
    FieldMissed = auto()
    FieldValueMissed = auto()


class RegistryError(Exception):
    """
    Exception raised for Registry class errors.

    Attributes:
        code    -- error code
        message -- explanation of the error
    """

    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class Registry:
    def __init__(self) -> None:
        self._accounts: dict[str, Account] = dict()

    @classmethod
    def load(cls, io: TextIO) -> Self:
        """Load registry from stream."""
        registry = cls()

        storage = cls._read_storage(io)
        for account_name in storage.sections():
            account = cls._read_account(account_name, storage)
            registry.add(account)

        return registry

    def save(self, io: TextIO) -> None:
        """Dump the registry to the stream in ini-format."""
        storage = Storage()
        for account in self._accounts.values():
            self._dump_account(account, storage)
        storage.write(io)

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
    def _read_storage(io: TextIO) -> Storage:
        storage = Storage()
        try:
            storage.read_file(io)
        except ParsingError:
            raise RegistryError(ErrorCode.FileCorrupted, "Registry file is corrupted")
        except DuplicateSectionError:
            raise RegistryError(ErrorCode.DuplicateAccount, "Registry file contains duplicates")
        return storage

    @staticmethod
    def _read_account(account_name: str, storage: Storage) -> Account:
        fields = storage[account_name]
        if "cert_file" not in fields:
            raise RegistryError(ErrorCode.FieldMissed, f"Field (cert_file) is missed for account ({account_name})")

        if not fields["cert_file"]:
            raise RegistryError(
                ErrorCode.FieldValueMissed, f"Field value (cert_file) is missed for account ({account_name})"
            )

        return Account.create(account_name, **fields)

    @staticmethod
    def _dump_account(account: Account, storage: Storage) -> None:
        # asdict isn't the best choice, but we don't care about performance for now
        record = {field: str(value) for field, value in asdict(account).items() if field != "name" and value}
        storage[account.name] = record
