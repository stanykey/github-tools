# GitHub Tools

The package contains a set of small CLIs for different purposes.

Note: yet one educational project with practical purposes. Educational topics/goals:
- [ssh config](https://linux.die.net/man/5/ssh_config) editing
- mastering in [click](https://palletsprojects.com/p/click/) package and CLI in the whole
- python [builtin unit tests framework](https://docs.python.org/3/library/unittest.html)


## List of applications:
- *[github-account](#github-account)*: allowing to switch between accounts in shell


### github-account
```text
Usage: github-account [OPTIONS] COMMAND [ARGS]...

  Allows switching between GitHub accounts in shells.

  It's done pretty simply: the application creates or updates a section for
  **Host github.com** by pointing **IdentityFile** to the symbolic link which
  can be switched to another certificate file with the **switch** command


Options:
  --config PATH  [default: ~/.github-tools.cfg]
  --help         Show this message and exit.

Commands:
  add        add account
  check      check account
  check-ssh  check ssh config
  list       list accounts
  prune      drop accounts
  remove     remove account
  switch     switch account

```
