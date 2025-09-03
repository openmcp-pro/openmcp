"""Command line interface for openmcp."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .core.config import Config
from .core.server import OpenMCPServer

app = typer.Typer(help="openmcp - Optimized MCP services for AI Agents")
console = Console()


@app.command()
def serve(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    host: Optional[str] = typer.Option(
        None, "--host", "-h", help="Server host"
    ),
    port: Optional[int] = typer.Option(
        None, "--port", "-p", help="Server port"
    ),
    reload: bool = typer.Option(
        False, "--reload", help="Enable auto-reload for development"
    ),
    protocol: str = typer.Option(
        "http", "--protocol", help="Server protocol: 'http' or 'mcp'"
    ),
):
    """Start the openmcp server."""
    if protocol == "mcp":
        console.print("[bold green]Starting openmcp MCP server...[/bold green]")
        from .mcp_server import OpenMCPServer as MCPServer
        server = MCPServer()
        try:
            import asyncio
            asyncio.run(server.run())
        except KeyboardInterrupt:
            console.print("\n[yellow]MCP server stopped by user[/yellow]")
    else:
        console.print("[bold green]Starting openmcp HTTP server...[/bold green]")
        server = OpenMCPServer(config_file)
        try:
            server.run(host=host, port=port, reload=reload)
        except KeyboardInterrupt:
            console.print("\n[yellow]HTTP server stopped by user[/yellow]")


@app.command()
def init_config(
    output: Path = typer.Option(
        Path("config.yaml"), "--output", "-o", help="Output configuration file"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing configuration"
    ),
):
    """Initialize a default configuration file."""
    if output.exists() and not force:
        console.print(f"[red]Configuration file already exists: {output}[/red]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)
    
    config = Config.create_default()
    config.save_to_file(output)
    
    console.print(f"[green]Configuration file created: {output}[/green]")
    console.print("\n[bold]Default API Key:[/bold]")
    console.print("Name: default")
    
    # Get the default API key
    from .core.auth import AuthManager
    auth_manager = AuthManager(config.auth)
    api_keys = auth_manager.list_api_keys()
    for key, key_obj in api_keys.items():
        if key_obj.name == "default":
            console.print(f"Key: {key}")
            break


@app.command()
def list_services():
    """List available MCP services."""
    table = Table(title="Available MCP Services")
    table.add_column("Service", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Status", style="yellow")
    
    # For now, we only have browseruse
    table.add_row(
        "browseruse",
        "Web browser automation service",
        "Available"
    )
    
    console.print(table)


@app.command()
def create_key(
    name: str = typer.Argument(help="API key name"),
    expires_days: Optional[int] = typer.Option(
        None, "--expires", "-e", help="Expiration in days"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
):
    """Create a new API key."""
    config = Config.from_file(config_file)
    
    from .core.auth import AuthManager
    auth_manager = AuthManager(config.auth)
    
    api_key = auth_manager.create_api_key(name, expires_days)
    
    console.print(f"[green]API key created successfully![/green]")
    console.print(f"Name: {name}")
    console.print(f"Key: {api_key}")
    if expires_days:
        console.print(f"Expires in: {expires_days} days")


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"openmcp version {__version__}")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
