"""
Claim Pilot Core - Base Configuration

Generic, reusable settings base class using Pydantic Settings.
Each service should create its own Settings class inheriting from BaseSettings.
"""

import os
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict


def _get_env_file() -> Optional[str]:
    """Only load .env file in development."""
    env = os.getenv("ENVIRONMENT", "development")
    if env == "development" and os.path.exists(".env"):
        return ".env"
    return None


class BaseSettings(PydanticBaseSettings):
    """
    Base settings class for Claim Pilot services.
    Inherit and add service-specific fields.
    """

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # Application
    app_name: str = Field(default="claim-pilot", description="Service name")
    environment: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)

    # Database
    database_url: Optional[str] = Field(default=None)
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_pool_timeout: int = Field(default=30)
    db_pool_recycle: int = Field(default=1800)

    # Redis
    redis_url: Optional[str] = Field(default=None)

    # AWS
    aws_region: str = Field(default="us-east-1")
    aws_secrets_prefix: Optional[str] = Field(default=None)

    # Bedrock / LLM
    bedrock_model_id: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0")
    bedrock_embedding_model_id: str = Field(default="amazon.titan-embed-text-v2:0")
    bedrock_knowledge_base_id: Optional[str] = Field(default=None)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: Literal["json", "console"] = Field(default="console")

    @field_validator("log_format", mode="before")
    @classmethod
    def set_log_format_for_production(cls, v, info):
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and v == "console":
            return "json"
        return v

    # Security
    allowed_origins: List[str] = Field(default=["*"])
    api_key: Optional[SecretStr] = Field(default=None)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


# Settings factory
T = TypeVar("T", bound=BaseSettings)
_settings_instance: Optional[BaseSettings] = None


def create_settings(settings_class: Type[T]) -> T:
    """Create and cache a settings instance."""
    global _settings_instance
    if _settings_instance is None or not isinstance(_settings_instance, settings_class):
        _settings_instance = settings_class()
    return _settings_instance


def get_settings() -> BaseSettings:
    """Get the current settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = BaseSettings()
    return _settings_instance


def reload_settings(settings_class: Optional[Type[T]] = None) -> BaseSettings:
    """Force reload settings from environment."""
    global _settings_instance
    if settings_class:
        _settings_instance = settings_class()
    elif _settings_instance:
        _settings_instance = type(_settings_instance)()
    else:
        _settings_instance = BaseSettings()
    return _settings_instance


# AWS Secrets Manager
_secrets_cache: Dict[str, str] = {}


def get_secret(secret_name: str, use_cache: bool = True) -> Optional[str]:
    """Fetch a secret from AWS Secrets Manager (production only)."""
    global _secrets_cache
    if use_cache and secret_name in _secrets_cache:
        return _secrets_cache[secret_name]

    settings = get_settings()
    if not settings.is_production or not settings.aws_secrets_prefix:
        return None

    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        return None

    full_name = f"{settings.aws_secrets_prefix}{secret_name}"
    try:
        client = boto3.client("secretsmanager", region_name=settings.aws_region)
        response = client.get_secret_value(SecretId=full_name)
        secret_value = response.get("SecretString")
        if secret_value and use_cache:
            _secrets_cache[secret_name] = secret_value
        return secret_value
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ("ResourceNotFoundException", "AccessDeniedException"):
            return None
        raise
    except Exception:
        return None


def clear_secrets_cache() -> None:
    global _secrets_cache
    _secrets_cache = {}


# Remote Config Service
_remote_config_cache: Optional[Dict[str, Any]] = None


def get_remote_config(service: str, environment: Optional[str] = None, config_url: Optional[str] = None, timeout: float = 5.0, use_cache: bool = True) -> Dict[str, Any]:
    """Fetch configuration from a central config service."""
    global _remote_config_cache
    if use_cache and _remote_config_cache is not None:
        return _remote_config_cache

    try:
        import httpx
    except ImportError:
        raise ImportError("httpx is required for remote config.")

    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    if config_url is None:
        config_url = os.getenv("CONFIG_SERVICE_URL", "http://localhost:8080")

    url = f"{config_url}/config/{service}/{environment}"
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            config = data.get("config", {})
            if use_cache:
                _remote_config_cache = config
            return config
    except Exception:
        return {}


def clear_remote_config_cache() -> None:
    global _remote_config_cache
    _remote_config_cache = None


def get_config_value(key: str, default: Any = None, service: Optional[str] = None, environment: Optional[str] = None) -> Any:
    """Get a specific config value (supports dot notation for nested keys)."""
    if service is None:
        settings = get_settings()
        service = settings.app_name
    config = get_remote_config(service=service, environment=environment)
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value
