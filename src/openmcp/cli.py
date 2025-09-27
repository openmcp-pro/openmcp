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
        None, "--host", "-h", help="Server host (Note: FastMCP uses default configuration)"
    ),
    port: Optional[int] = typer.Option(
        None, "--port", "-p", help="Server port (Note: FastMCP uses default configuration)"
    ),
    transport: str = typer.Option(
        "streamable-http", "--transport", "-t", help="Transport protocol (streamable-http, sse, or rest)"
    ),
    reload: bool = typer.Option(
        False, "--reload", help="Enable auto-reload for development (rest transport only)"
    ),
):
    """Start the OpenMCP server (default: FastMCP with streamable-http transport)."""
    
    if transport == "rest":
        # Legacy HTTP API server
        console.print("[bold yellow]Starting OpenMCP Legacy HTTP API server...[/bold yellow]")
        console.print("[dim]Note: This is the legacy REST API. Use --transport streamable-http for MCP protocol.[/dim]")
        server = OpenMCPServer(config_file)
        try:
            server.run(host=host, port=port, reload=reload)
        except KeyboardInterrupt:
            console.print("\n[yellow]HTTP server stopped by user[/yellow]")
    elif transport == "sse":
        console.print(f"[bold green]Starting OpenMCP FastMCP Server (SSE transport)...[/bold green]")
        try:
            from .api.mcp_server import run_sse_server
            run_sse_server(config_file, host or "0.0.0.0", port or 8000)
        except KeyboardInterrupt:
            console.print("\n[yellow]MCP SSE server stopped by user[/yellow]")
    elif transport == "streamable-http":
        console.print(f"[bold green]Starting OpenMCP FastMCP Server (streamable-http transport)...[/bold green]")
        try:
            from .api.mcp_server import run_streamable_http_server
            run_streamable_http_server(config_file, host or "0.0.0.0", port or 8000)
        except KeyboardInterrupt:
            console.print("\n[yellow]MCP streamable-http server stopped by user[/yellow]")
    else:
        console.print(f"[red]Unsupported transport: {transport}[/red]")
        console.print("Supported transports: streamable-http, sse, rest")
        raise typer.Exit(1)


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
def mcp_sse(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    host: Optional[str] = typer.Option(
        "0.0.0.0", "--host", "-h", help="Server host"
    ),
    port: Optional[int] = typer.Option(
        9001, "--port", "-p", help="Server port"
    ),
):
    """Start MCP server with SSE transport (specialized command)."""
    console.print("[bold green]Starting OpenMCP FastMCP Server (SSE transport)...[/bold green]")
    console.print("[dim]Note: Use 'openmcp serve --transport sse' for the same functionality.[/dim]")
    
    try:
        from .api.mcp_server import run_sse_server
        run_sse_server(config_file, host, port)
    except KeyboardInterrupt:
        console.print("\n[yellow]MCP SSE server stopped by user[/yellow]")


@app.command()
def mcp_http(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    host: Optional[str] = typer.Option(
        "0.0.0.0", "--host", "-h", help="Server host"
    ),
    port: Optional[int] = typer.Option(
        9002, "--port", "-p", help="Server port"
    ),
):
    """Start MCP server with streamable-http transport (specialized command)."""
    console.print("[bold green]Starting OpenMCP FastMCP Server (streamable-http transport)...[/bold green]")
    console.print("[dim]Note: Use 'openmcp serve --transport streamable-http' for the same functionality.[/dim]")
    
    try:
        from .api.mcp_server import run_streamable_http_server
        run_streamable_http_server(config_file, host, port)
    except KeyboardInterrupt:
        console.print("\n[yellow]MCP streamable-http server stopped by user[/yellow]")


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
