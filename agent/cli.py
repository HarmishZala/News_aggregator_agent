#!/usr/bin/env python3
"""
Rich-powered CLI for the News Aggregation Agent.

Usage examples:
  python cli.py -q "latest AI news" --category tech --provider groq --thread myrun
  python cli.py --interactive
"""

import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live

from dotenv import load_dotenv
from agent.agentic_workflow import GraphBuilder

console = Console()


def build_agent(model_provider: str, enable_memory: bool) -> GraphBuilder:
    with Live(Spinner("dots", text="Initializing agent..."), refresh_per_second=8):
        agent = GraphBuilder(model_provider=model_provider, enable_memory=enable_memory)
        agent.build_graph()
    return agent


def run_query(agent: GraphBuilder, query: str, thread_id: str) -> None:
    with Live(Spinner("line", text="Thinking..."), refresh_per_second=8):
        result = agent.run_with_memory(query, thread_id=thread_id)

    if "error" in result:
        console.print(Panel(f"❌ {result['error']}", title="Error", border_style="red"))
        return

    console.print(Panel(Markdown(result["response"]), title="Response", border_style="cyan"))
    console.print(
        Panel.fit(
            f"[dim]Thread:[/] {thread_id}\n[dim]Timestamp:[/] {result['timestamp']}\n[dim]Memory:[/] {'Enabled' if result['memory_enabled'] else 'Disabled'}",
            title="Meta",
            border_style="blue",
        )
    )


def interactive_loop(agent: GraphBuilder, thread_id: str) -> None:
    console.print(Rule("💬 Interactive Mode - type 'exit' to quit"))
    while True:
        query = Prompt.ask("[bold cyan]You[/]")
        if query.strip().lower() in {"exit", ":q", "quit"}:
            console.print(Panel("Goodbye!", border_style="green"))
            break
        run_query(agent, query, thread_id)


def main(argv: Optional[list[str]] = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="News Aggregation Agent CLI")
    parser.add_argument("-q", "--query", type=str, help="Your query text")
    parser.add_argument("-p", "--provider", type=str, default="groq", choices=["groq", "openai"], help="LLM provider")
    parser.add_argument("-t", "--thread", type=str, default="default", help="Thread ID for memory continuity")
    parser.add_argument("--no-memory", action="store_true", help="Disable memory")
    parser.add_argument("--interactive", action="store_true", help="Interactive chat mode")

    args = parser.parse_args(argv)

    console.print(Rule("📰 News Aggregation Agent"))
    agent = build_agent(args.provider, enable_memory=not args.no_memory)

    if args.interactive:
        interactive_loop(agent, args.thread)
        return 0

    if not args.query:
        console.print(Panel("Please provide a query with -q/--query or use --interactive.", border_style="yellow"))
        return 2

    run_query(agent, args.query, args.thread)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


