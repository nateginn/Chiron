"""
Streamlit UI for Chiron medical scribe application.
"""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.asr.recorder import AudioRecorder
from src.asr.transcriber import WhisperTranscriber
from src.nlp.pipeline import NLPPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Chiron - Medical SOAP Note Generator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'soap_note' not in st.session_state:
    st.session_state.soap_note = None
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = None
if 'visit_date' not in st.session_state:
    st.session_state.visit_date = datetime.now().strftime("%Y%m%d")

def start_recording():
    """Start audio recording."""
    st.session_state.recording = True
    
    # Create recorder
    recorder = AudioRecorder()
    
    # Display recording status
    status_placeholder = st.empty()
    status_placeholder.warning("Recording in progress... Speak clearly and wait for silence detection.")
    
    # Start recording
    try:
        audio_path = recorder.start_recording()
        st.session_state.audio_path = audio_path
        status_placeholder.success(f"Recording completed and saved to {audio_path}")
    except Exception as e:
        status_placeholder.error(f"Error during recording: {str(e)}")
    finally:
        st.session_state.recording = False

def process_audio():
    """Transcribe audio and generate SOAP note."""
    if not st.session_state.audio_path:
        st.error("No audio recording found. Please record audio first.")
        return
    
    # Transcribe audio
    transcriber = WhisperTranscriber()
    
    with st.spinner("Transcribing audio..."):
        try:
            transcription = transcriber.transcribe(st.session_state.audio_path)
            st.session_state.transcription = transcription
            st.success("Transcription completed!")
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")
            return
    
    # Process transcription
    pipeline = NLPPipeline()
    
    with st.spinner("Generating SOAP note..."):
        try:
            soap_note = pipeline.process(
                transcription, 
                patient_id=st.session_state.patient_id,
                visit_date=st.session_state.visit_date
            )
            st.session_state.soap_note = soap_note
            st.success("SOAP note generated successfully!")
        except Exception as e:
            st.error(f"Error generating SOAP note: {str(e)}")

def clear_session():
    """Clear session data."""
    st.session_state.audio_path = None
    st.session_state.transcription = None
    st.session_state.soap_note = None
    st.success("Session data cleared!")

def main():
    """Main Streamlit application."""
    st.title("Chiron - Medical SOAP Note Generator")
    st.markdown("---")
    
    # Sidebar for patient information
    with st.sidebar:
        st.header("Patient Information")
        st.session_state.patient_id = st.text_input("Patient ID", value=st.session_state.patient_id or "")
        st.session_state.visit_date = st.date_input(
            "Visit Date", 
            value=datetime.strptime(st.session_state.visit_date, "%Y%m%d") if st.session_state.visit_date else datetime.now()
        ).strftime("%Y%m%d")
        
        st.markdown("---")
        st.header("Actions")
        
        # Recording controls
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.recording:
                st.button("Start Recording", on_click=start_recording, use_container_width=True)
            else:
                st.button("Recording...", disabled=True, use_container_width=True)
        
        with col2:
            st.button("Clear Session", on_click=clear_session, use_container_width=True)
        
        # Process button
        if st.session_state.audio_path:
            st.button("Process Recording", on_click=process_audio, use_container_width=True)
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Recording", "Transcription", "SOAP Note"])
    
    # Tab 1: Recording
    with tab1:
        st.header("Audio Recording")
        
        if st.session_state.audio_path:
            st.success(f"Recording saved to: {st.session_state.audio_path}")
            
            # Display audio player if file exists
            if os.path.exists(st.session_state.audio_path):
                st.audio(st.session_state.audio_path)
            else:
                st.warning("Audio file not found. It may have been moved or deleted.")
        else:
            st.info("No recording available. Click 'Start Recording' to begin.")
    
    # Tab 2: Transcription
    with tab2:
        st.header("Transcription")
        
        if st.session_state.transcription:
            st.text_area(
                "Transcribed Text", 
                value=st.session_state.transcription, 
                height=400
            )
        else:
            st.info("No transcription available. Process a recording to see the transcription.")
    
    # Tab 3: SOAP Note
    with tab3:
        st.header("SOAP Note")
        
        if st.session_state.soap_note:
            # Create editable text areas for each section
            soap_sections = st.session_state.soap_note
            
            for section, content in soap_sections.items():
                st.subheader(section.upper())
                soap_sections[section] = st.text_area(
                    f"{section}_content", 
                    value=content, 
                    label_visibility="collapsed",
                    height=150
                )
            
            # Save button
            if st.button("Save SOAP Note"):
                try:
                    # Create pipeline to save
                    pipeline = NLPPipeline()
                    saved_path = pipeline.template_filler.save_soap_note(
                        soap_sections, 
                        patient_id=st.session_state.patient_id,
                        visit_date=st.session_state.visit_date
                    )
                    st.success(f"SOAP note saved to: {saved_path}")
                except Exception as e:
                    st.error(f"Error saving SOAP note: {str(e)}")
        else:
            st.info("No SOAP note available. Process a recording to generate a SOAP note.")

if __name__ == "__main__":
    main()
