import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, set_key

# Load existing .env if present
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(env_path)

class Settings(BaseSettings):
    NVIDIA_NIM_API_KEY: str = os.getenv("NVIDIA_NIM_API_KEY", "")
    
    # Model Mappings
    MODEL_OPUS: str = os.getenv("MODEL_OPUS", "deepseek-ai/deepseek-v4-pro")
    MODEL_SONNET: str = os.getenv("MODEL_SONNET", "openai/gpt-oss-120b")
    MODEL_HAIKU: str = os.getenv("MODEL_HAIKU", "z-ai/glm-5.1")
    MODEL_FALLBACK: str = os.getenv("MODEL_FALLBACK", "openai/gpt-oss-20b")

    # Defaults
    DEFAULT_TEMPERATURE: float = 1.0
    DEFAULT_TOP_P: float = 1.0
    DEFAULT_MAX_TOKENS: int = 16384
    DEFAULT_REASONING_EFFORT: str = "medium"

    # Behavior
    ENABLE_OPTIMIZATIONS: bool = True
    ENABLE_THINKING: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8082

settings = Settings()

def save_config():
    """Saves current settings back to .env file"""
    set_key(env_path, "NVIDIA_NIM_API_KEY", settings.NVIDIA_NIM_API_KEY)
    set_key(env_path, "MODEL_OPUS", settings.MODEL_OPUS)
    set_key(env_path, "MODEL_SONNET", settings.MODEL_SONNET)
    set_key(env_path, "MODEL_HAIKU", settings.MODEL_HAIKU)
    set_key(env_path, "MODEL_FALLBACK", settings.MODEL_FALLBACK)
    
    set_key(env_path, "DEFAULT_TEMPERATURE", str(settings.DEFAULT_TEMPERATURE))
    set_key(env_path, "DEFAULT_MAX_TOKENS", str(settings.DEFAULT_MAX_TOKENS))
    set_key(env_path, "DEFAULT_REASONING_EFFORT", settings.DEFAULT_REASONING_EFFORT)
    set_key(env_path, "ENABLE_THINKING", str(settings.ENABLE_THINKING).lower())
    set_key(env_path, "ENABLE_OPTIMIZATIONS", str(settings.ENABLE_OPTIMIZATIONS).lower())
