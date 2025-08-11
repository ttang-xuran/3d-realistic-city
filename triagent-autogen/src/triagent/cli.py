from __future__ import annotations

import os
import shlex
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from .core import build_agents
from .executor import safe_run_command
from .mcp_search import search_docs

app = typer.Typer(help="TriAgent AutoGen 0.7.2 CLI")
console = Console()

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)


def ensure_env_loaded() -> None:
    load_dotenv(ROOT / ".env")


@app.command()
def run(task: str = typer.Argument(..., help="Task for the agents to accomplish")) -> None:
    ensure_env_loaded()
    console.print(Panel.fit(f"[bold]Task[/bold]: {task}"))
    agents = build_agents(workspace_dir=str(WORKSPACE))
    result = agents["manager"].initiate_chat(
        recipient=agents["coder"],
        message=f"You are part of a 3-agent team. Complete this task: {task}. Use the executor to run commands when needed.",
    )
    console.print(Panel.fit("[bold green]Conversation finished[/bold green]"))
    if result:
        console.print(result)


@app.command()
def exec(cmd: str = typer.Argument(..., help="Command to run in workspace")) -> None:
    ensure_env_loaded()
    ok, out = safe_run_command(cmd, cwd=str(WORKSPACE))
    status = "OK" if ok else "ERR"
    console.print(Panel.fit(f"[{status}] {cmd}\n\n{out}"))


@app.command()
def docs(query: str = typer.Argument(..., help="Query about AutoGen 0.7.2"), url: Optional[str] = typer.Option(None, help="ws:// URL of context7 MCP server")) -> None:
    ensure_env_loaded()
    results = search_docs(query, server_url=url)
    for idx, item in enumerate(results, 1):
        console.print(Panel.fit(f"[bold]Result {idx}[/bold]\n{item}"))
