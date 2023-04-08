from io import StringIO
from unittest import main
from unittest import TestCase

from github_tools.internal.account import Account
from github_tools.internal.registry import ErrorCode
from github_tools.internal.registry import Registry
from github_tools.internal.registry import RegistryError


def load_fake_db() -> StringIO:
    return StringIO("[Jack]\n" "cert_file = /fake/cert-file\n" "[Joe]\n" "cert_file=other/fake-file\n")


class RegistryTestCase(TestCase):
    def test_create(self) -> None:
        registry = Registry()
        self.assertEqual(0, len(registry))

    def test_load_basic(self) -> None:
        registry = Registry.load(StringIO())
        self.assertEqual(0, len(registry))

        registry = Registry.load(load_fake_db())
        self.assertEqual(2, len(registry))
        self.assertTrue("Jack" in registry)
        self.assertTrue("Joe" in registry)

    def test_load_corrupted(self) -> None:
        with self.assertRaises(RegistryError) as call_context:
            Registry.load(StringIO("[Joe"))
        self.assertEqual(ErrorCode.FileCorrupted, call_context.exception.code)

        with self.assertRaises(RegistryError) as call_context:
            Registry.load(StringIO("[Joe]\n[Joe]\n"))
        self.assertEqual(ErrorCode.DuplicateAccount, call_context.exception.code)

        with self.assertRaises(RegistryError) as call_context:
            Registry.load(StringIO("[Joe]"))
        self.assertEqual(ErrorCode.FieldMissed, call_context.exception.code)

        with self.assertRaises(RegistryError) as call_context:
            Registry.load(StringIO("[Joe]\ncert_file="))
        self.assertEqual(ErrorCode.FieldValueMissed, call_context.exception.code)

    def test_modify_operations(self) -> None:
        registry = Registry()

        registry.add(Account.create(name="Jack", cert_file=r"/face/certificate"))
        registry.add(Account.create(name="Joe", cert_file=r"/face/certificate"))
        self.assertEqual(2, len(registry))

        self.assertFalse(registry.add(Account.create(name="Jack", cert_file=r"/face/certificate")))
        self.assertTrue(registry.add(Account.create(name="Jack", cert_file=r"/face/certificate"), rewrite=True))
        self.assertEqual(2, len(registry))

        registry.remove(Account.create(name="Jack", cert_file=r"/face/certificate"))
        self.assertEqual(1, len(registry))
        self.assertTrue("Joe" in registry)

        registry.remove("Joe")
        self.assertEqual(0, len(registry))

    def test_save(self) -> None:
        registry = Registry.load(load_fake_db())
        registry.remove("Joe")

        fake_file = StringIO()
        registry.save(fake_file)
        fake_file.seek(0)

        content = fake_file.read()
        self.assertFalse("Joe" in content)
        self.assertTrue("Jack" in content)
        self.assertTrue("cert_file" in content)
        self.assertFalse("author" in content)
        self.assertFalse("email" in content)


if __name__ == "__main__":
    main()
