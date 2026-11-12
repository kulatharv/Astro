"""Global Application Settings & Environment Configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Astro-Platform"
    APP_NAME: str = "Astro-Platform"
    app_name: str = "Astro-Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "astrologic-ai-super-secret-jwt-key-2026-production-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "sqlite:///./astrologic.db"
    REDIS_URL: Optional[str] = None

    # LLM Settings
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    llm_provider: str = "auto"
    LLM_PROVIDER: str = "auto"  # 'groq', 'gemini', 'openai', or 'auto'

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"
    SESSION_SECRET_KEY: str = "astrologic-session-secret-key-2026"
    session_secret_key: str = "astrologic-session-secret-key-2026"

    # Chart Cache Settings
    CHART_CACHE_ENABLED: bool = True
    CHART_CACHE_TTL_SECONDS: int = 2592000  # 30 days
    CHART_CACHE_LRU_SIZE: int = 1000

    # Ephemeris Settings
    EPHE_PATH: Optional[str] = None  # Path to Swiss Ephemeris .se1 files; if None, falls back safely to Moshier mode
    EPHEMERIS_MODE: str = "auto"  # 'auto', 'swiss_ephemeris' (strict), or 'moshier' (force fallback)
    REQUIRE_SWIEPH: bool = False  # If True, fails startup/initialization if .se1 Swiss Ephemeris files are not loaded

    # Combustion Settings
    TREAT_MOON_AS_COMBUST: bool = True  # If True, Moon within 12° of Sun (Surya Siddhanta Ch. 10 v. 1) is flagged combust; if False, classified as Amavasya

    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS or ["*"]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "prod")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __getattr__(self, name: str):
        # Prevent recursion when checking attributes
        upper_name = name.upper()
        if upper_name in self.__class__.model_fields or upper_name in self.__dict__ or hasattr(self.__class__, upper_name):
            return getattr(self, upper_name)
        lower_name = name.lower()
        if lower_name in self.__class__.model_fields or lower_name in self.__dict__ or hasattr(self.__class__, lower_name):
            return getattr(self, lower_name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")





def validate_settings(s: Settings = None) -> bool:
    """Validate critical security settings."""
    if s is None:
        s = settings
    sec_key = getattr(s, "secret_key", None) or getattr(s, "SECRET_KEY", None)
    if not sec_key:
        raise RuntimeError("Missing required environment variable: SECRET_KEY")
    return True



settings = Settings()


