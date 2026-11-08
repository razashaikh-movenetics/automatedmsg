#!/usr/bin/env python3
import sys
import argparse
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

from config import config
from deepseek_mailer import DeepSeekMailer
from smtp_sender import SMTPSender

console = Console()


def print_banner():
    """Renders the application header banner."""
    content = f"""[bold cyan]AI Lead Outreach & Personalized Email Pipeline[/bold cyan]
[dim]Powered by DeepSeek LLM & SMTP[/dim]

[bold]Sender:[/bold] [green]{config.sender_name}[/green] <{config.sender_email}>
[bold]Company:[/bold] {config.sender_company} | {config.sender_title}
[bold]DeepSeek Model:[/bold] {config.deepseek_model} ({'configured' if config.is_deepseek_configured() else '[yellow]demo fallback / needs key[/yellow]'})
[bold]SMTP Server:[/bold] {config.smtp_host}:{config.smtp_port} ({'configured' if config.is_smtp_configured() else '[yellow]needs password in .env[/yellow]'})"""

    console.print(Panel(content, border_style="cyan", box=box.ROUNDED))


def interactive_mode():
    """Runs the step-by-step terminal prompt interface."""
    print_banner()

    # Step 1: Available Product / Service
    console.print("\n[bold yellow]Step 1: Your Available Product / Solution[/bold yellow]")
    default_product = "Custom AI Workflow Automation & Intelligent Lead Engine"
    product_available = Prompt.ask(
        "Enter the product/service you are offering",
        default=default_product
    ).strip()

    while True:
        # Step 2: Receiver Information
        console.print("\n[bold yellow]Step 2: Prospective Client Details[/bold yellow]")
        receiver_email = Prompt.ask("Receiver Email address").strip()
        while not receiver_email or "@" not in receiver_email:
            console.print("[red]Please enter a valid email address containing '@'[/red]")
            receiver_email = Prompt.ask("Receiver Email address").strip()

        receiver_name = Prompt.ask("Receiver Name or Company", default="Prospective Partner").strip()

        # Step 3: What the receiver wants / needs
        console.print("\n[bold yellow]Step 3: What does the receiver want / need?[/bold yellow]")
        console.print("[dim](e.g. 'Looking to automate client follow-ups', 'Needs 24/7 customer support without hiring more staff', 'Wants higher B2B lead conversions')[/dim]")
        receiver_wants = Prompt.ask("Receiver's goal / requirement / pain point").strip()
        while not receiver_wants:
            console.print("[red]Please enter what the receiver is looking for so we can tailor the pitch.[/red]")
            receiver_wants = Prompt.ask("Receiver's goal / requirement / pain point").strip()

        # Step 4: Tone selection
        tones = [
            "Consultative & High-Value",
            "Executive & Direct",
            "Conversational & Friendly",
            "Results & ROI Focused"
        ]
        console.print("\n[bold yellow]Step 4: Select Email Tone[/bold yellow]")
        for idx, t in enumerate(tones, start=1):
            console.print(f"  [cyan][{idx}][/cyan] {t}")
        tone_choice = Prompt.ask("Choose tone [1-4]", choices=["1", "2", "3", "4"], default="1")
        selected_tone = tones[int(tone_choice) - 1]

        # Step 5: Generate with DeepSeek
        mailer = DeepSeekMailer()
        sender = SMTPSender()

        custom_notes = ""
        while True:
            with console.status("[bold green]Generating personalized email with DeepSeek...[/bold green]"):
                email_data = mailer.generate_personalized_email(
                    receiver_email=receiver_email,
                    receiver_name=receiver_name,
                    receiver_wants=receiver_wants,
                    product_available=product_available,
                    tone=selected_tone,
                    custom_instructions=custom_notes
                )

            # Display Preview
            preview_table = Table(show_header=False, box=box.SIMPLE)
            preview_table.add_column("Field", style="bold cyan", width=12)
            preview_table.add_column("Content")
            preview_table.add_row("To", f"{receiver_name} <{receiver_email}>")
            preview_table.add_row("From", f"{config.sender_name} <{config.sender_email}>")
            preview_table.add_row("Subject", email_data.get("subject", ""))
            if email_data.get("key_angle"):
                preview_table.add_row("Angle", f"[italic yellow]{email_data['key_angle']}[/italic yellow]")

            console.print("\n")
            console.print(Panel(preview_table, title="[bold]Email Metadata[/bold]", border_style="blue"))
            console.print(Panel(email_data.get("body_text", ""), title="[bold green]Email Body Preview[/bold green]", border_style="green"))

            if email_data.get("warning"):
                console.print(f"[yellow]Note: {email_data['warning']}[/yellow]")

            # Action menu
            console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
            console.print("  [green][1] Send Email Now[/green]")
            console.print("  [cyan][2] Regenerate Email[/cyan] (add specific instructions or tweak)")
            console.print("  [magenta][3] Edit Subject & Body Manually[/magenta]")
            console.print("  [yellow][4] Dry Run (simulate send without contacting server)[/yellow]")
            console.print("  [red][5] Skip / Next Client[/red]")
            console.print("  [bold red][0] Exit[/bold red]")

            action = Prompt.ask("Select action", choices=["1", "2", "3", "4", "5", "0"], default="1")

            if action == "1":
                # Real Send
                with console.status("[bold green]Connecting to SMTP server and dispatching email...[/bold green]"):
                    success, msg = sender.send_email(
                        receiver_email=receiver_email,
                        subject=email_data.get("subject", ""),
                        body_text=email_data.get("body_text", ""),
                        body_html=email_data.get("body_html", ""),
                        dry_run=False
                    )
                if success:
                    console.print(f"\n[bold green]✓ SUCCESS:[/bold green] {msg}")
                else:
                    console.print(f"\n[bold red]✗ FAILED:[/bold red] {msg}")
                break

            elif action == "2":
                # Regenerate
                custom_notes = Prompt.ask("Enter instructions for re-generation (e.g. 'make it shorter', 'focus on pricing')").strip()
                continue

            elif action == "3":
                # Manual edit
                new_sub = Prompt.ask("Edit Subject", default=email_data.get("subject", "")).strip()
                console.print("[dim]Edit body text below:[/dim]")
                new_body = Prompt.ask("Body", default=email_data.get("body_text", "")).strip()
                email_data["subject"] = new_sub
                email_data["body_text"] = new_body
                email_data["body_html"] = f"<pre style='font-family: sans-serif;'>{new_body}</pre>"
                continue

            elif action == "4":
                # Dry run
                success, msg = sender.send_email(
                    receiver_email=receiver_email,
                    subject=email_data.get("subject", ""),
                    body_text=email_data.get("body_text", ""),
                    body_html=email_data.get("body_html", ""),
                    dry_run=True
                )
                console.print(f"\n[bold yellow]ℹ DRY RUN RESULT:[/bold yellow] {msg}")
                break

            elif action == "5":
                console.print("[dim]Skipped this client.[/dim]")
                break

            elif action == "0":
                console.print("[cyan]Exiting outreach pipeline. Have a great day![/cyan]")
                sys.exit(0)

        # Ask if user wants to process another client
        if not Confirm.ask("\nWould you like to pitch another client?", default=True):
            console.print("[cyan]Exiting outreach pipeline. Happy prospecting![/cyan]")
            break


