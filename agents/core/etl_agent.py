from crewai import Agent
from .tools.pdf_processor import PDFProcessor
from .tools.db_utils import DatabaseUtils
from pyspark.sql.functions import col

class ETLAgent(Agent):
    """Agent that handles ETL operations for PDF processing"""
    
    def __init__(self, name="ETL Agent", description="An agent that processes PDF files and stores them in PostgreSQL"):
        super().__init__(name, description)
        self.processor = PDFProcessor()
        self.db_utils = DatabaseUtils()

    def run_etl(self, pdf_dir: str, table_name: str) -> str:
        """Run the complete ETL process"""
        try:
            # Extract
            print("Extracting data from PDFs...")
            df = self.processor.process_pdfs(pdf_dir)
            
            # Transform
            print("Transforming data...")
            transformed_df = df.withColumn(
                'word_count',
                col('content').rlike('.+').cast('integer')
            )
            
            # Load
            print("Loading data into PostgreSQL...")
            self.db_utils.save_to_postgres(transformed_df, table_name)
            
            return "ETL process completed successfully"
        except Exception as e:
            return f"Error during ETL process: {str(e)}"
