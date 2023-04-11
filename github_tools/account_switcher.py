from dataclasses import dataclass
from pathlib import Path

from click import argument
from click import confirm
from click import echo
from click import group
from click import option
from click import pass_context
from click import pass_obj

from github_tools.internal.account import Account
from github_tools.internal.registry import Registry
from github_tools.internal.registry import RegistryError
from github_tools.internal.ssh_config import SshConfig


@dataclass
class Application:
    config: Path
    registry: Registry


@group()
@option("--config", type=Path, default=Path.home() / ".github-tools.cfg", show_default=True)
@pass_context
def cli(ctx: object, config: Path) -> None:
    """
    Allows switching between GitHub accounts in shells.

    It's done pretty simply: the application creates or updates a section for **Host github.com** by pointing
    **IdentityFile** to the symbolic link which can be switched to another certificate file with the **switch** command
    """
    registry = Registry()
    skip_loading = getattr(ctx, "invoked_subcommand") == "prune"
    if not skip_loading and config.exists():
        with open(config, encoding="utf-8") as file:
            try:
                registry = Registry.load(file)
            except RegistryError as error:
                echo(f"can't load accounts: {error.message}")
                exit(error.code)

    setattr(ctx, "obj", Application(config, registry))


@cli.command(short_help="drop accounts")
@pass_obj
def prune(app: Application) -> None:
    """Simply delete config file."""
    app.config.unlink(missing_ok=True)
    echo("all accounts were dropped")


@cli.command(name="check-ssh", short_help="check ssh config")
def check_ssh_config() -> None:
    """Check ~/.ssh/config for GitHub host entry."""
    config_path = Path.home() / ".ssh" / "config"
    if not config_path.is_file():
        echo("ssh config file (~/.ssh/config) is missing")

    with open(config_path, encoding="utf-8") as file:
        ssh_config = SshConfig(file)

    status = "valid" if ssh_config.is_valid() else "corrupted"
    print(f"ssh config is {status}")

    status = "contains" if "github.com" in ssh_config else "doesn't contain"
    print(f"ssh config {status} 'github.com' entry")


@cli.command(name="list", short_help="list accounts")
@pass_obj
def list_accounts(app: Application) -> None:
    """Print list of all registered accounts."""
    if not app.registry.accounts:
        echo("no accounts")
        return

    echo("Github Accounts:")
    for account in app.registry.accounts:
        echo(f"{account.name}:")
        echo(f"    cert:   '{account.cert_file}'")
        echo(f"    author: {account.author!r}")
        echo(f"    email:  {account.email!r}")


@cli.command(name="add", short_help="add account")
@argument("name", type=str)
@argument("cert-path", type=Path)
@option("--author", type=str)
@option("--email", type=str)
@pass_obj
def add_account(app: Application, name: str, cert_path: Path, author: str, email: str) -> None:
    """Add/update account to registry."""
    try:
        account = Account.create(name, cert_path, author, email)
        if not account.is_valid():
            if not confirm("account is invalid. add anyway?"):
                return

        app.registry.add(account, rewrite=True)
        with open(app.config, "w", encoding="utf-8") as file:
            app.registry.save(file)

        action = "updated" if name in app.registry else "added"
        echo(f"operation succeeded: account was {action}")
    except OSError as error:
        echo(f"operation failed: {error.strerror}")


@cli.command(name="remove", short_help="remove account")
@argument("name", type=str)
@pass_obj
def remove_account(app: Application, name: str) -> None:
    """Remove account from registry."""
    if name not in app.registry:
        echo("no registered account")
        return

    try:
        app.registry.remove(name)
        with open(app.config, "w", encoding="utf-8") as file:
            app.registry.save(file)

        echo("operation succeeded: account was removed")
    except OSError as error:
        echo(f"operation failed: {error.strerror}")


@cli.command(name="switch", short_help="switch account")
@argument("name", type=str)
def switch_to_account(name: str) -> None:
    """Switch to account if exists."""
    echo(f"switch to account - {name}")


@cli.command(name="check", short_help="check account")
@argument("name", type=str)
@option("--remove", type=bool, is_flag=True, default=False)
@pass_obj
def validate_account(app: Application, name: str, remove: bool) -> None:
    """Validate accounts and delete invalid if *remove* is set to **True**."""
    account = app.registry.get(name)
    if not account:
        echo("no registered account")
        return

    if account.is_valid():
        echo(f"account ({name}) is valid")
        return

    echo(f"account ({name}) is invalid")
    if remove and confirm("confirm delete", prompt_suffix="? "):
        app.registry.remove(account)
        with open(app.config, "w", encoding="utf-8") as file:
            app.registry.save(file)


if __name__ == "__main__":
    cli()
