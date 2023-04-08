from dataclasses import dataclass
from pathlib import Path

from click import argument
from click import echo
from click import group
from click import option
from click import pass_context
from click import pass_obj

from github_tools.internal.account import Account
from github_tools.internal.registry import Registry
from github_tools.internal.registry import RegistryError


@dataclass
class Application:
    config: Path
    registry: Registry


@group()
@option("--config", type=Path, default=Path.home() / ".github-tools.cfg")
@pass_context
def cli(ctx: object, config: Path) -> None:
    """Allows switching between GitHub accounts in shells."""
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
    """Check ~/.ssh/config for GitHub host."""
    echo("check ssh config")


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
        app.registry.add(Account.create(name, cert_path, author, email), rewrite=True)
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


if __name__ == "__main__":
    cli()
