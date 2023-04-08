from dataclasses import dataclass
from pathlib import Path

from click import argument
from click import echo
from click import group
from click import option
from click import pass_context

from github_tools.internal.registry import Registry


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
    if config.exists():
        with open(config, encoding="utf-8") as file:
            registry = Registry.load(file)

    setattr(ctx, "obj", Application(config, registry))


@cli.command(name="check-ssh", short_help="check ssh config")
def check_ssh_config() -> None:
    """Check ~/.ssh/config for GitHub host."""
    echo("check ssh config")


@cli.command(name="list", short_help="list accounts")
def list_accounts() -> None:
    """Print list of all registered accounts."""
    echo("list of github accounts")


@cli.command(name="add", short_help="add account")
@argument("name", type=str)
@argument("cert-path", type=Path)
@option("--author", type=str)
@option("--email", type=str)
def add_account(name: str, cert_path: Path, author: str, email: str) -> None:
    """Add/update account to registry."""
    echo(f"add github account - {name}")
    echo(f"\tcert: {str(cert_path)}")

    if author:
        echo(f"\tauthor: {author}")

    if email:
        echo(f"\temail: {email}")


@cli.command(name="remove", short_help="remove account")
@argument("name", type=str)
def remove_account(name: str) -> None:
    """Remove account from registry."""
    echo(f"remove github account - {name}")


@cli.command(name="switch", short_help="switch account")
@argument("name", type=str)
def switch_to_account(name: str) -> None:
    """Switch to account if exists."""
    echo(f"switch to account - {name}")


if __name__ == "__main__":
    cli()
