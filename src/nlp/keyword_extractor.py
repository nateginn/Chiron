"""
Medical keyword extraction from transcribed text.
"""
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch
import re
from pathlib import Path
import json
from ..utils.logger import get_logger

logger = get_logger(__name__)

class KeywordExtractor:
    def __init__(self, config=None):
        self.config = config or {}
        self.ner_pipeline = None
        self.medical_terms_path = self.config.get('MEDICAL_TERMS_PATH', 'data/medical_terms.json')
        self.medical_terms = self._load_medical_terms()
        self.initialize_pipeline()
        
    def initialize_pipeline(self):
        """Initialize the NER pipeline for medical term extraction."""
        try:
            # Try to load the model from Hugging Face
            model_name = "samrawal/bert-base-uncased-medical-ner"
            
            logger.info(f"Loading NER model: {model_name}")
            
            # Check if CUDA is available
            device = 0 if torch.cuda.is_available() else -1
            logger.info(f"Using device: {'CUDA' if device == 0 else 'CPU'}")
            
            self.ner_pipeline = pipeline(
                "ner", 
                model=model_name,
                tokenizer=model_name,
                aggregation_strategy="simple",
                device=device
            )
            
            logger.info("NER pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NER pipeline: {str(e)}")
            logger.warning("Falling back to rule-based extraction")
            self.ner_pipeline = None
            
    def _load_medical_terms(self):
        """Load medical terms dictionary for rule-based extraction."""
        try:
            medical_terms_file = Path(self.medical_terms_path)
            
            # If the file doesn't exist, create a basic version
            if not medical_terms_file.exists():
                logger.warning(f"Medical terms file not found at {self.medical_terms_path}")
                return self._create_basic_medical_terms()
                
            with open(medical_terms_file, 'r', encoding='utf-8') as f:
                medical_terms = json.load(f)
                
            logger.info(f"Loaded {sum(len(terms) for terms in medical_terms.values())} medical terms")
            return medical_terms
        except Exception as e:
            logger.error(f"Error loading medical terms: {str(e)}")
            return self._create_basic_medical_terms()
            
    def _create_basic_medical_terms(self):
        """Create a basic medical terms dictionary."""
        medical_terms = {
            "PROBLEM": [
                "headache", "migraine", "pain", "fever", "cough", "nausea", "vomiting",
                "diarrhea", "constipation", "fatigue", "dizziness", "shortness of breath",
                "chest pain", "back pain", "abdominal pain", "joint pain", "rash", "swelling",
                "inflammation", "infection", "hypertension", "diabetes", "asthma", "COPD",
                "arthritis", "depression", "anxiety", "insomnia"
            ],
            "TREATMENT": [
                "surgery", "medication", "therapy", "physical therapy", "counseling",
                "antibiotics", "painkillers", "anti-inflammatory", "injection", "implant",
                "pacemaker", "transplant", "dialysis", "chemotherapy", "radiation therapy",
                "immunotherapy", "rehabilitation", "exercise", "diet", "rest", "hydration"
            ],
            "TEST": [
                "blood test", "urine test", "X-ray", "MRI", "CT scan", "ultrasound",
                "EKG", "ECG", "EEG", "biopsy", "colonoscopy", "endoscopy", "mammogram",
                "PET scan", "stress test", "glucose test", "cholesterol test", "culture"
            ],
            "ANATOMY": [
                "head", "neck", "chest", "abdomen", "back", "arm", "leg", "knee", "ankle",
                "shoulder", "elbow", "wrist", "hand", "foot", "spine", "heart", "lung",
                "liver", "kidney", "stomach", "intestine", "colon", "brain", "muscle",
                "bone", "joint", "tendon", "ligament", "artery", "vein", "nerve"
            ]
        }
        
        # Save the basic terms for future use
        try:
            medical_terms_file = Path(self.medical_terms_path)
            medical_terms_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(medical_terms_file, 'w', encoding='utf-8') as f:
                json.dump(medical_terms, f, indent=2)
                
            logger.info(f"Created basic medical terms file at {self.medical_terms_path}")
        except Exception as e:
            logger.error(f"Error saving basic medical terms: {str(e)}")
            
        return medical_terms
            
    def extract_keywords(self, text):
        """Extract medical keywords from text."""
        try:
            # Try using the NER pipeline if available
            if self.ner_pipeline:
                logger.info("Extracting keywords using NER pipeline")
                return self._extract_with_ner(text)
            else:
                logger.info("Extracting keywords using rule-based approach")
                return self._extract_with_rules(text)
        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            # Fall back to rule-based extraction if NER fails
            return self._extract_with_rules(text)
            
    def _extract_with_ner(self, text):
        """Extract keywords using the NER pipeline."""
        entities = self.ner_pipeline(text)
        
        # Filter and format results
        keywords = [
            {
                "text": entity["word"],
                "label": entity["entity_group"],
                "score": entity["score"]
            }
            for entity in entities
            if entity["score"] > 0.7  # Only include high-confidence predictions
        ]
        
        logger.info(f"Extracted {len(keywords)} keywords with NER")
        return keywords
        
    def _extract_with_rules(self, text):
        """Extract keywords using rule-based approach."""
        keywords = []
        
        # Normalize text for matching
        text_lower = text.lower()
        
        # Match medical terms from our dictionary
        for category, terms in self.medical_terms.items():
            for term in terms:
                # Use word boundary to match whole words
                pattern = r'\b' + re.escape(term.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    # Get the actual text from the original case
                    original_text = text[match.start():match.end()]
                    
                    keywords.append({
                        "text": original_text,
                        "label": category,
                        "score": 1.0  # Rule-based matches get a score of 1.0
                    })
        
        logger.info(f"Extracted {len(keywords)} keywords with rule-based approach")
        return keywords
