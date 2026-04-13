# app/core/config.py
from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración cargada desde variables de entorno o archivo .env.

    Acepta las variables individuales de Postgres y construye DATABASE_URL
    automáticamente con @computed_field, o usa DATABASE_URL directamente
    si se provee en el entorno.

    Orden de prioridad (pydantic-settings):
      1. Variables de entorno del sistema
      2. Archivo .env
      3. Defaults declarados en la clase
    """

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # Ignorar variables extra del .env que no sean campos declarados
        "extra": "ignore",
    }


settings = Settings()
