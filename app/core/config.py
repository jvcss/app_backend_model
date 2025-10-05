import os
from starlette.config import Config
import logging

envfile=".env"
config = Config(envfile)
logging.basicConfig(level=logging.INFO)

if config("MODE", default="Development") == "Development":
    logging.info("Running in Development mode")
    CELERY_BROKER_URL: str = config("CELERY_BROKER_URL_EXTERNAL", default="redis://localhost:6397/0")
    CELERY_RESULT_BACKEND: str = config("CELERY_BROKER_URL_EXTERNAL", default="redis://localhost:6397/0")
else:
    logging.info("Running in Production mode")
    CELERY_BROKER_URL: str = config("CELERY_BROKER_URL", default="redis://redis_app_backend:6379/0")
    CELERY_RESULT_BACKEND: str = config("CELERY_RESULT_BACKEND", default="redis://redis_app_backend:6379/0")

class Settings:
    """
        Auto-load all variables from `.env` into uppercase attributes,
        fallback to environment variables. Assumes `.env` is in project root.
    usage:\n
        print(settings.ANY_VARIABLE)
    """
    def __init__(self):
        self._config = Config(envfile)  # Starlette já busca na raiz do projeto
        # Carrega todas as chaves do .env
        for key in self._config.file_values.keys():  # ._dict: todas as chaves carregadas do .env
            value = self._config(key)
            setattr(self, key.upper(), value)
        # Complementa com variáveis de ambiente ainda não definidas
        for key, value in os.environ.items():
            if not hasattr(self, key.upper()):
                setattr(self, key.upper(), value)
    def __repr__(self):
        entries = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"<Settings {entries}>"
settings = Settings()
