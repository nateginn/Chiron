"""
Fill SOAP templates with extracted information.
"""
import re
import json
from pathlib import Path
import openai
import os
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TemplateFiller:
    def __init__(self, config=None):
        self.config = config or {}
        self.openai_api_key = self.config.get('OPENAI_API_KEY')
        self.use_openai = self.openai_api_key is not None
        self.output_dir = Path(self.config.get('SOAP_OUTPUT_DIR', 'output/soap_notes'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def fill_template(self, template, transcription, keywords):
        """Fill the template with information from transcription and keywords."""
        try:
            logger.info(f"Filling template: {template.get('name', 'Unknown')}")
            
            # Extract template sections
            template_sections = template.get('template', {})
            
            if self.use_openai:
                # Use OpenAI to intelligently fill the template
                filled_template = self._fill_with_openai(template_sections, transcription, keywords)
            else:
                # Use rule-based approach
                filled_template = self._fill_with_rules(template_sections, transcription, keywords)
                
            return filled_template
        except Exception as e:
            logger.error(f"Error filling template: {str(e)}")
            return self._create_empty_soap_note()
            
    def _fill_with_openai(self, template_sections, transcription, keywords):
        """Use OpenAI to intelligently fill the template."""
        try:
            # Set up OpenAI API
            openai.api_key = self.openai_api_key
            
            # Prepare prompt
            prompt = self._create_openai_prompt(template_sections, transcription, keywords)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that creates SOAP notes from doctor-patient conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and parse the response
            soap_text = response.choices[0].message.content.strip()
            
            # Parse the response into sections
            filled_template = self._parse_openai_response(soap_text, template_sections)
            
            logger.info("Successfully filled template with OpenAI")
            return filled_template
        except Exception as e:
            logger.error(f"Error using OpenAI to fill template: {str(e)}")
            # Fall back to rule-based approach
            return self._fill_with_rules(template_sections, transcription, keywords)
            
    def _create_openai_prompt(self, template_sections, transcription, keywords):
        """Create a prompt for OpenAI to fill the template."""
        # Extract keywords text
        keywords_text = ""
        if keywords:
            if isinstance(keywords, list):
                if all(isinstance(k, dict) for k in keywords):
                    keywords_text = ", ".join([f"{k.get('text', '')} ({k.get('label', '')})" for k in keywords])
                else:
                    keywords_text = ", ".join(keywords)
            else:
                keywords_text = str(keywords)
                
        prompt = f"""
I need you to create a SOAP note based on the following doctor-patient conversation.

CONVERSATION TRANSCRIPT:
{transcription}

EXTRACTED MEDICAL KEYWORDS:
{keywords_text}

Please create a SOAP note with the following sections:
"""

        # Add template sections to prompt
        for section_name, section_template in template_sections.items():
            prompt += f"\n{section_name.upper()}: {section_template}"
            
        prompt += """

Replace all placeholders like [SYMPTOMS], [HISTORY], etc. with appropriate information from the conversation.
Format your response as a complete SOAP note with clear section headers.
"""

        return prompt
        
    def _parse_openai_response(self, soap_text, template_sections):
        """Parse the OpenAI response into a structured SOAP note."""
        filled_template = {}
        
        # Initialize with empty sections
        for section_name in template_sections.keys():
            filled_template[section_name] = ""
            
        # Try to extract sections using regex
        for section_name in template_sections.keys():
            pattern = rf"{section_name.upper()}:?\s*(.*?)(?=\n\n|\n[A-Z]+:|\Z)"
            match = re.search(pattern, soap_text, re.DOTALL | re.IGNORECASE)
            if match:
                filled_template[section_name] = match.group(1).strip()
                
        # If any section is empty, try alternative section names
        alternative_names = {
            "subjective": ["SUBJECTIVE", "S:", "HISTORY", "HPI"],
            "objective": ["OBJECTIVE", "O:", "PHYSICAL EXAM", "EXAMINATION"],
            "assessment": ["ASSESSMENT", "A:", "IMPRESSION", "DIAGNOSIS"],
            "plan": ["PLAN", "P:", "TREATMENT", "RECOMMENDATIONS"]
        }
        
        for section_name, alternatives in alternative_names.items():
            if section_name in filled_template and not filled_template[section_name]:
                for alt in alternatives:
                    pattern = rf"{alt}:?\s*(.*?)(?=\n\n|\n[A-Z]+:|\Z)"
                    match = re.search(pattern, soap_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        filled_template[section_name] = match.group(1).strip()
                        break
                        
        return filled_template
        
    def _fill_with_rules(self, template_sections, transcription, keywords):
        """Use rule-based approach to fill the template."""
        filled_template = {}
        
        # Extract keywords by category
        categorized_keywords = self._categorize_keywords(keywords)
        
        # Process each template section
        for section_name, section_template in template_sections.items():
            filled_section = section_template
            
            # Replace placeholders with extracted information
            filled_section = self._replace_placeholders(filled_section, transcription, categorized_keywords)
            
            filled_template[section_name] = filled_section
            
        return filled_template
        
    def _categorize_keywords(self, keywords):
        """Categorize keywords by their label."""
        categories = {
            "PROBLEM": [],
            "TREATMENT": [],
            "TEST": [],
            "ANATOMY": [],
            "OTHER": []
        }
        
        if not keywords:
            return categories
            
        # Process keywords
        if isinstance(keywords, list):
            for keyword in keywords:
                if isinstance(keyword, dict):
                    text = keyword.get("text", "")
                    label = keyword.get("label", "OTHER")
                    
                    if label in categories:
                        categories[label].append(text)
                    else:
                        categories["OTHER"].append(text)
                else:
                    # If it's just a string, add to OTHER
                    categories["OTHER"].append(keyword)
        
        return categories
        
    def _replace_placeholders(self, template, transcription, categorized_keywords):
        """Replace placeholders in the template with actual content."""
        # Common placeholders and their replacements
        replacements = {
            "[SYMPTOMS]": self._get_symptoms_text(categorized_keywords, transcription),
            "[HISTORY]": self._extract_history(transcription),
            "[FINDINGS]": self._get_findings_text(categorized_keywords, transcription),
            "[DIAGNOSIS]": self._get_diagnosis_text(categorized_keywords, transcription),
            "[TREATMENT]": self._get_treatment_text(categorized_keywords, transcription),
            "[VITALS]": self._extract_vitals(transcription),
            "[EXAM]": self._extract_exam_findings(transcription),
            "[MEDICATIONS]": self._extract_medications(transcription),
            "[TIMEFRAME]": "2 weeks",  # Default follow-up time
            "[ROM]": "within normal limits",  # Default range of motion
            "[TESTS]": self._get_tests_text(categorized_keywords),
            "[NEURO_EXAM]": "Neurological examination is unremarkable",  # Default neuro exam
            "[LUNG_EXAM]": "Clear to auscultation bilaterally",  # Default lung exam
            "[O2_SAT]": "98"  # Default oxygen saturation
        }
        
        # Replace each placeholder
        result = template
        for placeholder, replacement in replacements.items():
            result = result.replace(placeholder, replacement)
            
        return result
        
    def _get_symptoms_text(self, categorized_keywords, transcription):
        """Get text describing symptoms."""
        problems = categorized_keywords.get("PROBLEM", [])
        
        if not problems:
            # Try to extract symptoms from transcription
            symptoms_pattern = r"(?:complain(?:s|ing|ed) of|(?:has|having|had) (?:a|an)|suffering from|experiencing) ([^.]*)"
            match = re.search(symptoms_pattern, transcription, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return "unspecified symptoms"
            
        if len(problems) == 1:
            return problems[0]
        elif len(problems) == 2:
            return f"{problems[0]} and {problems[1]}"
        else:
            return f"{', '.join(problems[:-1])}, and {problems[-1]}"
            
    def _get_findings_text(self, categorized_keywords, transcription):
        """Get text describing physical findings."""
        anatomy = categorized_keywords.get("ANATOMY", [])
        problems = categorized_keywords.get("PROBLEM", [])
        
        if not anatomy and not problems:
            return "no significant findings"
            
        findings = []
        
        # Try to match anatomy with problems
        for part in anatomy:
            matched = False
            for problem in problems:
                if re.search(r"\b" + re.escape(problem) + r"\b", transcription, re.IGNORECASE):
                    findings.append(f"{part} shows {problem}")
                    matched = True
            if not matched and part:
                findings.append(f"{part} appears normal")
                
        if not findings:
            if problems:
                return f"evidence of {', '.join(problems)}"
            return "no significant findings"
                
        return "; ".join(findings)
        
    def _get_diagnosis_text(self, categorized_keywords, transcription):
        """Get text describing diagnosis."""
        problems = categorized_keywords.get("PROBLEM", [])
        
        if not problems:
            # Try to extract diagnosis from transcription
            diagnosis_pattern = r"(?:diagnos(?:is|ed|e) (?:of|as|with)|impression:?|assessment:?) ([^.]*)"
            match = re.search(diagnosis_pattern, transcription, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return "Diagnosis pending further evaluation"
            
        if len(problems) == 1:
            return problems[0]
        else:
            return f"1. {problems[0]}" + ''.join(f"\n2. {p}" for p in problems[1:])
            
    def _get_treatment_text(self, categorized_keywords, transcription):
        """Get text describing treatment plan."""
        treatments = categorized_keywords.get("TREATMENT", [])
        
        if not treatments:
            # Try to extract treatment from transcription
            treatment_pattern = r"(?:recommend(?:ed|ing)?|prescrib(?:ed|ing)?|start(?:ed|ing)?|plan:?) ([^.]*)"
            match = re.search(treatment_pattern, transcription, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return "Supportive care and symptomatic treatment"
            
        if len(treatments) == 1:
            return treatments[0]
        elif len(treatments) == 2:
            return f"{treatments[0]} and {treatments[1]}"
        else:
            return f"{', '.join(treatments[:-1])}, and {treatments[-1]}"
            
    def _get_tests_text(self, categorized_keywords):
        """Get text describing tests."""
        tests = categorized_keywords.get("TEST", [])
        
        if not tests:
            return "No additional tests performed"
            
        if len(tests) == 1:
            return f"{tests[0]} was performed"
        elif len(tests) == 2:
            return f"{tests[0]} and {tests[1]} were performed"
        else:
            return f"{', '.join(tests[:-1])}, and {tests[-1]} were performed"
            
    def _extract_history(self, transcription):
        """Extract patient history from transcription."""
        history_patterns = [
            r"(?:past medical history|pmh):? ([^.]*)",
            r"(?:history of|previously had|has had) ([^.]*)",
            r"(?:patient reports|patient states|patient notes) ([^.]*)"
        ]
        
        for pattern in history_patterns:
            match = re.search(pattern, transcription, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "no significant past medical history"
        
    def _extract_vitals(self, transcription):
        """Extract vital signs from transcription."""
        vitals_pattern = r"(?:vital signs|vitals):? ([^.]*)"
        match = re.search(vitals_pattern, transcription, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Try to extract individual vitals
        bp_pattern = r"(?:blood pressure|bp):? (\d+/\d+)"
        hr_pattern = r"(?:heart rate|pulse|hr):? (\d+)"
        temp_pattern = r"(?:temperature|temp):? (\d+\.?\d*)"
        
        vitals = []
        
        bp_match = re.search(bp_pattern, transcription, re.IGNORECASE)
        if bp_match:
            vitals.append(f"BP {bp_match.group(1)}")
            
        hr_match = re.search(hr_pattern, transcription, re.IGNORECASE)
        if hr_match:
            vitals.append(f"HR {hr_match.group(1)}")
            
        temp_match = re.search(temp_pattern, transcription, re.IGNORECASE)
        if temp_match:
            vitals.append(f"Temp {temp_match.group(1)}°F")
            
        if vitals:
            return ", ".join(vitals)
            
        return "Within normal limits"
        
    def _extract_exam_findings(self, transcription):
        """Extract physical examination findings from transcription."""
        exam_pattern = r"(?:physical exam|examination|exam findings):? ([^.]*)"
        match = re.search(exam_pattern, transcription, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        return "No abnormal findings"
        
    def _extract_medications(self, transcription):
        """Extract medications from transcription."""
        med_pattern = r"(?:medications?|prescrib(?:e|ed|ing)|recommend(?:ed|ing)?) ([^.]*)"
        match = re.search(med_pattern, transcription, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        return "No medications prescribed"
        
    def _create_empty_soap_note(self):
        """Create an empty SOAP note structure."""
        return {
            "subjective": "Patient presents with unspecified symptoms.",
            "objective": "Physical examination was performed.",
            "assessment": "Assessment pending.",
            "plan": "Follow up as needed."
        }
        
    def save_soap_note(self, soap_note, patient_id=None, visit_date=None):
        """Save the SOAP note to a file."""
        try:
            # Generate filename
            if patient_id is None:
                patient_id = "unknown_patient"
                
            if visit_date is None:
                from datetime import datetime
                visit_date = datetime.now().strftime("%Y%m%d")
                
            filename = f"{patient_id}_{visit_date}_soap.json"
            filepath = self.output_dir / filename
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(soap_note, f, indent=2)
                
            logger.info(f"Saved SOAP note to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving SOAP note: {str(e)}")
            return None
