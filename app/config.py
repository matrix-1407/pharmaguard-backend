"""Application configuration via environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    port: int = int(os.getenv("PORT", "8080"))
    gemini_api: str = os.getenv("GEMINI_API", "")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


settings = Settings()
