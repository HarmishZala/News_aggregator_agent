#!/usr/bin/env python3
"""
Example usage of the enhanced News Aggregation Agent with memory capabilities.

Now styled with Rich for a visually pleasing CLI.
"""

import os
from dotenv import load_dotenv
from agent.agentic_workflow import GraphBuilder
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live

# Load environment variables
load_dotenv()

console = Console()


def section(title: str, subtitle: str | None = None, emoji: str = "✨") -> None:
    header = f"[bold { 'cyan' if emoji else 'white' }] {emoji} {title}[/]"
    console.print(Rule(header))
    if subtitle:
        console.print(f"[dim]{subtitle}[/]\n")


def main():
    """Demonstrate the enhanced agent capabilities with Rich UI."""

    section(
        title="Initializing Enhanced News Aggregation Agent",
        subtitle="Memory, formatting, and conversation management enabled",
        emoji="🚀",
    )

    with Live(Spinner("dots", text="Loading model and tools..."), refresh_per_second=8):
        agent = GraphBuilder(model_provider="groq", enable_memory=True)
        agent.build_graph()

    console.print(
        Panel.fit(
            "[green]Agent initialized successfully with memory support![/]\n"
            "[white]\- Memory persistence across conversations\n"
            "\- Enhanced output formatting (Markdown)\n"
            "\- Conversation history management\n"
            "\- Timestamp tracking",
            title="Ready",
            border_style="green",
        )
    )

    thread_id = "demo_conversation"

    # First query
    section("Query 1: Technology news about AI", emoji="🔍")
    with Live(Spinner("line", text="Fetching latest AI technology news..."), refresh_per_second=8):
        result1 = agent.run_with_memory(
            "What are the latest developments in AI technology?",
            thread_id=thread_id,
        )

    if "error" not in result1:
        console.print(Panel(Markdown(result1["response"]), title="Response", border_style="cyan"))
        meta = Table.grid(padding=1)
        meta.add_column(justify="right", style="bold dim")
        meta.add_column()
        meta.add_row("Timestamp", result1["timestamp"])
        meta.add_row("Memory", "Enabled" if result1["memory_enabled"] else "Disabled")
        console.print(Panel(meta, title="Meta", border_style="blue"))
    else:
        console.print(Panel(f"❌ {result1['error']}", title="Error", border_style="red"))

    # Second query
    section("Query 2: Follow-up on AI business impact", emoji="🔍")
    with Live(Spinner("line", text="Analyzing business impact..."), refresh_per_second=8):
        result2 = agent.run_with_memory(
            "How are these AI developments affecting the business world?",
            thread_id=thread_id,
        )

    if "error" not in result2:
        console.print(Panel(Markdown(result2["response"]), title="Response", border_style="cyan"))
        meta = Table.grid(padding=1)
        meta.add_column(justify="right", style="bold dim")
        meta.add_column()
        meta.add_row("Timestamp", result2["timestamp"])
        meta.add_row("Memory", "Enabled" if result2["memory_enabled"] else "Disabled")
        console.print(Panel(meta, title="Meta", border_style="blue"))
    else:
        console.print(Panel(f"❌ {result2['error']}", title="Error", border_style="red"))

    # Conversation history
    section("Conversation History", emoji="📚")
    history = agent.get_conversation_history(thread_id)
    if history:
        table = Table(title="Messages", show_lines=True)
        table.add_column("#", justify="right", style="bold")
        table.add_column("Role", style="magenta")
        table.add_column("Content", style="white")
        for i, message in enumerate(history, 1):
            role = message.get("role", "unknown").upper()
            content_full = message.get("content", "")
            content = content_full if len(content_full) <= 120 else content_full[:117] + "..."
            table.add_row(str(i), role, content)
        console.print(table)
    else:
        console.print(Panel("No conversation history found.", border_style="yellow"))

    section("Memory Management", emoji="🧠")
    console.print(
        Panel.fit(
            "[green]Memory is automatically managed by LangGraph[/]\n"
            "[white]\- Conversations persist across sessions\n"
            "\- Context is maintained within thread boundaries\n\n"
            "[dim]To clear conversation history: [/]`agent.clear_conversation_history(\"demo_conversation\")`",
            border_style="green",
        )
    )

    console.print(Rule("🎉 Demo completed successfully!"))


if __name__ == "__main__":
    main()
