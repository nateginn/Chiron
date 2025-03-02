"""
Tests for the ASR pipeline components.
"""
import pytest
from src.asr.recorder import AudioRecorder
from src.asr.transcriber import WhisperTranscriber
from src.asr.processor import TextProcessor

def test_audio_recorder_initialization():
    config = {'SAMPLE_RATE': 16000, 'CHANNELS': 1, 'CHUNK_SIZE': 1024}
    recorder = AudioRecorder(config)
    assert recorder.sample_rate == 16000
    assert recorder.channels == 1
    assert recorder.chunk_size == 1024
    assert not recorder.recording

def test_text_processor():
    processor = TextProcessor()
    test_text = "Patient John Doe complains of headache and fever."
    cleaned_text = processor.clean_text(test_text)
    assert isinstance(cleaned_text, str)
    assert len(cleaned_text) > 0
    
    sections = processor.extract_sections(cleaned_text)
    assert isinstance(sections, dict)
    assert 'symptoms' in sections
