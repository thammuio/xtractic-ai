<p align="center">
  <img src="images/xtractic-ai3.png" alt="Xtractic AI Logo" width="250"/>
</p>
<h1 align="center" style="font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;">Xtractic AI</h1>



This project implements an ETL (Extract, Transform, Load) pipeline using AI for processing PDF documents using Apache Spark and storing the extracted data in PostgreSQL.

## Features

- Extract text from PDF files using PyPDF2
- Process multiple PDF files using Apache Spark
- Transform data with Spark DataFrame operations
- Load processed data into PostgreSQL
- Agent-based architecture using Crew AI

## Prerequisites

- Python 3.8+
- Apache Spark 3.4.1
- PostgreSQL 14+
- Java 8+

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

## Usage

1. Place your PDF files in the `pdfs/` directory
2. Run the ETL process:
```bash
![Xtractic AI Logo](images/xtractic-ai2.png)

Xtractic AI

python etl_agent.py
```

## Project Structure

- `etl_agent.py`: Main ETL agent implementation
- `requirements.txt`: Project dependencies
- `.env.example`: Example environment configuration
- `README.md`: Project documentation

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.
