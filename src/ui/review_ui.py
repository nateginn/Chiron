"""
Streamlit-based review interface for doctors.
"""
import streamlit as st
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ReviewUI:
    def __init__(self):
        self.title = "Chiron - Medical SOAP Note Assistant"
        
    def run(self):
        """Launch the Streamlit UI."""
        try:
            st.set_page_config(page_title=self.title, layout="wide")
            st.title(self.title)
            
            # Sidebar controls
            with st.sidebar:
                st.header("Controls")
                if st.button("Start Recording"):
                    self._handle_recording_start()
                if st.button("Stop Recording"):
                    self._handle_recording_stop()
                    
            # Main content area
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transcription")
                self._show_transcription()
                
            with col2:
                st.subheader("Generated SOAP Note")
                self._show_soap_note()
                
        except Exception as e:
            logger.error(f"UI error: {str(e)}")
            st.error("An error occurred in the UI")
            
    def _handle_recording_start(self):
        """Handle start recording button click."""
        st.session_state.recording = True
        st.success("Recording started...")
        
    def _handle_recording_stop(self):
        """Handle stop recording button click."""
        st.session_state.recording = False
        st.success("Recording stopped")
        
    def _show_transcription(self):
        """Display the transcribed text."""
        if "transcription" in st.session_state:
            st.text_area("Transcribed Text", 
                        st.session_state.transcription,
                        height=300)
            
    def _show_soap_note(self):
        """Display the generated SOAP note."""
        if "soap_note" in st.session_state:
            st.text_area("SOAP Note",
                        st.session_state.soap_note,
                        height=300)
            if st.button("Save SOAP Note"):
                self._save_soap_note()
