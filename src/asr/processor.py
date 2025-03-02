"""
Process and structure transcribed text.
"""
import re
import json
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TextProcessor:
    def __init__(self):
        # Regular expressions for different sections of medical conversation
        self.patterns = {
            'patient_info': r'(?:patient|name|mr\.|mrs\.|ms\.|age)[^\.\n]*?(?:\d+|\w+)',
            'symptoms': r'(?:complains of|reports|experiencing|symptoms|pain|discomfort|feeling)[^\.\n]*?(?=\.|\n|$)',
            'medications': r'(?:taking|prescribed|medication|drug|dose|mg|mcg|ml)[^\.\n]*?(?=\.|\n|$)',
            'allergies': r'(?:allerg|sensitive)[^\.\n]*?(?=\.|\n|$)',
            'past_medical_history': r'(?:history|previous|prior|past)[^\.\n]*?(?=\.|\n|$)',
            'vitals': r'(?:blood pressure|temperature|pulse|heart rate|respiratory rate|oxygen|spo2|bp)[^\.\n]*?(?=\.|\n|$)',
            'assessment': r'(?:assess|diagnos|impression)[^\.\n]*?(?=\.|\n|$)',
            'plan': r'(?:plan|recommend|prescribe|treatment|therapy|follow up)[^\.\n]*?(?=\.|\n|$)',
        }
        
        # Medical abbreviations and their expansions
        self.abbreviations = {
            'pt': 'patient',
            'hx': 'history',
            'dx': 'diagnosis',
            'tx': 'treatment',
            'rx': 'prescription',
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'rr': 'respiratory rate',
            'temp': 'temperature',
            'o2': 'oxygen',
            'spo2': 'oxygen saturation',
            'lab': 'laboratory',
            'w/': 'with',
            'w/o': 'without',
            'y/o': 'year old',
            'yo': 'year old',
            'pm': 'past medical',
            'pmh': 'past medical history',
            'fh': 'family history',
            'sh': 'social history',
            'cc': 'chief complaint',
            'c/o': 'complains of',
            'sob': 'shortness of breath',
            'cp': 'chest pain',
            'ha': 'headache',
            'n/v': 'nausea and vomiting',
            'abd': 'abdominal',
            'uti': 'urinary tract infection',
            'uri': 'upper respiratory infection',
            'lrti': 'lower respiratory tract infection',
            'uc': 'urgent care',
            'er': 'emergency room',
            'ed': 'emergency department',
        }
        
    def clean_text(self, text):
        """Clean and normalize transcribed text."""
        # Basic cleaning
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Expand medical abbreviations
        for abbr, expansion in self.abbreviations.items():
            # Match whole word abbreviations only (with word boundaries)
            text = re.sub(r'\b' + abbr + r'\b', expansion, text, flags=re.IGNORECASE)
            
        # Normalize punctuation
        text = re.sub(r'\s*([.,;:?!])', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug(f"Cleaned text: {text[:100]}...")
        return text
        
    def extract_sections(self, text):
        """Extract relevant sections from the transcribed text."""
        sections = {}
        
        # Apply each pattern to extract relevant sections
        for key, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            sections[key] = [match.group().strip() for match in matches]
            
        # If we couldn't extract structured sections, try a simpler approach
        if all(len(v) == 0 for v in sections.values()):
            logger.warning("Could not extract structured sections, using sentence-based approach")
            sentences = re.split(r'[.!?]\s+', text)
            
            # Categorize sentences based on keywords
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Simple keyword matching for categorization
                if any(kw in sentence.lower() for kw in ['complain', 'pain', 'discomfort', 'symptom']):
                    sections['symptoms'].append(sentence)
                elif any(kw in sentence.lower() for kw in ['medication', 'taking', 'prescribed', 'drug']):
                    sections['medications'].append(sentence)
                elif any(kw in sentence.lower() for kw in ['allerg', 'sensitive']):
                    sections['allergies'].append(sentence)
                elif any(kw in sentence.lower() for kw in ['history', 'previous', 'prior', 'past']):
                    sections['past_medical_history'].append(sentence)
                elif any(kw in sentence.lower() for kw in ['plan', 'recommend', 'prescribe', 'treatment']):
                    sections['plan'].append(sentence)
                elif any(kw in sentence.lower() for kw in ['assess', 'diagnos', 'impression']):
                    sections['assessment'].append(sentence)
        
        logger.info(f"Extracted {sum(len(v) for v in sections.values())} items across {len(sections)} sections")
        return sections
        
    def format_soap_sections(self, sections):
        """Format extracted sections into SOAP note structure."""
        soap = {
            'subjective': [],
            'objective': [],
            'assessment': [],
            'plan': []
        }
        
        # Map extracted sections to SOAP structure
        if 'patient_info' in sections:
            soap['subjective'].extend(sections['patient_info'])
        
        if 'symptoms' in sections:
            soap['subjective'].extend(sections['symptoms'])
            
        if 'past_medical_history' in sections:
            soap['subjective'].extend(sections['past_medical_history'])
            
        if 'allergies' in sections:
            soap['subjective'].extend(sections['allergies'])
            
        if 'medications' in sections:
            soap['subjective'].extend(sections['medications'])
            
        if 'vitals' in sections:
            soap['objective'].extend(sections['vitals'])
            
        if 'assessment' in sections:
            soap['assessment'].extend(sections['assessment'])
            
        if 'plan' in sections:
            soap['plan'].extend(sections['plan'])
            
        # Format each section
        formatted_soap = {}
        for section, items in soap.items():
            if items:
                formatted_soap[section] = "• " + "\n• ".join(items)
            else:
                formatted_soap[section] = "No information available"
                
        return formatted_soap
        
    def save_processed_text(self, processed_data, output_path=None):
        """Save processed text to a JSON file."""
        if output_path is None:
            output_dir = Path('data/processed')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"processed_{Path(output_path).stem}.json"
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2)
            
        logger.info(f"Saved processed text to {output_path}")
        return output_path