def cli_mode(args):
    """Handles direct non-interactive CLI arguments."""
    mailer = DeepSeekMailer()
    sender = SMTPSender()

    email_data = mailer.generate_personalized_email(
        receiver_email=args.to,
        receiver_name=args.name or "Partner",
        receiver_wants=args.wants,
        product_available=args.product,
        tone=args.tone or "Consultative & High-Value"
    )

    console.print(f"[bold]Target:[/bold] {args.name} <{args.to}>")
    console.print(f"[bold]Subject:[/bold] {email_data.get('subject')}")
    console.print("\n" + email_data.get("body_text", ""))

    if args.send:
        success, msg = sender.send_email(
            receiver_email=args.to,
            subject=email_data.get("subject", ""),
            body_text=email_data.get("body_text", ""),
            body_html=email_data.get("body_html", ""),
            dry_run=args.dry_run
        )
        if success:
            console.print(f"\n[bold green]✓ SUCCESS:[/bold green] {msg}")
        else:
            console.print(f"\n[bold red]✗ FAILED:[/bold red] {msg}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Automated Lead Pitch & Personalized Mailer Pipeline")
    parser.add_argument("--to", help="Receiver email address")
    parser.add_argument("--name", help="Receiver name / company", default="Partner")
    parser.add_argument("--wants", help="What the receiver wants / needs / pain points")
    parser.add_argument("--product", help="Your available product or service to pitch", default="Custom AI Automation Pipeline")
    parser.add_argument("--tone", help="Pitch tone", default="Consultative & High-Value")
    parser.add_argument("--send", action="store_true", help="Send email directly via SMTP")
    parser.add_argument("--dry-run", action="store_true", help="Simulate email sending without connecting")

    args = parser.parse_args()

    # If receiver arguments are provided directly via CLI flags
    if args.to and args.wants:
        cli_mode(args)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

