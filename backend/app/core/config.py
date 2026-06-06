from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TranslationTurbo"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # Redis & Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    # Support full URL for Upstash/Managed Redis (e.g. rediss://...)
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    def model_post_init(self, __context):
        # Use full URL if provided, otherwise construct from host/port
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

        # Celery requires explicit SSL params for rediss://
        # Upstash specifically requires rediss:// and cert params
        if ".upstash.io" in self.CELERY_BROKER_URL and self.CELERY_BROKER_URL.startswith("redis://"):
            self.CELERY_BROKER_URL = self.CELERY_BROKER_URL.replace("redis://", "rediss://", 1)

        if self.CELERY_BROKER_URL.startswith("rediss://") and "ssl_cert_reqs" not in self.CELERY_BROKER_URL:
            separator = "&" if "?" in self.CELERY_BROKER_URL else "?"
            self.CELERY_BROKER_URL += f"{separator}ssl_cert_reqs=none"

        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.CELERY_BROKER_URL

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
