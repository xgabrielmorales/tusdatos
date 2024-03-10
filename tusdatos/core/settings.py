from typing import Any, Optional, Union

from pydantic import ValidationInfo, field_validator
from pydantic.networks import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_HOST: str
    MONOG_URI: Optional[Union[MongoDsn, str]] = None

    @field_validator("MONOG_URI", mode="before")
    @classmethod
    def assemble_mongo_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        url = MongoDsn.build(
            scheme="mongodb",
            host=values.data["MONGO_HOST"],
            username=values.data["MONGO_INITDB_ROOT_USERNAME"],
            password=values.data["MONGO_INITDB_ROOT_PASSWORD"],
        )

        return str(url)


settings = Settings()
