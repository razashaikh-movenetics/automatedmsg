import os
from dataclasses import dataclass
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)


@dataclass
class Config:
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    company_name: str = os.getenv("COMPANY_NAME", "Movenetics").strip()
    company_full_name: str = os.getenv("COMPANY_FULL_NAME", "Movenetics Digital").strip()
    sender_name: str = os.getenv("SENDER_NAME", "Raza Shaikh").strip()
    sender_email: str = os.getenv("SENDER_EMAIL", "raza.shaikh@moveneticsdigital.com").strip()

    def is_configured(self) -> bool:
        return bool(self.deepseek_api_key and not self.deepseek_api_key.startswith("your_"))


config = Config()
