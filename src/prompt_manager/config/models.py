from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ConsoleLoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    dependency_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class FileLoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    dependency_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    rotation: Literal["S", "M", "H", "D", "midnight"]
    retain_days: int = Field(ge=0, le=1000)
    utc_time: bool


class LoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    console: ConsoleLoggingConfig
    file: FileLoggingConfig


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    logging: LoggingConfig
