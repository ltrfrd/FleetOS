"""
backend/core/config.py
----------------------
Central application configuration loaded from environment variables.

All settings are declared as typed fields on the Settings class. pydantic-settings
reads values from the environment first, then falls back to the .env file, then
uses field defaults where defined. Any required field (no default) that is missing
from both sources will raise a ValidationError at startup — intentional, so the
app never runs silently misconfigured.

Usage anywhere in the application:
    from backend.core.config import settings

    print(settings.PROJECT_NAME)
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration surface.

    Field loading order (highest to lowest priority):
      1. Environment variables (e.g. export SECRET_KEY=...)
      2. Variables defined in the .env file at the project root
      3. Default values declared on each field below

    Fields without a default are required and will cause a startup error if
    absent from the environment or .env file.
    """

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    DATABASE_URL: str
    """
    Full PostgreSQL connection string.
    Expected format: postgresql://user:password@host:port/dbname
    Must be provided — no default. The application will not start without it.
    """

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    SECRET_KEY: str
    """
    Secret used to sign and verify JWT tokens.
    Must be a long, randomly generated string (e.g. output of `openssl rand -hex 32`).
    Must be provided — no default. Never commit a real value to source control.
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """
    Lifetime of a short-lived access token, in minutes.
    Default: 30 minutes.
    """

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    """
    Lifetime of a long-lived refresh token, in days.
    Default: 7 days.
    """

    # ------------------------------------------------------------------
    # Application metadata
    # ------------------------------------------------------------------

    PROJECT_NAME: str = "FleetOS"
    """
    Human-readable application name. Shown in the OpenAPI docs title.
    Default: "FleetOS".
    """

    VERSION: str = "1.0.0"
    """
    Application version string. Shown in the OpenAPI docs and health endpoints.
    Default: "1.0.0".
    """

    # ------------------------------------------------------------------
    # pydantic-settings configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Extra fields in .env that are not declared above are silently ignored
        # rather than raising a validation error.
        extra="ignore",
    )


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

settings = Settings()
"""
Single shared Settings instance imported across the application.

Import pattern:
    from backend.core.config import settings
"""
