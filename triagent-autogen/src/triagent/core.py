from __future__ import annotations

import os
from typing import Dict

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient

from .executor import ExecutorAgent


def build_model_clients() -> Dict[str, object]:
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    openai_client = OpenAIChatCompletionClient(model=openai_model)
    anthropic_client = AnthropicChatCompletionClient(model=anthropic_model)
    return {"openai": openai_client, "anthropic": anthropic_client}


def build_agents(workspace_dir: str):
    clients = build_model_clients()

    manager = AssistantAgent(
        name="manager",
        system_message=(
            "You are the manager. Break down tasks, assign work to the coder, "
            "and ask the executor to run commands. Keep iterations minimal."
        ),
        model_client=clients["openai"],
    )

    coder = AssistantAgent(
        name="coder",
        system_message=(
            "You are the coder. Write and modify files strictly inside the workspace directory. "
            "Provide exact filenames, code blocks, and testing steps."
        ),
        model_client=clients["openai"],
    )

    executor = ExecutorAgent(
        name="executor",
        workspace_dir=workspace_dir,
        model_client=clients["anthropic"],
    )

    team = RoundRobinGroupChat(agents=[manager, coder, executor], max_turns=12)
    team.add_termination(MaxMessageTermination(max_messages=24))

    return {"manager": manager, "coder": coder, "executor": executor, "team": team}
