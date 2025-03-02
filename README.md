# Chiron - Medical SOAP Note Generation Assistant

Chiron is an AI-powered medical scribe that automatically generates SOAP notes from doctor-patient conversations. It uses state-of-the-art speech recognition and natural language processing to streamline medical documentation.

## Features

- Real-time voice activation and audio recording
- Automatic speech recognition using Whisper
- Medical keyword extraction and template matching
- SOAP note generation using local LLM (Llama)
- HIPAA-compliant data handling
- User-friendly review interface

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv chiron_env
   
   # Activate the virtual environment
   # On Windows (PowerShell):
   .\chiron_env\Scripts\Activate.ps1
   # On Windows (Command Prompt):
   .\chiron_env\Scripts\activate.bat
   # On macOS/Linux:
   source chiron_env/bin/activate
   ```
   
   > **IMPORTANT**: Always ensure the virtual environment is activated before installing dependencies or running any code. The terminal prompt should show `(chiron_env)` when the environment is active.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
4. Set up environment variables in `.env`
5. Run the application:
   ```bash
   python run.py
   ```

## Project Structure

```
Chiron/
│─── data/                     # Stores audio recordings, logs, and test data
│    ├── templates/            # SOAP note templates for different specialties
│    ├── medical_terms/        # Medical terminology dictionaries
│    └── audio/                # Recorded audio files
│─── models/                   # Pretrained & fine-tuned models
│    └── vector_db/            # FAISS vector database for template matching
│─── src/                      # Source code
│    ├── asr/                  # Speech-to-text pipeline
│    │    ├── recorder.py      # Audio recording with voice activation
│    │    ├── transcriber.py   # Whisper-based transcription
│    │    └── processor.py     # Text cleaning and preprocessing
│    ├── nlp/                  # Natural language processing
│    │    ├── keyword_extractor.py  # Medical term extraction
│    │    ├── template_matcher.py   # Finding relevant SOAP templates
│    │    ├── template_filler.py    # Generating SOAP notes from templates
│    │    └── pipeline.py           # End-to-end NLP pipeline
│    ├── ui/                   # User interface components
│    ├── storage/              # Data handling
│    └── utils/                # Helper functions
│─── tests/                    # Unit and integration tests
```

## NLP Pipeline

Chiron uses a sophisticated NLP pipeline to process transcribed doctor-patient conversations:

1. **Keyword Extraction**: Identifies medical terms, symptoms, diagnoses, and treatments using a combination of:
   - Medical Named Entity Recognition (NER) using specialized BERT models
   - Rule-based extraction with comprehensive medical dictionaries
   - Fallback mechanisms to ensure robustness

2. **Template Matching**: Finds the most appropriate SOAP note template based on the conversation content:
   - Uses FAISS vector database for efficient semantic search
   - Embeddings generated from medical-specific language models
   - Sample templates included for common medical specialties

3. **Template Filling**: Generates complete SOAP notes by filling templates with extracted information:
   - Rule-based approach for structured data
   - Optional OpenAI integration for enhanced natural language generation
   - Comprehensive section extraction for Subjective, Objective, Assessment, and Plan

4. **Post-Processing**: Ensures the generated SOAP notes are properly formatted and medically accurate.

## Usage

### Basic Usage

```python
from src.asr.recorder import AudioRecorder
from src.asr.transcriber import WhisperTranscriber
from src.nlp.pipeline import NLPPipeline

# Record audio
recorder = AudioRecorder()
audio_path = recorder.start_recording()  # Returns path to saved audio file

# Transcribe audio
transcriber = WhisperTranscriber()
transcription = transcriber.transcribe(audio_path)

# Process transcription
pipeline = NLPPipeline()
soap_note = pipeline.process(transcription, patient_id="P12345", visit_date="20230801")

# Print SOAP note
for section, content in soap_note.items():
    print(f"\n{section.upper()}:")
    print(content)
```

### Testing

Run the NLP pipeline test script to see the components in action:

```bash
python tests/test_nlp_pipeline.py
```

## License

[MIT License](LICENSE)
