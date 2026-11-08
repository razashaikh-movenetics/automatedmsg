import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load .env file from the current project directory
load_dotenv()


@dataclass
class AppConfig:
    # DeepSeek Configuration
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    # SMTP Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port: int = int(os.getenv("SMTP_PORT", "587").strip())
    smtp_user: str = os.getenv("SMTP_USER", "raza.shaikh@moveneticsdigital.com").strip()
    smtp_password: str = os.getenv("SMTP_PASSWORD", "").strip()
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes")
    smtp_ignore_cert_errors: bool = os.getenv("SMTP_IGNORE_CERT_ERRORS", "false").lower() in ("true", "1", "yes")

    # Sender Identity
    sender_name: str = os.getenv("SENDER_NAME", "Raza Shaikh").strip()
    sender_email: str = os.getenv("SENDER_EMAIL", "raza.shaikh@moveneticsdigital.com").strip()
    sender_company: str = os.getenv("SENDER_COMPANY", "Movenetics Digital").strip()
    sender_title: str = os.getenv("SENDER_TITLE", "Founder & Solutions Lead").strip()

    def is_deepseek_configured(self) -> bool:
        """Check if a valid DeepSeek API key is provided."""
        return bool(self.deepseek_api_key and not self.deepseek_api_key.startswith("your_"))

    def is_smtp_configured(self) -> bool:
        """Check if SMTP connection credentials are provided."""
        return bool(
            self.smtp_host
            and self.smtp_user
            and self.smtp_password
            and not self.smtp_password.startswith("your_")
        )

    def mask_secret(self, val: str) -> str:
        """Safely mask passwords/keys for display."""
        if not val:
            return "[Not Set]"
        if len(val) <= 6:
            return "******"
        return f"{val[:3]}...{val[-3:]}"


# Global configuration instance
config = AppConfig()

