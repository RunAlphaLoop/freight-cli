"""AlphaLoops Freight CLI — command-line interface for FMCSA carrier data."""

__version__ = "0.3.0"

import json
import os
import stat
import sys

import click
from rich.console import Console

from alphaloops.freight.config import resolve_config
from .state import ClientState, pass_state
from . import carriers_cmd, fleet_cmd, inspections_cmd, crashes_cmd, contacts_cmd

console = Console(stderr=True)


@click.group(invoke_without_command=True)
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON (for scripts and agents).")
@click.option("--python", "output_python", is_flag=True, help="Print Python SDK code instead of running the command.")
@click.option("--typescript", "output_typescript", is_flag=True, help="Print TypeScript SDK code instead of running the command.")
@click.option("--api-key", envvar="ALPHALOOPS_API_KEY", default=None, help="API key (default: env/config file).")
@click.version_option(__version__, prog_name="loopsh")
@click.pass_context
def main(ctx, output_json, output_python, output_typescript, api_key):
    """AlphaLoops Freight CLI — FMCSA carrier data at your fingertips.

    \b
    Examples:
      loopsh carriers search "Werner Enterprises"
      loopsh carriers 2247505
      loopsh fleet 2247505
      loopsh crashes 2247505 --severity FATAL
      loopsh contacts search --dot 2247505

    \b
    Agent workflow (search → details → fleet):
      DOT=$(loopsh --json carriers search "Swift" | jq -r '.results[0].dot_number')
      loopsh carriers get "$DOT"
      loopsh fleet trucks "$DOT"
      loopsh inspections list "$DOT"

    \b
    Code generation:
      loopsh --python carriers get 2247505
      loopsh --typescript contacts search --dot 2247505
    """
    ctx.ensure_object(dict)
    ctx.obj = ClientState(
        api_key=api_key,
        output_json=output_json,
        output_python=output_python,
        output_typescript=output_typescript,
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


main.add_command(carriers_cmd.carriers)
main.add_command(fleet_cmd.fleet)
main.add_command(inspections_cmd.inspections)
main.add_command(crashes_cmd.crashes)
main.add_command(contacts_cmd.contacts)


@main.command()
@click.argument("api_key", required=False)
def login(api_key):
    """Save your API key to ~/.alphaloops."""
    if not api_key:
        api_key = click.prompt("API key")

    api_key = api_key.strip()
    if not api_key:
        raise click.ClickException("API key cannot be empty")

    config_path = os.path.expanduser("~/.alphaloops")
    config = {}

    # Preserve existing config
    if os.path.isfile(config_path):
        try:
            with open(config_path) as f:
                text = f.read().strip()
            if text.startswith("{"):
                config = json.loads(text)
        except Exception:
            pass

    config["api_key"] = api_key

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)

    console.print(f"[green]API key saved to {config_path}[/green]")


@main.command()
@pass_state
def whoami(state):
    """Show current API key info."""
    key, url = resolve_config()
    if not key:
        raise click.ClickException("No API key configured. Run: loopsh login")

    masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"

    if state.output_json:
        click.echo(json.dumps({"api_key": masked, "base_url": url}, indent=2))
    else:
        console.print(f"  [bold cyan]api_key[/bold cyan]   {masked}")
        console.print(f"  [bold cyan]base_url[/bold cyan]  {url}")


def cli():
    """Entry point that catches exceptions cleanly."""
    try:
        main(standalone_mode=False)
    except click.ClickException as e:
        console.print(f"[red]Error:[/red] {e.format_message()}")
        sys.exit(e.exit_code)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
