"""
Database management for patient records and SOAP notes.
"""
import sqlite3
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, config):
        self.db_path = config.get('DB_CONNECTION_STRING')
        self.conn = None
        self.initialize_db()
        
    def initialize_db(self):
        """Initialize the SQLite database and create tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
            
    def _create_tables(self):
        """Create necessary database tables."""
        cursor = self.conn.cursor()
        
        # Create patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                dob DATE,
                mrn TEXT UNIQUE
            )
        ''')
        
        # Create soap_notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soap_notes (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER,
                date DATETIME,
                content TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        self.conn.commit()
        
    def save_soap_note(self, patient_id, content):
        """Save a SOAP note to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO soap_notes (patient_id, date, content)
                VALUES (?, CURRENT_TIMESTAMP, ?)
            ''', (patient_id, content))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving SOAP note: {str(e)}")
            raise
