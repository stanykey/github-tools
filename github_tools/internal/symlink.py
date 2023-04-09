"""Helper to work with symbolic file links."""
from os import PathLike
from pathlib import Path
from typing import Self

PathType = str | PathLike[str] | Path


class Symlink:
    def __init__(self, path: PathType) -> None:
        self._path = Path(path)
        if not self._path.is_symlink():
            raise ValueError(f"path ({path!s}) is not symlink")

        if not self._path.is_file():
            raise ValueError(f"path ({path!s}) is not file")

    @classmethod
    def make(cls, *, path: PathType, to: PathType, override: bool = False) -> Self:
        location = Path(path)
        if override and location.exists():
            location.unlink()

        target = Path(to)
        if target.is_dir():
            raise ValueError(f"target ({target!s}) is not file")

        location.symlink_to(target, target_is_directory=False)
        return cls(location)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: PathType) -> None:
        self._path = Path(path)

    @property
    def target(self) -> Path:
        return self._path.resolve(strict=True)

    def switch(self, to: PathType, /) -> Self:
        target = Path(to).resolve(strict=True)
        if target.is_dir():
            raise ValueError(f"target ({target!s}) is not file")

        self._path.unlink()
        self._path.symlink_to(target, target_is_directory=False)

        return self

    def __hash__(self) -> int:
        return hash(self._path)
