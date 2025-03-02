"""
Configuration management for the application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    
    config = {
        # Audio settings
        'SAMPLE_RATE': int(os.getenv('SAMPLE_RATE', 16000)),
        'CHANNELS': int(os.getenv('CHANNELS', 1)),
        'CHUNK_SIZE': int(os.getenv('CHUNK_SIZE', 1024)),
        
        # Model paths
        'WHISPER_MODEL_PATH': os.getenv('WHISPER_MODEL_PATH'),
        'LLAMA_MODEL_PATH': os.getenv('LLAMA_MODEL_PATH'),
        'VECTOR_DB_PATH': os.getenv('VECTOR_DB_PATH'),
        
        # Database settings
        'DB_CONNECTION_STRING': os.getenv('DB_CONNECTION_STRING'),
        
        # Logging
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_PATH': os.getenv('LOG_PATH'),
    }
    
    return config
