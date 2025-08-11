# TriAgent AutoGen 0.7.2 Demo

This project implements a 3-agent system using AutoGen 0.7.2 with:
- Manager agent (planning and orchestration)
- Coder agent (writes code to the workspace)
- Executor agent (runs shell/pytest commands securely)

It integrates with the context7 MCP server to search AutoGen 0.7.2 documentation from the IDE or via the MCP client API.

## Prerequisites
- Python 3.10+
- Environment variables for your models in `.env` (see below)
- Optional: context7 MCP server installed per its docs

## Install
```bash
pip install -e .
```

## Configure models
Create `.env` at repo root:
```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620
```

## Run
```bash
triagent run "Build a FastAPI endpoint that echoes JSON and tests"
```

The manager will break down the task, the coder writes files into `workspace/`, and the executor runs commands (e.g., pytest). Results are fed back to the agents.

## MCP: Searching AutoGen 0.7.2 docs with context7
- Ensure the context7 MCP server is available to your IDE (Cursor/VS Code MCP client) or reachable via ws(s) URL.
- Use the built-in MCP search tool provider in `triagent.mcp_search` to query AutoGen 0.7.2 docs, for example:

```bash
triagent docs "GroupChat and AssistantAgent in AutoGen 0.7.2"
```

## Security notes
- The executor runs commands in `workspace/` only and prevents long-lived processes.
- Commands are whitelisted; outputs are truncated.
