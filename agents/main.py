from crewai import Crew
from .etl_agent import ETLAgent


def main():
    # Create the ETL agent
    etl_agent = ETLAgent()

    # Create a Crew to manage the agent
    crew = Crew([etl_agent])

    # Example usage
    pdf_directory = "pdfs/"
    table_name = "processed_pdfs"
    
    result = etl_agent.run_etl(pdf_directory, table_name)
    print(result)

if __name__ == "__main__":
    main()
