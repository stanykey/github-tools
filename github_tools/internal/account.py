"""Account representation."""
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Self


@dataclass(frozen=True, kw_only=True, slots=True)
class Account:
    name: str
    cert_file: Path
    author: str = ""
    email: str = ""

    @classmethod
    def create(cls, name: str, cert_file: str | PathLike[str], author: str = "", email: str = "") -> Self:
        """Create an object via default ctor, but ensure that `cert_path` is an instance of pathlib.Path."""
        return cls(name=name, cert_file=Path(cert_file), author=author, email=email)
