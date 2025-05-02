import psycopg2
from dotenv import load_dotenv
import os


class DatabaseUtils:
    """Utility class for database operations"""
    
    def __init__(self):
        load_dotenv()
        self.url = f"jdbc:postgresql://{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        self.properties = {
            "user": os.getenv('DB_USER'),
            "password": os.getenv('DB_PASSWORD'),
            "driver": "org.postgresql.Driver"
        }

    def save_to_postgres(self, df, table_name: str) -> None:
        """Save DataFrame to PostgreSQL"""
        try:
            df.write.jdbc(
                url=self.url,
                table=table_name,
                mode='append',
                properties=self.properties
            )
            print(f"Data successfully saved to {table_name}")
        except Exception as e:
            print(f"Error saving to PostgreSQL: {str(e)}")
