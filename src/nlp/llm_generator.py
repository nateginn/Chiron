"""
Generate SOAP notes using local LLM.
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from ..utils.logger import get_logger

logger = get_logger(__name__)

class LLMGenerator:
    def __init__(self, config):
        self.model_path = config.get('LLAMA_MODEL_PATH')
        self.model = None
        self.tokenizer = None
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize the LLM model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            logger.info("LLM model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
            
    def generate_soap_note(self, template, keywords):
        """Generate SOAP note based on template and keywords."""
        try:
            prompt = self._create_prompt(template, keywords)
            inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
            
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                temperature=0.7,
                num_return_sequences=1
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"SOAP note generation error: {str(e)}")
            raise
            
    def _create_prompt(self, template, keywords):
        """Create a prompt for the LLM."""
        return f"""Generate a medical SOAP note based on the following template:
        {template}
        
        Using these medical keywords:
        {', '.join(keywords)}
        
        SOAP Note:"""
