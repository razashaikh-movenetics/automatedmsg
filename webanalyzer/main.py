#!/usr/bin/env python3
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

from config import config
from site_scraper import scrape_website, clean_url
from analyzer import WebsiteAnalyzer

console = Console()


def print_banner():
    banner_text = f"""[bold cyan]MOVENETICS WEBSITE & UI/UX ANALYZER[/bold cyan]
[dim]Powered by DeepSeek AI ({config.deepseek_model})[/dim]
[dim]Audit UI/UX flaws • Recommend modern features • Generate outreach drafts[/dim]"""
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED))


def process_url(raw_url: str):
    raw_url = raw_url.strip()
    if not raw_url:
        console.print("[red]Please provide a valid website link.[/red]")
        return

    target_url = clean_url(raw_url)
    console.print(f"\n[cyan]Target URL:[/cyan] [bold]{target_url}[/bold]")

    # 1. Scrape Website
    with console.status("[bold green]Scraping and inspecting website DOM & UI/UX signals...[/bold green]"):
        site_data = scrape_website(target_url)

    if "error" in site_data and "status_code" not in site_data:
        console.print(f"\n[bold red]✗ Failed to inspect website:[/bold red] {site_data['error']}")
        return

    # 2. Analyze with DeepSeek
    analyzer = WebsiteAnalyzer()
    with console.status("[bold blue]Analyzing UI/UX errors and drafting outreach with DeepSeek AI...[/bold blue]"):
        result = analyzer.analyze(site_data)

    if not result.get("success"):
        console.print(f"\n[bold red]✗ Analysis error:[/bold red] {result.get('error')}")
        return

    # 3. Display Website Summary
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Key", style="bold cyan", width=16)
    summary_table.add_column("Value")
    summary_table.add_row("Domain", site_data.get("domain", ""))
    summary_table.add_row("Page Title", site_data.get("title") or "[dim]None[/dim]")
    summary_table.add_row("Mobile Viewport", "[green]✓ Present[/green]" if site_data.get("has_viewport") else "[bold red]✗ Missing[/bold red]")
    summary_table.add_row("H1 Headings", f"{site_data.get('h1_count', 0)} found")
    summary_table.add_row("Call To Actions", ", ".join(site_data.get("cta_found", [])) if site_data.get("cta_found") else "[yellow]None detected[/yellow]")
    summary_table.add_row("Chat Widget", "Present" if site_data.get("has_chat_widget") else "None detected")
    summary_table.add_row("Visual Images", f"[green]{site_data.get('visual_image_count', 0)} captured & inspected with DeepSeek Vision[/green]")

    console.print("\n")
    console.print(Panel(summary_table, title="[bold]Website Overview[/bold]", border_style="blue", box=box.ROUNDED))

    # 4. Display UI/UX Errors (Strict Rules)
    has_errors = result.get("has_errors", False)
    errors_list = result.get("errors_list", [])

    if has_errors and errors_list:
        errors_table = Table(box=box.ROUNDED, show_header=True, header_style="bold red")
        errors_table.add_column("#", width=4)
        errors_table.add_column("Severity", width=10)
        errors_table.add_column("Issue Title", width=25)
        errors_table.add_column("Impact & How Movenetics Fixes It")

        for idx, err in enumerate(errors_list, 1):
            sev = err.get("severity", "Medium")
            sev_color = "red" if sev.lower() == "high" else "yellow"
            desc = f"[bold]{err.get('impact', '')}[/bold]\n[dim]Fix:[/dim] {err.get('solution', '')}"
            errors_table.add_row(str(idx), f"[{sev_color}]{sev}[/{sev_color}]", err.get("title", ""), desc)

        console.print(Panel(errors_table, title="[bold red]UI/UX Errors Detected[/bold red]", border_style="red"))
    else:
        no_error_msg = f"[bold green]✓ {result.get('errors_summary', 'No significant UI/UX errors detected.')}[/bold green]\n[dim]The website structure, responsiveness, and primary elements appear clean and functional.[/dim]"
        console.print(Panel(no_error_msg, title="[bold green]UI/UX Status[/bold green]", border_style="green", box=box.ROUNDED))

    # 5. Display Features That Can Be Added
    features = result.get("features_to_add", [])
    if features:
        feat_table = Table(box=box.ROUNDED, show_header=True, header_style="bold yellow")
        feat_table.add_column("Feature", style="bold cyan", width=28)
        feat_table.add_column("Benefit & How It Works")
        for f in features:
            content = f"[bold]{f.get('benefit', '')}[/bold]\n[dim]{f.get('how_it_works', '')}[/dim]"
            feat_table.add_row(f.get("feature_name", ""), content)

        console.print(Panel(feat_table, title="[bold yellow]High-Impact Features Movenetics Can Add[/bold yellow]", border_style="yellow"))

    # 6. Direct msg: output
    msg_content = result.get("draft_msg", "").strip()
    console.print("\n[bold magenta]msg:[/bold magenta]")
    console.print(Panel(msg_content, border_style="magenta", box=box.ROUNDED))

    # 7. Direct mail: output
    mail_subject = result.get("draft_email_subject", "").strip()
    mail_body = result.get("draft_email_body", "").strip()

    mail_display = f"[bold cyan]Subject:[/bold cyan] {mail_subject}\n\n{mail_body}"
    console.print("\n[bold green]mail:[/bold green]")
    console.print(Panel(mail_display, border_style="green", box=box.ROUNDED))


def main():
    parser = argparse.ArgumentParser(description="Movenetics Website & UI/UX Analyzer")
    parser.add_argument("url", nargs="?", help="Website URL to analyze")
    parser.add_argument("--url", dest="opt_url", help="Website URL to analyze")
    args = parser.parse_args()

    input_url = args.url or args.opt_url

    if input_url:
        process_url(input_url)
        return

    print_banner()

    while True:
        console.print("\n[bold yellow]Enter or paste a website link below (or type 'exit' to quit):[/bold yellow]")
        url = Prompt.ask("[cyan]Paste Link[/cyan]").strip()

        if url.lower() in ("exit", "quit", "q"):
            console.print("[cyan]Goodbye![/cyan]")
            break

        process_url(url)


if __name__ == "__main__":
    main()

