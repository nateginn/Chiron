#!/usr/bin/env python3
"""
Main entry point for the Chiron medical scribe application.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from src.asr.recorder import AudioRecorder
from src.asr.transcriber import WhisperTranscriber
from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.template_matcher import TemplateMatcher
from src.nlp.llm_generator import LLMGenerator
from src.ui.review_ui import ReviewUI
from src.utils.logger import setup_logger
from src.utils.config import load_config

def run_ui():
    """Run the Streamlit UI."""
    import streamlit.web.cli as stcli
    from src.ui.app import main
    
    # Use Streamlit CLI to run the app
    sys.argv = ["streamlit", "run", str(Path(__file__).parent / "src" / "ui" / "app.py")]
    sys.exit(stcli.main())

def run_cli():
    """Run in CLI mode for testing."""
    from src.asr.recorder import AudioRecorder
    from src.asr.transcriber import WhisperTranscriber
    from src.nlp.pipeline import NLPPipeline
    
    print("Running Chiron in CLI mode...")
    
    # Record audio
    recorder = AudioRecorder()
    print("Starting audio recording. Speak clearly and wait for silence detection.")
    audio_path = recorder.start_recording()
    print(f"Recording saved to: {audio_path}")
    
    # Transcribe audio
    transcriber = WhisperTranscriber()
    print("Transcribing audio...")
    transcription = transcriber.transcribe(audio_path)
    print("\nTranscription:")
    print(transcription)
    
    # Process transcription
    pipeline = NLPPipeline()
    print("\nGenerating SOAP note...")
    soap_note = pipeline.process(transcription)
    
    # Display SOAP note
    print("\nSOAP Note:")
    for section, content in soap_note.items():
        print(f"\n{section.upper()}:")
        print(content)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Chiron Medical Scribe Application")
    parser.add_argument(
        "--mode", 
        choices=["ui", "cli"], 
        default="ui",
        help="Run mode: ui (Streamlit interface) or cli (command line)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "ui":
        run_ui()
    else:
        run_cli()

if __name__ == "__main__":
    main()
