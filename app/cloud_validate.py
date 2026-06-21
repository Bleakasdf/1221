from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


REQUIRED_FILES = [
    "app/cloud_web.py",
    "app/main.py",
    "app/bot.py",
    "app/config.py",
    "app/database.py",
    "requirements.txt",
    "Dockerfile",
    "Procfile",
    "render.yaml",
    ".env.cloud.example",
    "FREE_24_7_SETUP.md",
]

FORBIDDEN_FILES = [
    ".env",
    "training_bot.db",
]


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    forbidden = [path for path in FORBIDDEN_FILES if (ROOT / path).exists()]

    env_example = (ROOT / ".env.cloud.example").read_text(encoding="utf-8")
    checks = {
        "BOT_TOKEN in env example": "BOT_TOKEN=" in env_example,
        "Postgres DATABASE_URL in env example": "DATABASE_URL=postgres" in env_example,
        "TELEGRAM_PROXY empty for cloud": "TELEGRAM_PROXY=" in env_example,
        "aiohttp-socks dependency present": "aiohttp-socks" in (ROOT / "requirements.txt").read_text(encoding="utf-8"),
        "psycopg2 dependency present": "psycopg2-binary" in (ROOT / "requirements.txt").read_text(encoding="utf-8"),
        "render launch command present": "run_render.py" in (ROOT / "render.yaml").read_text(encoding="utf-8"),
        "render launcher present": (ROOT / "run_render.py").exists(),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    if missing or forbidden or failed_checks:
        if missing:
            print("Missing files:")
            for path in missing:
                print(f"- {path}")
        if forbidden:
            print("Forbidden local-only files found:")
            for path in forbidden:
                print(f"- {path}")
        if failed_checks:
            print("Failed checks:")
            for name in failed_checks:
                print(f"- {name}")
        raise SystemExit(1)

    print("Cloud package looks ready.")


if __name__ == "__main__":
    main()
