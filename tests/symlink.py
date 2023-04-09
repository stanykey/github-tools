from pathlib import Path
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from unittest import main
from unittest import TestCase

from github_tools.internal.symlink import PathType
from github_tools.internal.symlink import Symlink


def write_file_content(file_path: PathType, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def get_file_content(file_path: PathType) -> str:
    with open(file_path, encoding="utf-8") as file:
        return file.read()


def compare_files(first: PathType, second: PathType) -> bool:
    return get_file_content(first) == get_file_content(second)


class SymlinkTestCase(TestCase):
    def test_creation(self) -> None:
        with self.assertRaises(ValueError):
            Symlink("/fake/path")

        with self.assertRaises(ValueError):
            existing_path = Path(__file__)
            Symlink(existing_path)

        with NamedTemporaryFile() as file:
            with self.assertRaises(FileExistsError):
                Symlink.make(path=file.name, to=__file__)

        with TemporaryDirectory() as generated_dir:
            target = Path.home()
            self.assertTrue(target.exists() and target.is_dir())

            link_path = Path(generated_dir) / "home-dir-link"
            with self.assertRaises(ValueError):
                Symlink.make(path=link_path, to=target)

            with self.assertRaises(ValueError):
                self.assertTrue(not link_path.exists())

                link_path.symlink_to(target, True)
                self.assertTrue(link_path.exists() and link_path.is_dir())

                Symlink(link_path)

    def test_override(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target_file = root / "target"
            target_file.touch()
            link_file = root / "link"
            link_file.touch()

            link = Symlink.make(path=link_file, to=target_file, override=True)
            self.assertEqual(target_file, link.target)

    def test_linkability(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target_file = root / "target"
            link_file = root / "link"

            test_content = "test content"
            write_file_content(target_file, test_content)
            link = Symlink.make(path=link_file, to=target_file)
            self.assertEqual(target_file, link.target)
            self.assertEqual(test_content, get_file_content(link.path))


if __name__ == "__main__":
    main()
