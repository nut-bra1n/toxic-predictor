import pathlib
from typing import Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASEDIR: str = str(pathlib.Path(__file__).parent.parent)

    # Config from APP group
    DEBUG: Optional[bool] = False
    LOGFILE: Optional[str] = 'predictor.log'

    # Config from LLM group
    LOCAL_MODEL_PATH: Optional[str] = None
    OLLAMA_BASE_URL: Optional[AnyHttpUrl] = None
    OPENAI_API_BASE: Optional[AnyHttpUrl] = None
    OPENAI_API_KEY: Optional[str] = 'EMPTY'
    MODEL_NAME: Optional[str] = None
    TEMPERATURE: Optional[float] = 0.7

    # Config from TELEGRAM BOT group
    TOKEN: str

    # Config from TELEGRAM API group
    API_ID: str
    API_HASH: str

    # Config from MTPROTO PROXY group
    PROXY_HOST: str
    PROXY_PORT: int
    PROXY_SECRET: str

    model_config = SettingsConfigDict(env_file=f'{BASEDIR}/.env',
                                      env_ignore_empty=True,
                                      extra='allow')


settings = Settings()
