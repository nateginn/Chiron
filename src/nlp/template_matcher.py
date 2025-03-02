"""
Match appropriate SOAP templates based on extracted information.
"""
import faiss
import numpy as np
import torch
import json
import os
from pathlib import Path
from transformers import AutoModel, AutoTokenizer
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TemplateMatcher:
    def __init__(self, config=None):
        self.config = config or {}
        self.model = None
        self.tokenizer = None
        self.index = None
        self.templates = []
        self.templates_dir = Path(self.config.get('TEMPLATES_DIR', 'data/templates'))
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path = Path(self.config.get('VECTOR_DB_PATH', 'models/vector_db'))
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = 768  # Default for most BERT models
        self.initialize_model()
        self.load_templates()
        self.build_or_load_index()
        
    def initialize_model(self):
        """Initialize the embedding model."""
        try:
            # Use a medical/clinical BERT model for better domain-specific embeddings
            model_name = "pritamdeka/S-PubMedBert-MS-MARCO"
            logger.info(f"Loading embedding model: {model_name}")
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(device)
            
            logger.info("Template matching model initialized")
        except Exception as e:
            logger.error(f"Error initializing template matcher: {str(e)}")
            raise
            
    def load_templates(self):
        """Load SOAP templates from the templates directory."""
        try:
            template_files = list(self.templates_dir.glob("*.json"))
            
            if not template_files:
                logger.warning("No template files found. Creating sample templates.")
                self._create_sample_templates()
                template_files = list(self.templates_dir.glob("*.json"))
                
            self.templates = []
            for template_file in template_files:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    self.templates.append(template)
                    
            logger.info(f"Loaded {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            self._create_sample_templates()
            
    def _create_sample_templates(self):
        """Create sample SOAP templates for testing."""
        sample_templates = [
            {
                "id": "knee_exam",
                "name": "Knee Examination",
                "keywords": ["knee", "joint", "pain", "swelling", "mobility", "arthritis", "meniscus", "ACL", "MCL", "patella"],
                "template": {
                    "subjective": "Patient presents with knee pain. [SYMPTOMS]. Patient reports [HISTORY].",
                    "objective": "Examination of the knee reveals [FINDINGS]. Range of motion is [ROM]. [TESTS].",
                    "assessment": "Assessment: [DIAGNOSIS].",
                    "plan": "Plan: [TREATMENT]. Follow up in [TIMEFRAME]."
                }
            },
            {
                "id": "headache",
                "name": "Headache Evaluation",
                "keywords": ["headache", "migraine", "pain", "aura", "nausea", "vomiting", "photophobia", "neurological"],
                "template": {
                    "subjective": "Patient presents with headache. [SYMPTOMS]. Patient reports [HISTORY].",
                    "objective": "Vital signs: [VITALS]. Neurological examination: [NEURO_EXAM].",
                    "assessment": "Assessment: [DIAGNOSIS].",
                    "plan": "Plan: [TREATMENT]. [MEDICATIONS]. Follow up as needed."
                }
            },
            {
                "id": "respiratory",
                "name": "Respiratory Examination",
                "keywords": ["cough", "shortness of breath", "SOB", "wheezing", "chest pain", "sputum", "pneumonia", "bronchitis", "asthma", "COPD"],
                "template": {
                    "subjective": "Patient presents with respiratory symptoms including [SYMPTOMS]. History of [HISTORY].",
                    "objective": "Vital signs: [VITALS]. Lung examination: [LUNG_EXAM]. Oxygen saturation: [O2_SAT]%.",
                    "assessment": "Assessment: [DIAGNOSIS].",
                    "plan": "Plan: [TREATMENT]. [MEDICATIONS]. Follow up in [TIMEFRAME]."
                }
            }
        ]
        
        # Save sample templates
        for template in sample_templates:
            template_path = self.templates_dir / f"{template['id']}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
                
        logger.info(f"Created {len(sample_templates)} sample templates")
            
    def build_or_load_index(self):
        """Build or load the FAISS index for template matching."""
        index_path = self.vector_db_path / "templates.index"
        
        try:
            if index_path.exists():
                # Load existing index
                logger.info(f"Loading existing FAISS index from {index_path}")
                self.index = faiss.read_index(str(index_path))
            else:
                # Build new index
                logger.info("Building new FAISS index")
                self._build_index()
                
                # Save index for future use
                logger.info(f"Saving FAISS index to {index_path}")
                faiss.write_index(self.index, str(index_path))
        except Exception as e:
            logger.error(f"Error with FAISS index: {str(e)}")
            # Create a new index if loading fails
            self._build_index()
            
    def _build_index(self):
        """Build a FAISS index from templates."""
        # Initialize index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        if not self.templates:
            logger.warning("No templates available to build index")
            return
            
        # Get embeddings for all templates
        embeddings = []
        for template in self.templates:
            # Concatenate keywords for embedding
            keywords_text = " ".join(template.get("keywords", []))
            if not keywords_text:
                keywords_text = template.get("name", "")
                
            embedding = self._get_embedding(keywords_text)
            embeddings.append(embedding)
            
        # Add embeddings to index
        if embeddings:
            embeddings_array = np.vstack(embeddings)
            self.index.add(embeddings_array)
            logger.info(f"Added {len(embeddings)} template embeddings to index")
            
    def find_matching_template(self, keywords):
        """Find the best matching SOAP template based on keywords."""
        try:
            if not self.index or self.index.ntotal == 0:
                logger.warning("No templates in index, returning default template")
                return self._get_default_template()
                
            # Convert keywords to text
            if isinstance(keywords, list):
                if all(isinstance(k, dict) for k in keywords):
                    # Extract text from keyword objects
                    keywords_text = " ".join([k.get("text", "") for k in keywords])
                else:
                    # Join string keywords
                    keywords_text = " ".join(keywords)
            else:
                # Use as is if already a string
                keywords_text = keywords
                
            # Get embedding and search
            embedding = self._get_embedding(keywords_text)
            D, I = self.index.search(embedding.reshape(1, -1), 1)
            
            # Check if we got a valid result
            if len(I) > 0 and len(I[0]) > 0 and I[0][0] < len(self.templates):
                template = self.templates[I[0][0]]
                logger.info(f"Found matching template: {template.get('name', 'Unknown')}")
                return template
            else:
                logger.warning("No matching template found, returning default")
                return self._get_default_template()
        except Exception as e:
            logger.error(f"Template matching error: {str(e)}")
            return self._get_default_template()
            
    def _get_embedding(self, text):
        """Get embedding for input text."""
        try:
            # Ensure model and tokenizer are loaded
            if self.model is None or self.tokenizer is None:
                self.initialize_model()
                
            # Tokenize and get embedding
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True,
                padding="max_length"
            ).to(self.model.device)
            
            # Get embeddings without gradient calculation
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # Use mean of last hidden state as embedding
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Return zero embedding as fallback
            return np.zeros((1, self.embedding_dim))
            
    def _get_default_template(self):
        """Return a default template when no match is found."""
        default_template = {
            "id": "default",
            "name": "General Medical Examination",
            "template": {
                "subjective": "Patient presents with [SYMPTOMS]. Patient reports [HISTORY].",
                "objective": "Vital signs: [VITALS]. Physical examination: [EXAM].",
                "assessment": "Assessment: [DIAGNOSIS].",
                "plan": "Plan: [TREATMENT]. Follow up as needed."
            }
        }
        return default_template
