# Canvas QTI Quiz Generator

## Overview
A Python-based CLI tool that converts various document formats (HTML, PDF, Word, Excel, TXT) containing quiz questions into Canvas LMS importable QTI zip files.

**Current State:** Fully configured and ready to use in Replit environment

**Last Updated:** October 15, 2025

## Project Architecture

### Technology Stack
- **Language:** Python 3.11
- **Package Manager:** pip3
- **Key Dependencies:**
  - beautifulsoup4 - HTML parsing
  - PyPDF2 - PDF processing
  - python-docx - Word document processing
  - pandas & openpyxl - Excel file processing
  - boto3 - AWS S3 integration
  - lxml - XML processing

### File Structure
```
├── main.py                    # Interactive menu (Replit entry point)
├── generate_qti.py            # Local files mode generator
├── generate_qti_s3.py         # S3 bucket mode generator
├── generate_qti_enhanced.py   # Enhanced multi-format generator
├── run_generator.sh           # Local mode launcher
├── run_s3_generator.sh        # S3 mode launcher
├── run_enhanced_generator.sh  # Enhanced mode launcher
├── requirements.txt           # Python dependencies
├── .env.example              # S3 configuration template
├── documents/                 # Input folder for local files
├── output/                    # Generated QTI zip files
└── README.md                  # Full documentation
```

## Three Operating Modes

### 1. Local Files Mode
- Processes documents from `documents/` folder
- Supports HTML, PDF, Word files
- Quick and simple for local testing

### 2. S3 Bucket Mode
- Downloads and processes documents from AWS S3
- Requires `.env` configuration with AWS credentials
- Best for cloud-based document storage

### 3. Enhanced Multi-Format Mode (Recommended)
- Processes entire folder structures recursively
- Supports HTML, PDF, DOCX, XLSX, TXT files
- Advanced AWS exam format parsing
- Source file tracking for each question

## How to Use

### Via Interactive Menu (Replit)
1. Run the workflow "Canvas QTI Generator"
2. Select from the menu options
3. Follow the prompts

### Via Command Line
```bash
# Local mode
python3 generate_qti.py

# Enhanced mode with custom folder
python3 generate_qti_enhanced.py /path/to/folder

# S3 mode (after configuring .env)
python3 generate_qti_s3.py
```

## Question Format
Documents should contain questions in these formats:

**Standard Format:**
```
Question: What is 2+2?
A) 3
B) 4 *
C) 5
D) 6
```

**Multiple Select (multiple asterisks):**
```
Question: Which are programming languages?
A) Python *
B) HTML
C) JavaScript *
D) CSS
```

## Output
- Generated files are saved to `output/` directory
- Files are named with timestamp: `canvas_quiz_YYYYMMDD_HHMMSS.zip`
- Import directly into Canvas LMS via Quizzes → Import Quiz

## Configuration

### For S3 Mode
1. Copy `.env.example` to `.env`
2. Edit `.env` with your AWS credentials:
   - S3_BUCKET_NAME
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION

## Recent Changes
- **2025-10-15:** Initial Replit setup completed
  - Installed Python 3.11 and all dependencies
  - Created interactive menu system (main.py)
  - Configured workflow for console output
  - Added .gitignore for Python projects
  - Verified tool functionality with sample documents

## Replit Environment Setup
- Python 3.11 installed via programming_language_install_tool
- All dependencies from requirements.txt installed
- Workflow configured to run main.py for interactive CLI
- Shell scripts made executable (run_*.sh)
- Output directory created and functional
