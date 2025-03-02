"""
Tests for the NLP components.
"""
import pytest
from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.template_matcher import TemplateMatcher
from src.nlp.llm_generator import LLMGenerator

def test_keyword_extractor():
    extractor = KeywordExtractor()
    test_text = "Patient presents with severe migraine and nausea."
    keywords = extractor.extract_keywords(test_text)
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert all(isinstance(k, dict) for k in keywords)

def test_template_matcher():
    matcher = TemplateMatcher()
    test_keywords = ["migraine", "nausea", "photophobia"]
    template = matcher.find_matching_template(test_keywords)
    assert isinstance(template, str)
    assert len(template) > 0
