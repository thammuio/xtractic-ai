import os
from crewai import Crew, Agent
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import PyPDF2
import psycopg2
from dotenv import load_dotenv

class PDFProcessor:
    def __init__(self):
        self.spark = SparkSession.builder\
            .appName("PDF ETL")\
            .config("spark.jars", "postgresql-42.6.0.jar")\
            .getOrCreate()
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""

    def process_pdfs(self, pdf_dir):
        """Process all PDFs in the directory and create Spark DataFrame"""
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        data = []
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_dir, pdf_file)
            text = self.extract_text_from_pdf(file_path)
            data.append({
                'filename': pdf_file,
                'content': text,
                'processed_at': datetime.now()
            })
        
        df = self.spark.createDataFrame(data)
        return df

    def save_to_postgres(self, df, table_name):
        """Save DataFrame to PostgreSQL"""
        try:
            load_dotenv()
            url = f"jdbc:postgresql://{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
            properties = {
                "user": os.getenv('DB_USER'),
                "password": os.getenv('DB_PASSWORD'),
                "driver": "org.postgresql.Driver"
            }
            
            df.write.jdbc(
                url=url,
                table=table_name,
                mode='append',
                properties=properties
            )
            print(f"Data successfully saved to {table_name}")
        except Exception as e:
            print(f"Error saving to PostgreSQL: {str(e)}")

class ETLAgent(Agent):
    def __init__(self, name="ETL Agent", description="An agent that processes PDF files and stores them in PostgreSQL"):
        super().__init__(name, description)
        self.processor = PDFProcessor()

    def run_etl(self, pdf_dir, table_name):
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
            self.processor.save_to_postgres(transformed_df, table_name)
            
            return "ETL process completed successfully"
        except Exception as e:
            return f"Error during ETL process: {str(e)}"

# Create the ETL agent
etl_agent = ETLAgent()

# Create a Crew to manage the agent
crew = Crew([etl_agent])

if __name__ == "__main__":
    # Example usage
    pdf_directory = "pdfs/"
    table_name = "processed_pdfs"
    
    result = etl_agent.run_etl(pdf_directory, table_name)
    print(result)
