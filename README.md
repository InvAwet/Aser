# Aser - Streamlit PDF Diary Tool

This tool parses and enhances daily diaries using PDF site reports.

## Features
- Upload PDF site report
- Extract structured content
- Process data with AI (Gemini)
- Review and edit parsed data
- Generate a formatted PDF diary

## Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variable
Create a `.env` file or export:
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

### 3. Run the app
```bash
streamlit run app.py
```

## Project Structure
- `app.py`: Main Streamlit application
- `utils/`: Parsing, AI processing, PDF generation, data models
- `requirements.txt`: Python dependencies
- `.gitignore`: Files to ignore
- `.env.example`: Example environment variables