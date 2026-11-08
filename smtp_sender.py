import smtplib
import ssl
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid
from typing import Dict, Any, Tuple
from config import config

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "sent_history.json")


class SMTPSender:
    def __init__(self):
        self.host = config.smtp_host
        self.port = config.smtp_port
        self.user = config.smtp_user
        # For Google Workspace app passwords, strip spaces if present
        if "gmail" in self.host.lower() and config.smtp_password:
            self.password = config.smtp_password.replace(" ", "")
        else:
            self.password = config.smtp_password.strip() if config.smtp_password else ""
        self.use_tls = config.smtp_use_tls
        self.use_ssl = config.smtp_use_ssl
        self.ignore_cert = config.smtp_ignore_cert_errors
        self.sender_name = config.sender_name
        self.sender_email = config.sender_email

    def send_email(
        self,
        receiver_email: str,
        subject: str,
        body_text: str,
        body_html: str = "",
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Sends a personalized email via SMTP.
        Returns: (success: bool, message: str)
        """
        if not receiver_email or "@" not in receiver_email:
            return False, f"Invalid receiver email address: '{receiver_email}'"

        if dry_run:
            self._log_history(receiver_email, subject, status="DRY_RUN", note="Simulated send (dry-run)")
            return True, f"[DRY RUN] Email successfully simulated for {receiver_email}. No mail was sent."

        if not self.password or self.password.startswith("your_"):
            return False, (
                "SMTP password is not configured in .env.\n"
                "Please update SMTP_PASSWORD in your .env file with your email or app password."
            )

        # Build MIME multipart message
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((self.sender_name, self.sender_email))
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=self.sender_email.split("@")[-1])
        msg["Reply-To"] = self.sender_email

        # Attach Plain Text part
        part1 = MIMEText(body_text, "plain", "utf-8")
        msg.attach(part1)

        # Attach HTML part if provided
        if body_html:
            part2 = MIMEText(body_html, "html", "utf-8")
            msg.attach(part2)

        context = ssl.create_default_context()
        if self.ignore_cert:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        try:
            if self.use_ssl or self.port == 465:
                # SSL connection (typically Port 465 for cPanel or SSL hosts)
                with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=20) as server:
                    if self.user and self.password:
                        server.login(self.user, self.password)
                    server.sendmail(self.sender_email, [receiver_email], msg.as_string())
            else:
                # Standard SMTP with STARTTLS (typically Port 587)
                with smtplib.SMTP(self.host, self.port, timeout=20) as server:
                    server.ehlo()
                    if self.use_tls:
                        server.starttls(context=context)
                        server.ehlo()
                    if self.user and self.password:
                        server.login(self.user, self.password)
                    server.sendmail(self.sender_email, [receiver_email], msg.as_string())

            self._log_history(receiver_email, subject, status="SENT", note="Delivered via SMTP")
            return True, f"Email successfully delivered to {receiver_email}!"

        except smtplib.SMTPAuthenticationError as e:
            if "gmail" in self.host.lower():
                err_msg = (
                    f"SMTP Authentication Failed: {str(e)}\n"
                    "Tip: For Gmail/Google Workspace, generate a 16-character App Password at:\n"
                    "Google Account > Security > 2-Step Verification > App Passwords"
                )
            else:
                err_msg = (
                    f"cPanel / SMTP Authentication Failed: {str(e)}\n"
                    "Tip for cPanel:\n"
                    "1. Ensure SMTP_USER is your full email address (e.g. raza.shaikh@moveneticsdigital.com)\n"
                    "2. Ensure SMTP_PASSWORD is your exact cPanel email account password\n"
                    "3. Check your cPanel > Email Accounts > 'Connect Devices' for exact host & port."
                )
            self._log_history(receiver_email, subject, status="FAILED", note=err_msg)
            return False, err_msg

        except ssl.SSLCertVerificationError as e:
            err_msg = (
                f"SSL Certificate Verification Failed: {str(e)}\n"
                "Tip for cPanel: If your server uses a self-signed or shared SSL certificate,\n"
                "add 'SMTP_IGNORE_CERT_ERRORS=true' in your .env file."
            )
            self._log_history(receiver_email, subject, status="FAILED", note=err_msg)
            return False, err_msg

        except Exception as e:
            err_msg = f"Failed to send email: {type(e).__name__} - {str(e)}"
            self._log_history(receiver_email, subject, status="FAILED", note=err_msg)
            return False, err_msg

    def _log_history(self, receiver_email: str, subject: str, status: str, note: str = ""):
        """Keep a local audit log of sent outreach."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": self.sender_email,
            "receiver": receiver_email,
            "subject": subject,
            "status": status,
            "note": note
        }
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(entry)
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass

