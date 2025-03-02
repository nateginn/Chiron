"""
Test the NLP pipeline components.
"""
import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.template_matcher import TemplateMatcher
from src.nlp.template_filler import TemplateFiller
from src.nlp.pipeline import NLPPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_keyword_extractor():
    """Test the keyword extractor."""
    # Sample medical text
    text = """
    Patient presents with right knee pain that has been ongoing for 3 weeks. 
    The pain is worse with walking and climbing stairs. Patient reports swelling 
    and occasional clicking. No previous history of knee injury. 
    Physical examination reveals tenderness along the medial joint line and 
    mild effusion. Range of motion is limited. McMurray test is positive.
    Assessment: Medial meniscus tear.
    Plan: MRI of the right knee, NSAIDs for pain, referral to orthopedics.
    """
    
    # Initialize the keyword extractor
    extractor = KeywordExtractor()
    
    # Extract keywords
    keywords = extractor.extract_keywords(text)
    
    # Print the results
    print("\n=== Keyword Extraction Results ===")
    for keyword in keywords:
        print(f"{keyword['text']} ({keyword['label']}): {keyword['score']:.2f}")
        
    return keywords

def test_template_matcher(keywords=None):
    """Test the template matcher."""
    if keywords is None:
        # Sample keywords if none provided
        keywords = [
            {"text": "knee", "label": "ANATOMY", "score": 0.95},
            {"text": "pain", "label": "PROBLEM", "score": 0.92},
            {"text": "swelling", "label": "PROBLEM", "score": 0.88},
            {"text": "MRI", "label": "TEST", "score": 0.97},
            {"text": "NSAIDs", "label": "TREATMENT", "score": 0.94}
        ]
    
    # Initialize the template matcher
    matcher = TemplateMatcher()
    
    # Find matching template
    template = matcher.find_matching_template(keywords)
    
    # Print the results
    print("\n=== Template Matching Results ===")
    print(f"Template ID: {template.get('id', 'unknown')}")
    print(f"Template Name: {template.get('name', 'Unknown')}")
    if 'template' in template:
        print("Template Sections:")
        for section, content in template['template'].items():
            print(f"  {section.upper()}: {content}")
            
    return template

def test_template_filler(template=None, keywords=None):
    """Test the template filler."""
    # Sample transcription
    transcription = """
    Doctor: Good morning. What brings you in today?
    
    Patient: I've been having pain in my right knee for about 3 weeks now. It's getting worse.
    
    Doctor: Can you describe the pain and when it occurs?
    
    Patient: It hurts when I walk, especially going up and down stairs. Sometimes I hear a clicking sound, and it's been swelling up.
    
    Doctor: Have you had any previous injuries to this knee?
    
    Patient: No, nothing serious that I can remember.
    
    Doctor: Let me examine your knee. [pause] I can see some swelling. Does it hurt when I press here?
    
    Patient: Yes, that's tender.
    
    Doctor: I'm going to test your range of motion. [pause] There's some limitation and I'm getting a positive McMurray test, which suggests a meniscus issue.
    
    Doctor: Based on your symptoms and my examination, I believe you have a medial meniscus tear. I'd like to order an MRI to confirm. In the meantime, I'll prescribe some anti-inflammatory medication for the pain and swelling. I'm also going to refer you to orthopedics for further evaluation and treatment.
    
    Patient: How long will it take to heal?
    
    Doctor: That depends on the severity of the tear. Some tears heal with conservative treatment, while others may require surgery. The orthopedic specialist will be able to give you more specific information after reviewing your MRI.
    
    Patient: Okay, thank you doctor.
    
    Doctor: You're welcome. The front desk will schedule your MRI and orthopedic appointment. Take the medication as directed and try to avoid activities that cause pain. Use ice for 20 minutes several times a day to help with the swelling.
    """
    
    if keywords is None:
        # Extract keywords if none provided
        extractor = KeywordExtractor()
        keywords = extractor.extract_keywords(transcription)
    
    if template is None:
        # Find matching template if none provided
        matcher = TemplateMatcher()
        template = matcher.find_matching_template(keywords)
    
    # Initialize the template filler
    filler = TemplateFiller()
    
    # Fill the template
    soap_note = filler.fill_template(template, transcription, keywords)
    
    # Print the results
    print("\n=== Template Filling Results ===")
    for section, content in soap_note.items():
        print(f"\n{section.upper()}:")
        print(content)
        
    return soap_note

def test_full_pipeline():
    """Test the full NLP pipeline."""
    # Sample transcription
    transcription = """
    Doctor: Good morning. What brings you in today?
    
    Patient: I've been having these terrible headaches for the past two weeks. They're really intense.
    
    Doctor: I'm sorry to hear that. Can you describe the headaches? Where are they located and how often do they occur?
    
    Patient: They're mostly on one side, usually the right side of my head. They come on suddenly and can last for hours. I've been getting them almost daily now.
    
    Doctor: Do you notice any triggers or warning signs before they start?
    
    Patient: Sometimes I see flashing lights or zigzag lines in my vision about 30 minutes before the headache starts. And bright lights and loud noises make it worse.
    
    Doctor: Any nausea or vomiting with these headaches?
    
    Patient: Yes, I often feel nauseated and I've vomited a few times during the worst ones.
    
    Doctor: Have you taken anything for the pain?
    
    Patient: I've tried over-the-counter pain relievers like ibuprofen, but they don't help much.
    
    Doctor: Let me check your vital signs and do a neurological examination. [pause] Your blood pressure is 128/82, heart rate is 76, and temperature is normal. Your neurological exam is normal as well.
    
    Doctor: Based on your symptoms - the one-sided headache, visual aura, sensitivity to light and sound, and associated nausea - you're experiencing migraine headaches. This is a common but often debilitating condition.
    
    Patient: Is there anything that can help? These are really affecting my work.
    
    Doctor: Yes, there are several approaches we can take. I'm going to prescribe sumatriptan, which can help stop a migraine once it starts. Take it at the first sign of a headache or aura. I also want you to start keeping a headache diary to identify potential triggers.
    
    Doctor: For prevention, try to maintain a regular sleep schedule, stay hydrated, and manage stress. If these episodes continue frequently, we might consider a daily preventive medication.
    
    Patient: How long will I have to deal with these?
    
    Doctor: Migraine is often a chronic condition, but many people find that with proper treatment and lifestyle adjustments, they can significantly reduce the frequency and severity of attacks. We'll work together to find the best management strategy for you.
    
    Patient: Thank you, doctor.
    
    Doctor: You're welcome. If the sumatriptan doesn't provide relief or if your symptoms worsen, please call me. I'd like to see you again in one month to assess how you're responding to treatment.
    """
    
    # Initialize the NLP pipeline
    pipeline = NLPPipeline()
    
    # Process the transcription
    soap_note = pipeline.process(transcription, "test_patient", "20230801")
    
    # Print the results
    print("\n=== Full Pipeline Results ===")
    for section, content in soap_note.items():
        print(f"\n{section.upper()}:")
        print(content)
        
    return soap_note

if __name__ == "__main__":
    print("Testing NLP Pipeline Components")
    
    # Test each component
    keywords = test_keyword_extractor()
    template = test_template_matcher(keywords)
    soap_note = test_template_filler(template, keywords)
    
    # Test full pipeline
    full_soap_note = test_full_pipeline()
    
    print("\nAll tests completed successfully!")
