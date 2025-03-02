"""
NLP pipeline for processing transcribed text into SOAP notes.
"""
import os
from pathlib import Path
import json
from .keyword_extractor import KeywordExtractor
from .template_matcher import TemplateMatcher
from .template_filler import TemplateFiller
from ..utils.logger import get_logger

logger = get_logger(__name__)

class NLPPipeline:
    def __init__(self, config=None):
        self.config = config or {}
        self.keyword_extractor = KeywordExtractor(config)
        self.template_matcher = TemplateMatcher(config)
        self.template_filler = TemplateFiller(config)
        self.output_dir = Path(self.config.get('PIPELINE_OUTPUT_DIR', 'output/pipeline'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process(self, transcription, patient_id=None, visit_date=None):
        """
        Process transcribed text through the NLP pipeline.
        
        Args:
            transcription (str): The transcribed text to process
            patient_id (str, optional): Patient identifier
            visit_date (str, optional): Visit date in YYYYMMDD format
            
        Returns:
            dict: The processed SOAP note
        """
        try:
            logger.info("Starting NLP pipeline processing")
            
            # Step 1: Extract keywords
            logger.info("Extracting keywords from transcription")
            keywords = self.keyword_extractor.extract_keywords(transcription)
            
            # Step 2: Match template
            logger.info("Matching appropriate template")
            template = self.template_matcher.find_matching_template(keywords)
            
            # Step 3: Fill template
            logger.info("Filling template with extracted information")
            soap_note = self.template_filler.fill_template(template, transcription, keywords)
            
            # Step 4: Save SOAP note
            logger.info("Saving SOAP note")
            saved_path = self.template_filler.save_soap_note(soap_note, patient_id, visit_date)
            
            # Step 5: Save pipeline output for debugging/analysis
            self._save_pipeline_output(transcription, keywords, template, soap_note, patient_id, visit_date)
            
            return soap_note
        except Exception as e:
            logger.error(f"Error in NLP pipeline: {str(e)}")
            # Return empty SOAP note in case of error
            return {
                "subjective": "Error processing transcription.",
                "objective": "Error processing transcription.",
                "assessment": "Error processing transcription.",
                "plan": "Error processing transcription."
            }
            
    def _save_pipeline_output(self, transcription, keywords, template, soap_note, patient_id, visit_date):
        """Save the pipeline output for debugging and analysis."""
        try:
            # Generate filename
            if patient_id is None:
                patient_id = "unknown_patient"
                
            if visit_date is None:
                from datetime import datetime
                visit_date = datetime.now().strftime("%Y%m%d")
                
            filename = f"{patient_id}_{visit_date}_pipeline.json"
            filepath = self.output_dir / filename
            
            # Prepare output
            output = {
                "transcription": transcription,
                "keywords": keywords,
                "template": {
                    "id": template.get("id", "unknown"),
                    "name": template.get("name", "Unknown Template")
                },
                "soap_note": soap_note
            }
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)
                
            logger.info(f"Saved pipeline output to {filepath}")
        except Exception as e:
            logger.error(f"Error saving pipeline output: {str(e)}")
            
    def batch_process(self, transcriptions_dir, output_dir=None):
        """
        Process multiple transcription files in a directory.
        
        Args:
            transcriptions_dir (str): Directory containing transcription files
            output_dir (str, optional): Directory to save SOAP notes
            
        Returns:
            list: Paths to generated SOAP notes
        """
        try:
            transcriptions_path = Path(transcriptions_dir)
            if not transcriptions_path.exists() or not transcriptions_path.is_dir():
                logger.error(f"Transcriptions directory not found: {transcriptions_dir}")
                return []
                
            # Override output directory if specified
            if output_dir:
                self.template_filler.output_dir = Path(output_dir)
                self.template_filler.output_dir.mkdir(parents=True, exist_ok=True)
                
            # Get all text files in the directory
            transcription_files = list(transcriptions_path.glob("*.txt"))
            logger.info(f"Found {len(transcription_files)} transcription files to process")
            
            soap_note_paths = []
            
            # Process each file
            for file_path in transcription_files:
                try:
                    # Extract patient ID and date from filename
                    filename = file_path.stem
                    parts = filename.split('_')
                    
                    patient_id = None
                    visit_date = None
                    
                    if len(parts) >= 2:
                        patient_id = parts[0]
                        visit_date = parts[1]
                    
                    # Read transcription
                    with open(file_path, 'r', encoding='utf-8') as f:
                        transcription = f.read()
                        
                    # Process transcription
                    logger.info(f"Processing file: {file_path}")
                    soap_note = self.process(transcription, patient_id, visit_date)
                    
                    # Save SOAP note
                    saved_path = self.template_filler.save_soap_note(soap_note, patient_id, visit_date)
                    if saved_path:
                        soap_note_paths.append(saved_path)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
            logger.info(f"Batch processing complete. Generated {len(soap_note_paths)} SOAP notes.")
            return soap_note_paths
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return []
