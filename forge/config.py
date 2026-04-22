"""Forge POC - Configuration"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Alternative: Direct OpenAI
    openai_api_key: str = ""
    
    # Directories
    upload_dir: Path = Path("./data/uploads")
    packages_dir: Path = Path("./data/packages")
    policies_dir: Path = Path("./data/policies")
    chroma_persist_dir: Path = Path("./data/chroma")
    
    # App settings
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def ensure_dirs(self):
        """Create required directories if they don't exist."""
        for d in [self.upload_dir, self.packages_dir, self.policies_dir, self.chroma_persist_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    @property
    def use_azure(self) -> bool:
        """Check if Azure OpenAI is configured."""
        return bool(self.azure_openai_endpoint and self.azure_openai_api_key)


settings = Settings()
settings.ensure_dirs()
