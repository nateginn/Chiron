"""
Speech-to-text transcription using Whisper ASR.
"""
import whisper
import torch
import os
from pathlib import Path
from datetime import datetime
from ..utils.logger import get_logger

logger = get_logger(__name__)

class WhisperTranscriber:
    def __init__(self, config):
        self.model_size = config.get('WHISPER_MODEL_SIZE', 'base')
        self.model_path = config.get('WHISPER_MODEL_PATH')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.output_dir = Path(config.get('TRANSCRIPTION_OUTPUT_DIR', 'data/transcriptions'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.load_model()
        
    def load_model(self):
        """Load the Whisper ASR model."""
        logger.info(f"Loading Whisper model '{self.model_size}' on {self.device}...")
        try:
            # Check if we have a local model file
            if self.model_path and os.path.exists(self.model_path):
                logger.info(f"Loading model from local path: {self.model_path}")
                self.model = whisper.load_model(self.model_path, device=self.device)
            else:
                # Download and load the model from the Whisper repository
                logger.info(f"Downloading model '{self.model_size}' from Whisper repository")
                self.model = whisper.load_model(self.model_size, device=self.device)
                
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise
        
    def transcribe(self, audio_path):
        """Transcribe audio file to text."""
        logger.info(f"Transcribing audio file: {audio_path}")
        try:
            # Ensure audio_path is a string
            audio_path_str = str(audio_path)
            
            # Run transcription
            result = self.model.transcribe(
                audio_path_str,
                fp16=torch.cuda.is_available(),
                language="en",
                task="transcribe"
            )
            
            # Save transcription to file
            transcription_text = result["text"]
            self._save_transcription(audio_path, transcription_text)
            
            return transcription_text
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise
            
    def _save_transcription(self, audio_path, transcription_text):
        """Save transcription to a text file."""
        try:
            # Create filename based on audio filename
            audio_filename = Path(audio_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{audio_filename}_{timestamp}.txt"
            filepath = self.output_dir / filename
            
            # Write transcription to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcription_text)
                
            logger.info(f"Transcription saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving transcription: {str(e)}")
            raise
