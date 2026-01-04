from typing import Annotated, Optional

from pydantic import AnyUrl, BaseModel, Field, UrlConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AVAILABILITYCHECKER_", env_nested_delimiter="__")

    class MongoDBConfig(BaseModel):
        username: Optional[str] = Field(None, description="Database username")
        password: Optional[str] = Field(None, description="Database password")
        host: str = Field(..., description="Database host address")
        port: int = Field(27017, description="Database port")
        db_name: str = Field(..., description="Database name")

    mongodb: MongoDBConfig