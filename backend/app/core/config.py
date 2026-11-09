from pydantic_settings import BaseSettings, SettingsConfigDict

# Committed in .env.example, so it is public knowledge. Anyone who knows it can
# forge tokens for any user, which is why startup refuses to accept it.
INSECURE_JWT_SECRET = "change-me-to-a-long-random-string"


class Settings(BaseSettings):
    database_url: str = "postgresql://ufc:ufc@localhost:5432/ufc"
    jwt_secret: str = INSECURE_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    csv_path: str = "data/ufc-master.csv"
    model_path: str = "ml/ufc_ml.pkl"
    # Comma-separated list of browser origins allowed to call this API.
    # In production this must include the deployed frontend URL.
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=())

    @property
    def sqlalchemy_database_url(self) -> str:
        """Pin the psycopg (v3) driver. A bare postgresql:// URL, which is what Render
        provides, would otherwise leave the driver choice to SQLAlchemy's default."""
        for prefix in ("postgresql://", "postgres://"):
            if self.database_url.startswith(prefix):
                return "postgresql+psycopg://" + self.database_url[len(prefix):]
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_security(self) -> None:
        """Fail loudly rather than silently running with a forgeable token secret."""
        if self.jwt_secret == INSECURE_JWT_SECRET or len(self.jwt_secret) < 32:
            raise RuntimeError(
                "JWT_SECRET is unset, still the placeholder value, or too short. "
                "Anyone could forge login tokens. Generate one with:\n"
                '  python -c "import secrets; print(secrets.token_urlsafe(48))"\n'
                "and set it as the JWT_SECRET environment variable."
            )


settings = Settings()
