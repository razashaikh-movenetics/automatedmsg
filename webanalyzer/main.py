#!/usr/bin/env python3
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.rule import Rule
from rich import box
from rich.columns import Columns
from rich.text import Text

from config import config
from site_scraper import scrape_website, clean_url
from analyzer import WebsiteAnalyzer

console = Console()


def print_banner():
    banner_text = (
        f"[bold cyan]Movenetics / Element Labs — Website Intelligence Analyzer[/bold cyan]\n"
        f"[dim]3-Agent DeepSeek Pipeline • UI/UX Audit • Product Matching • Outreach Drafting[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED, padding=(1, 4)))


def render_error_badge(sev: str) -> str:
    if sev.lower() == "high":
        return f"[bold red]● High[/bold red]"
    elif sev.lower() == "medium":
        return f"[bold yellow]● Medium[/bold yellow]"
    return f"[dim]● Low[/dim]"


def process_url(raw_url: str):
    raw_url = raw_url.strip()
    if not raw_url:
        console.print("[red]Please provide a valid website link.[/red]")
        return

    target_url = clean_url(raw_url)
    console.print(f"\n[cyan]→ Analyzing:[/cyan] [bold]{target_url}[/bold]")

    # ─── Step 1: Scrape ───────────────────────────────────────────────────────
    with console.status("[bold green]Scraping website — fetching DOM + visual images...[/bold green]"):
        site_data = scrape_website(target_url)

    if "error" in site_data and "status_code" not in site_data:
        console.print(f"\n[bold red]✗ Failed:[/bold red] {site_data['error']}")
        return

    # ─── Step 2: Run 3-Agent Analysis ────────────────────────────────────────
    analyzer = WebsiteAnalyzer()
    with console.status(
        "[bold blue]Running 3 AI Agents: Auditor → Strategist → Outreach Drafter...[/bold blue]"
    ):
        result = analyzer.analyze(site_data)

    if not result.get("success"):
        console.print(f"\n[bold red]✗ Analysis error:[/bold red] {result.get('error')}")
        return

    console.print()
    console.print(Rule(f"[bold cyan]{site_data.get('domain', target_url)} — Analysis Report[/bold cyan]"))

    # ─── Section 1: Website Overview ─────────────────────────────────────────
    overview = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    overview.add_column("Key", style="bold cyan", width=18)
    overview.add_column("Value")
    overview.add_row("Domain", site_data.get("domain", ""))
    overview.add_row("Title", site_data.get("title") or "[dim]None[/dim]")
    overview.add_row("Business", result.get("business_summary", "[dim]—[/dim]"))
    overview.add_row("Mobile Viewport",
        "[green]✓ Present[/green]" if site_data.get("has_viewport") else "[bold red]✗ Missing[/bold red]"
    )
    overview.add_row("H1 Headings", f"{site_data.get('h1_count', 0)} found")
    overview.add_row("CTAs Detected",
        ", ".join(site_data.get("cta_found", [])) if site_data.get("cta_found") else "[yellow]None detected[/yellow]"
    )
    overview.add_row("Lead Form", "[green]Yes[/green]" if site_data.get("has_contact_or_lead_form") else "[yellow]No[/yellow]")
    overview.add_row("Chat Widget", "[green]Present[/green]" if site_data.get("has_chat_widget") else "[dim]None[/dim]")
    overview.add_row("Images Analyzed",
        f"[green]{site_data.get('visual_image_count', 0)} visual screenshots sent to AI[/green]"
    )
    console.print(Panel(overview, title="[bold]Website Overview[/bold]", border_style="blue"))

    # ─── Section 2: Customer First Impression ─────────────────────────────────
    first_impression = result.get("customer_first_impression", "")
    if first_impression:
        console.print(Panel(
            f"[italic]\"{first_impression}\"[/italic]",
            title="[bold]👤 Customer First Impression[/bold]",
            border_style="dim",
            padding=(0, 2)
        ))

    # ─── Section 3: What They Are Losing Right Now ────────────────────────────
    errors = result.get("errors_list", [])
    has_errors = result.get("has_errors", False)

    if has_errors and errors:
        err_table = Table(box=box.ROUNDED, show_header=True, header_style="bold red", padding=(0, 1))
        err_table.add_column("", width=10)
        err_table.add_column("What's Costing Them", width=28)
        err_table.add_column("The Real Impact  →  How We Fix It")
        for err in errors:
            err_table.add_row(
                render_error_badge(err.get("severity", "Medium")),
                err.get("title", ""),
                f"{err.get('impact', '')}\n[dim]→ {err.get('fix', '')}[/dim]"
            )
        console.print(Panel(err_table, title="[bold red]What's Actively Costing Them Customers / Revenue[/bold red]", border_style="red"))
    else:
        console.print(Panel(
            "[bold green]✓ Site is reasonably solid — no major conversion killers found.[/bold green]\n"
            "[dim]The opportunity here is growth and new channels, not damage repair.[/dim]",
            title="[bold green]Conversion Health[/bold green]", border_style="green"
        ))

    # ─── Section 4: Biggest Missed Opportunity ────────────────────────────────
    biggest_opp = result.get("biggest_missed_opportunity", "")
    if biggest_opp:
        console.print(Panel(
            f"[bold yellow]{biggest_opp}[/bold yellow]",
            title="[bold yellow]💡 Biggest Opportunity They Are Leaving On The Table[/bold yellow]",
            border_style="yellow",
            padding=(0, 2)
        ))

    # ─── Section 5: Growth Opportunities by Channel ───────────────────────────
    website_opps = result.get("website_opportunities", [])
    mobile_opps = result.get("mobile_app_opportunities", [])
    auto_opps = result.get("automation_opportunities", [])

    has_any = website_opps or mobile_opps or auto_opps
    if has_any:
        opp_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", padding=(0, 1))
        opp_table.add_column("Channel", style="bold", width=16)
        opp_table.add_column("What To Build", width=28)
        opp_table.add_column("What It Would Do For Their Business")

        for s in website_opps[:2]:
            opp_table.add_row("🌐 Website", s.get("opportunity", ""), s.get("business_impact", ""))
        for s in mobile_opps[:2]:
            opp_table.add_row("📱 Mobile App", s.get("opportunity", ""), s.get("business_impact", ""))
        for s in auto_opps[:2]:
            opp_table.add_row("⚡ Automation / AI", s.get("opportunity", ""), s.get("business_impact", ""))

        console.print(Panel(opp_table, title="[bold cyan]Growth Opportunities — What We Can Build[/bold cyan]", border_style="cyan"))

    # ─── Section 6: Matched Products ──────────────────────────────────────────
    products = result.get("relevant_products", [])
    if products:
        prod_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", padding=(0, 1))
        prod_table.add_column("Product", style="bold", width=22)
        prod_table.add_column("What They're Currently Missing", width=26)
        prod_table.add_column("What It Does For Their Business")
        for p in products[:3]:
            gap = p.get("gap_it_fills") or p.get("relevance_reason") or ""
            outcome = p.get("what_it_does_for_them") or p.get("pitch_line") or ""
            prod_table.add_row(
                f"{p.get('product_name', '')}\n[dim]{p.get('category', '')}[/dim]",
                f"[dim]{gap}[/dim]",
                outcome
            )
        console.print(Panel(
            prod_table,
            title="[bold magenta]Matched Products — What We Already Have Built For Them[/bold magenta]",
            border_style="magenta"
        ))

    # ─── Section 5: msg ───────────────────────────────────────────────────────
    msg_text = result.get("draft_msg", "").strip()
    console.print()
    console.print("[bold magenta]msg:[/bold magenta]")
    console.print(Panel(msg_text, border_style="magenta", padding=(1, 2)))

    # ─── Section 6: mail ──────────────────────────────────────────────────────
    mail_subject = result.get("draft_email_subject", "").strip()
    mail_body = result.get("draft_email_body", "").strip()
    mail_display = f"[bold cyan]Subject:[/bold cyan] {mail_subject}\n\n{mail_body}"
    console.print()
    console.print("[bold green]mail:[/bold green]")
    console.print(Panel(mail_display, border_style="green", padding=(1, 2)))


def main():
    parser = argparse.ArgumentParser(description="Movenetics / Element Labs Website Analyzer")
    parser.add_argument("url", nargs="?", help="Website URL to analyze")
    parser.add_argument("--url", dest="opt_url", help="Website URL to analyze")
    args = parser.parse_args()

    input_url = args.url or args.opt_url
    if input_url:
        process_url(input_url)
        return

    print_banner()
    while True:
        console.print("\n[bold yellow]Paste a website link (or type 'exit' to quit):[/bold yellow]")
        url = Prompt.ask("[cyan]Link[/cyan]").strip()
        if url.lower() in ("exit", "quit", "q"):
            console.print("[cyan]Done![/cyan]")
            break
        process_url(url)


if __name__ == "__main__":
    main()
