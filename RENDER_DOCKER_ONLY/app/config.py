from functools import lru_cache
import os
from pathlib import Path
import sys

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.bot_token = os.getenv("BOT_TOKEN", "")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///training_bot.db")
        self.allowed_telegram_ids = os.getenv("ALLOWED_TELEGRAM_IDS", "")
        self.export_dir = os.getenv("EXPORT_DIR", "exports")
        self.telegram_proxy = self._resolve_telegram_proxy(os.getenv("TELEGRAM_PROXY", "auto"))

    def _resolve_telegram_proxy(self, value: str) -> str:
        if value.lower() != "auto":
            return value
        if sys.platform != "win32":
            return ""
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
                enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
                proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
        except OSError:
            return ""
        if not enabled or not proxy_server:
            return ""
        proxy = proxy_server.split(";")[0]
        if "=" in proxy:
            proxy = proxy.split("=", 1)[1]
        if proxy.startswith(("http://", "https://", "socks4://", "socks5://")):
            return proxy
        return f"http://{proxy}"

    @property
    def allowed_ids(self) -> set[int]:
        raw_ids = [item.strip() for item in self.allowed_telegram_ids.split(",") if item.strip()]
        return {int(item) for item in raw_ids}

    @property
    def export_path(self) -> Path:
        path = Path(self.export_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
