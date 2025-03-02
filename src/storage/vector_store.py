"""
Vector database for storing and retrieving SOAP templates.
"""
import faiss
import numpy as np
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, config):
        self.vector_db_path = config.get('VECTOR_DB_PATH')
        self.dimension = 768  # Default for medical BERT models
        self.index = None
        self.initialize_store()
        
    def initialize_store(self):
        """Initialize the FAISS vector store."""
        try:
            index_path = Path(self.vector_db_path) / "templates.index"
            
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
                logger.info("Loaded existing vector store")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                logger.info("Created new vector store")
        except Exception as e:
            logger.error(f"Vector store initialization error: {str(e)}")
            raise
            
    def add_template(self, template_embedding, template_text):
        """Add a new template to the vector store."""
        try:
            self.index.add(np.array([template_embedding]))
            # Save template text mapping
            return True
        except Exception as e:
            logger.error(f"Error adding template: {str(e)}")
            raise
            
    def search_similar(self, query_embedding, k=1):
        """Search for similar templates."""
        try:
            D, I = self.index.search(np.array([query_embedding]), k)
            return D[0], I[0]
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
