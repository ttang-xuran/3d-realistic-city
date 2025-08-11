from __future__ import annotations

import subprocess
import shlex
from pathlib import Path
from typing import Tuple

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage


ALLOWED_PREFIXES = [
    "pytest",
    "python",
    "pip",
    "ls",
    "echo",
    "node",
    "npm",
]


def safe_run_command(command: str, cwd: str) -> Tuple[bool, str]:
    command = command.strip()
    if not command:
        return False, "Empty command"
    if command.split()[0] not in ALLOWED_PREFIXES:
        return False, f"Command not allowed: {command}"
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
            text=True,
        )
        output = completed.stdout
        if len(output) > 16000:
            output = output[:16000] + "\n... [truncated]"
        return True, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as exc:  # noqa: BLE001
        return False, f"Error: {exc}"


class ExecutorAgent(AssistantAgent):
    def __init__(self, name: str, workspace_dir: str, model_client):
        super().__init__(
            name=name,
            system_message=(
                "You run shell commands in the workspace on request. "
                "ONLY run short-lived commands. Never start servers."
            ),
            model_client=model_client,
        )
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def on_messages(self, messages):
        last = messages[-1]
        if isinstance(last, TextMessage) and last.from_ == "manager":
            content = last.content.strip()
            if content.startswith("EXEC:"):
                cmd = content[len("EXEC:") :].strip()
                ok, out = safe_run_command(cmd, cwd=str(self.workspace_dir))
                return TextMessage(content=f"EXEC RESULT ({'OK' if ok else 'ERR'}):\n{out}")
        return super().on_messages(messages)
