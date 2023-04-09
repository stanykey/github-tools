# GitHub Tools

The package contains a set of small CLIs for different purposes.


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
