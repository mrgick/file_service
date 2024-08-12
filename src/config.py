from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, DirectoryPath


class Settings(BaseSettings):
    database_url: PostgresDsn
    directory_path: DirectoryPath
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
