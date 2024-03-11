from typing import Any, Optional, Union

from pydantic import ValidationInfo, field_validator
from pydantic.networks import MongoDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    SECRET_KEY: str

    POSTGRES_HOST: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_URL: Optional[Union[PostgresDsn, str]] = None

    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_HOST: str
    MONOG_URI: Optional[Union[MongoDsn, str]] = None

    @field_validator("MONOG_URI", mode="before")
    @classmethod
    def assemble_mongo_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        uri = MongoDsn.build(
            scheme="mongodb",
            host=values.data["MONGO_HOST"],
            username=values.data["MONGO_INITDB_ROOT_USERNAME"],
            password=values.data["MONGO_INITDB_ROOT_PASSWORD"],
        )

        return str(uri)

    @field_validator("POSTGRES_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        url = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=values.data["POSTGRES_HOST"],
            password=values.data["POSTGRES_PASSWORD"],
            username=values.data["POSTGRES_USER"],
            path=values.data["POSTGRES_DB"],
        )

        return str(url)


settings = Settings()
