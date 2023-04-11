from io import StringIO
from unittest import main
from unittest import TestCase

from github_tools.internal.ssh_config import SshConfig
from github_tools.internal.ssh_config import SshConfigError
from github_tools.internal.ssh_config import SshKeyword

DUMMY_SSH_CONFIG = """
# GitLab.com
Host gitlab.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/git

# Github.com
Host github.com
    HostName github.com
    PreferredAuthentications publickey
    User git
    IdentityFile ~/.ssh/git

"""


class SshConfigTestCase(TestCase):
    def test_creation(self) -> None:
        config = SshConfig(StringIO())
        self.assertTrue(config.is_valid())

        config = SshConfig(StringIO(DUMMY_SSH_CONFIG))
        self.assertTrue(config.is_valid())
        self.assertEqual({"github.com", "gitlab.com"}, set(config.hosts))
        self.assertTrue("google.com" not in config)

        with self.assertRaises(SshConfigError):
            SshConfig(StringIO("Host gitlab.com\nInvalidKey publickey"))

    def test_host_config(self) -> None:
        config = SshConfig(StringIO(DUMMY_SSH_CONFIG))

        github_config = config.get("github.com")
        assert github_config is not None
        self.assertEqual(4, len(github_config))
        self.assertEqual("publickey", github_config.get(SshKeyword.PreferredAuthentications))
        self.assertEqual("~/.ssh/git", github_config.get(SshKeyword.IdentityFile))
        self.assertEqual("git", github_config.get(SshKeyword.User))
        self.assertEqual("github.com", github_config.get(SshKeyword.HostName))

        gitlab_config = config.get("gitlab.com")
        assert gitlab_config is not None
        self.assertEqual(2, len(gitlab_config))
        self.assertEqual("publickey", gitlab_config.get(SshKeyword.PreferredAuthentications))
        self.assertEqual("~/.ssh/git", gitlab_config.get(SshKeyword.IdentityFile))
        self.assertEqual(None, gitlab_config.get(SshKeyword.User))
        self.assertEqual(None, gitlab_config.get(SshKeyword.HostName))

        google_config = config.get("google.com")
        self.assertTrue(google_config is None)


if __name__ == "__main__":
    main()
