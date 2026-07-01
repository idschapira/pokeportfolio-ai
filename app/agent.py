# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters
from mcp.client.stdio import get_default_environment

from app.prompts import ROOT_AGENT_INSTRUCTION
from app.tools import get_portfolio, save_cards

load_dotenv()

_REQUIRED_CARD_API_ENV_VARS = ("CARD_API_KEY", "CARD_API_BASE_URL")
for _var in _REQUIRED_CARD_API_ENV_VARS:
    if not os.environ.get(_var):
        raise RuntimeError(f"Missing required environment variable: {_var}")

# The MCP server (mcp_server/server.py) runs as a stdio subprocess: ADK
# launches it, talks MCP over its stdin/stdout, and the tools it exposes
# (resolve_card, get_price) show up to the agent like any other tool.
# `get_default_environment()` gives the subprocess a minimal safe env
# (PATH, HOME, ...); we layer the card API credentials on top by reference
# to os.environ — their values are never written to code or logs.
_mcp_server_env = get_default_environment()
for _var in _REQUIRED_CARD_API_ENV_VARS:
    _mcp_server_env[_var] = os.environ[_var]

card_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            env=_mcp_server_env,
        ),
        timeout=15.0,
    ),
)

# require_confirmation=True is ADK's native HITL gate: the runtime pauses
# this tool call and requires an explicit human ToolConfirmation before
# save_cards() ever runs, independent of what the LLM/prompt decides.
save_cards_tool = FunctionTool(func=save_cards, require_confirmation=True)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[card_mcp_toolset, save_cards_tool, get_portfolio],
)

app = App(
    root_agent=root_agent,
    name="app",
)
