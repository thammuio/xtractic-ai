import os
from pyspark.sql import SparkSession
import PyPDF2
from datetime import datetime


class PDFProcessor:
    """Tool for processing PDF files"""
    
    def __init__(self):
        self.spark = SparkSession.builder\
            .appName("PDF ETL")\
            .config("spark.jars", "postgresql-42.6.0.jar")\
            .getOrCreate()
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
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

    def process_pdfs(self, pdf_dir: str) -> 'pyspark.sql.DataFrame':
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
