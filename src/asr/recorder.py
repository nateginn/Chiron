"""
Audio recording module with voice activation detection.
"""
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path
from datetime import datetime
import threading
import queue
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AudioRecorder:
    def __init__(self, config):
        self.sample_rate = config.get('SAMPLE_RATE', 16000)
        self.channels = config.get('CHANNELS', 1)
        self.chunk_size = config.get('CHUNK_SIZE', 1024)
        self.vad_threshold = config.get('VAD_THRESHOLD', 0.01)  # Voice activation threshold
        self.silence_limit = config.get('SILENCE_LIMIT', 2)  # Seconds of silence before stopping
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.silence_counter = 0
        self.output_dir = Path(config.get('AUDIO_OUTPUT_DIR', 'data/raw_audio'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Calculate audio energy for voice activation
        energy = np.mean(np.abs(indata))
        
        # Voice activation detection
        if energy > self.vad_threshold:
            self.silence_counter = 0
            logger.debug(f"Voice detected: energy={energy:.4f}")
        else:
            self.silence_counter += frames / self.sample_rate
            logger.debug(f"Silence detected: counter={self.silence_counter:.2f}s")
            
            # Stop recording after silence_limit seconds of silence
            if self.silence_counter > self.silence_limit and self.recording:
                self.stop_recording()
                return
        
        # Add audio data to queue
        if self.recording:
            self.audio_queue.put(indata.copy())
            self.audio_data.append(indata.copy())
        
    def start_recording(self):
        """Start recording audio with voice activation."""
        if self.recording:
            logger.warning("Recording already in progress")
            return
            
        logger.info("Starting audio recording...")
        self.recording = True
        self.audio_data = []
        self.silence_counter = 0
        
        # Start audio stream
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                blocksize=self.chunk_size
            )
            self.stream.start()
            logger.info("Audio stream started successfully")
        except Exception as e:
            self.recording = False
            logger.error(f"Error starting audio stream: {str(e)}")
            raise
        
    def stop_recording(self):
        """Stop recording and save the audio file."""
        if not self.recording:
            logger.warning("No recording in progress")
            return None
            
        self.recording = False
        logger.info("Recording stopped")
        
        try:
            # Stop the audio stream
            if hasattr(self, 'stream') and self.stream.active:
                self.stream.stop()
                self.stream.close()
                logger.info("Audio stream closed")
                
            # Process and save the recorded audio
            if self.audio_data:
                audio_path = self._save_audio_data()
                logger.info(f"Audio saved to: {audio_path}")
                return audio_path
            else:
                logger.warning("No audio data captured")
                return None
                
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            raise
            
    def _save_audio_data(self):
        """Save recorded audio data to a WAV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = self.output_dir / filename
        
        # Combine all audio chunks
        audio_data = np.concatenate(self.audio_data, axis=0)
        
        # Save as WAV file
        wav.write(filepath, self.sample_rate, audio_data)
        
        return filepath
