from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class LLMSettings(BaseSettings):
    model_name: str = "gpt-3.5-turbo"
    model_base_url: str = "http://api.openai.com/v1"
    model_api_key: str = ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="./config.toml")

    llm: LLMSettings
    # Threshold for requests per minute to trigger detection
    DDOS_THRESHOLD: int = 100
    # Time window in seconds for rate limiting
    RATE_LIMIT_WINDOW: int = 60
    # Email to notify in case of DDoS detection
    ALERT_EMAIL: str = "admin@example.com"
    # Logging level for the application
    LOGGING_LEVEL: str = "INFO"
    # Database URI for storing logs and alerts
    DATABASE_URI: str = "sqlite:///ddos_detection.db"
    RISK_THRESHOLD: float = 0.7
    MAX_NORMAL_RPS: int = 10
    MAX_NORMAL_IP_CONCENTRATION: int = 5

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = Settings(llm=LLMSettings())


if __name__ == "__main__":
    print(settings.llm.model_name)
