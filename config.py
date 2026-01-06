# config.py
import os
import logging

logger = logging.getLogger('main')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
VIDEO_API_KEY = os.getenv('VIDEO_API_KEY', '')
VIDEO_API_URL = os.getenv('VIDEO_API_URL', '')

GOOGLE_CREDENTIALS_PATH = 'credentials.json'
GOOGLE_TOKEN_PATH = 'token.json'

OUTPUT_DIR = 'generated_videos'
REPORT_DIR = 'analysis_reports'
LOG_DIR = 'logs'

def validate_config():
    try:
        missing = []
        
        if not OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
            logger.warning("OPENAI_API_KEY not set")
        
        if not VIDEO_API_KEY:
            missing.append('VIDEO_API_KEY')
            logger.warning("VIDEO_API_KEY not set")
        
        if not VIDEO_API_URL:
            missing.append('VIDEO_API_URL')
            logger.warning("VIDEO_API_URL not set")
        
        if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
            missing.append('credentials.json')
            logger.warning("credentials.json not found")
        
        if missing:
            print(f"\nWarning: Missing configuration: {', '.join(missing)}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Config validation error: {str(e)}")
        return False# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # API Keys
    mistral_api_key: str = ""
    sarvam_api_key: str = ""  # Optional for Indian language TTS
    video_api_key: str = ""
    video_api_url: str = ""
    
    # Ollama Configuration (ONLY for Phi-3 local fallback)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"  # Only phi3:mini supported via Ollama
    
    # TTS Configuration (100% FREE options)
    tts_provider: str = "huggingface_piper"  # piper, coqui, bark, sarvam, gtts, edge_tts
    tts_language: str = "en"  # en, hi, ta, te, bn, gu, kn, ml, mr, pa
    tts_voice: str = "default"
    tts_speaker: str = "meera"  # For Sarvam: meera, anushka, arvind, etc.
    
    # Google
    google_credentials_path: str = "credentials.json"
    google_token_path: str = "token.json"
    
    # Database
    database_url: str = "sqlite:///./video_synthesis.db"
    redis_url: str = "redis://localhost:6379"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    # Directories
    output_dir: str = "generated_videos"
    temp_dir: str = "temp_files"
    log_dir: str = "logs"
    
    # Video Processing
    manim_quality: str = "medium_quality"
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    
    # WebSocket
    websocket_heartbeat: int = 30
    max_upload_size: int = 100000000
    
    # LLM Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_directories()
    
    def create_directories(self):
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

settings = Settings()
