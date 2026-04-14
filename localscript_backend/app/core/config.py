from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # === DATABASE ===
    database_url: str

    # === OLLAMA ===
    ollama_base_url: str
    ollama_model: str
    request_timeout_seconds: float
    use_stub_model: bool

    # === OLLAMA OPTIONS ===
    ollama_num_ctx: int
    ollama_num_predict: int
    ollama_batch: int
    ollama_parallel: int
    ollama_temperature: float

    # === APP ===
    app_host: str
    app_port: int 
    app_title: str
    app_debug: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()