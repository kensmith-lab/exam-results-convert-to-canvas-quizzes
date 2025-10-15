# Canvas QTI Quiz Generator - Enhanced Edition

## Overview
A **significantly enhanced** Python-based CLI tool that converts various document formats (HTML, PDF, Word, Excel, TXT) containing quiz questions into Canvas LMS importable QTI zip files.

**Current State:** Fully configured with advanced validation, logging, and preview features

**Version:** 2.0 Enhanced Edition

**Last Updated:** October 15, 2025

---

## 🎉 Major Improvements (v2.0)

### New Features Added:
✨ **Comprehensive Input Validation** - Validates file paths, permissions, and formats before processing
✨ **Advanced Logging System** - Color-coded logs with timestamps saved to logs/ directory
✨ **QTI File Preview & Inspection** - View and validate generated QTI files before Canvas import
✨ **File Cleanup Utility** - Smart cleanup of old generated files and logs
✨ **System Information Dashboard** - View configuration and statistics at a glance
✨ **Question Validation** - Automatic validation of question quality and completeness
✨ **Progress Tracking** - Real-time progress bars and detailed statistics
✨ **Batch Processing Reports** - Comprehensive statistics showing file-by-file results
✨ **Centralized Configuration** - Easy-to-modify config.py for all settings

---

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

### Enhanced File Structure
```
├── main.py                    # ⭐ Enhanced interactive menu with validation
├── utils.py                   # 🆕 Utilities: validation, logging, statistics
├── config.py                  # 🆕 Centralized configuration management
├── generate_qti.py            # Original local files generator (with type fixes)
├── generate_qti_s3.py         # S3 bucket mode generator
├── generate_qti_enhanced.py   # Enhanced multi-format generator
├── run_generator.sh           # Local mode launcher
├── run_s3_generator.sh        # S3 mode launcher
├── run_enhanced_generator.sh  # Enhanced mode launcher
├── requirements.txt           # Python dependencies
├── .env.example              # S3 configuration template
├── documents/                 # Input folder for local files
├── output/                    # Generated QTI zip files
├── logs/                      # 🆕 Application logs with timestamps
└── README.md                  # Full documentation
```

---

## 🚀 How to Use (Enhanced Interface)

### Via Enhanced Interactive Menu (Recommended)
The new main.py provides a feature-rich interactive experience:

1. **Run the workflow** "Canvas QTI Generator"
2. **Choose from 8 options:**
   - 📁 Local Files Mode (with validation)
   - 🌐 S3 Bucket Mode (with config checking)
   - ⭐ Enhanced Multi-Format Mode (with progress tracking)
   - 📊 Preview Generated QTI Files (inspect zip contents)
   - 🧹 Cleanup Old Files (smart file management)
   - 📖 View README (paginated view)
   - ℹ️ System Info & Configuration (see all settings)
   - 🚪 Exit

### Key Features in Each Mode:

#### 1. Local Files Mode
- ✓ Validates documents/ directory exists and is readable
- ✓ Counts supported files before processing
- ✓ Confirms action before proceeding
- ✓ Shows progress and results

#### 2. S3 Bucket Mode
- ✓ Checks .env configuration is complete
- ✓ Validates AWS credentials are present
- ✓ Lists missing configuration variables
- ✓ Safe error handling

#### 3. Enhanced Multi-Format Mode
- ✓ Validates folder path and permissions
- ✓ Counts files recursively
- ✓ Shows supported formats
- ✓ Confirms before processing
- ✓ Comprehensive error handling

#### 4. Preview QTI Files
- ✓ Lists all generated QTI files with size and date
- ✓ Shows file count and structure
- ✓ Validates QTI format (checks for XML files)
- ✓ Detailed inspection of zip contents
- ✓ Preview manifest files

#### 5. Cleanup Utility
- ✓ Smart options: keep last 5/10, remove all, etc.
- ✓ Separate cleanup for QTI and log files
- ✓ Confirmation before destructive operations
- ✓ Summary of removed files

---

## 🛠️ Configuration (config.py)

### Customizable Settings:
```python
SUPPORTED_FORMATS = ['.html', '.htm', '.pdf', '.docx', '.xlsx', '.xls', '.txt']
MAX_FILE_SIZE_MB = 100
MIN_CHOICES = 2
MAX_CHOICES = 20
DEFAULT_POINTS_PER_QUESTION = 1
```

### Directory Settings:
- Output: `output/` (auto-created)
- Documents: `documents/` (auto-created)
- Logs: `logs/` (auto-created)
- Temp: `temp_qti/` (auto-cleaned)

---

## 📊 Enhanced Features Details

### Input Validation (utils.py → Validator)
```python
✓ Folder path validation (exists, readable, writable)
✓ File format checking (supported extensions)
✓ File permissions verification
✓ File size limits (max 100MB)
✓ Empty file detection
```

### Logging System (utils.py → Logger)
```python
✓ Color-coded output (success=green, error=red, etc.)
✓ Timestamp for every message
✓ File logging to logs/ directory
✓ Progress bars for long operations
✓ Elapsed time tracking
```

### Question Validation (utils.py → QuestionValidator)
```python
✓ Minimum question text length check
✓ Choice count validation (2-20 choices)
✓ Correct answer verification
✓ Question type validation
✓ Detailed issue reporting
```

### Statistics Tracking (utils.py → Statistics)
```python
✓ File processing counts (success/failed)
✓ Question counts by type
✓ Top files by question count
✓ Comprehensive summary reports
```

---

## 📝 Question Format (Unchanged)

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

---

## 🎯 Output & Results

### Generated Files:
- **Location:** `output/` directory
- **Format:** `canvas_quiz_YYYYMMDD_HHMMSS.zip` or `multi_format_quiz_YYYYMMDD_HHMMSS.zip`
- **Import:** Directly into Canvas LMS via Quizzes → Import Quiz

### Logs:
- **Location:** `logs/` directory
- **Format:** `qti_gen_YYYYMMDD.log`
- **Content:** Timestamped operations, errors, warnings, and info

### Preview Features:
- View all generated QTI files
- Check file sizes and creation dates
- Validate QTI structure (XML presence)
- Inspect zip contents
- Read manifest files

---

## 🔧 Configuration (S3 Mode)

### For S3 Mode:
1. Copy `.env.example` to `.env`
2. Edit `.env` with your AWS credentials:
   - S3_BUCKET_NAME
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION

### Validation:
The system checks S3 configuration and provides specific error messages for missing variables.

---

## 📈 Statistics & Reports

### Processing Summary:
- Total files scanned
- Successfully processed files
- Failed files (with error details)
- Total questions found
- Valid vs invalid questions
- Question type breakdown (multiple choice vs select)
- Top files by question count

---

## 🚀 Recent Changes

### 2025-10-15: Version 2.0 - Major Enhancement Release
- ✅ Created utils.py with comprehensive validation, logging, and statistics
- ✅ Created config.py for centralized configuration management
- ✅ Completely redesigned main.py with 8 feature-rich modes
- ✅ Added QTI file preview and inspection capabilities
- ✅ Implemented smart file cleanup utility
- ✅ Added system information dashboard
- ✅ Enhanced error handling and user feedback
- ✅ Fixed all type hint issues in generate_qti.py
- ✅ Improved type safety in generate_qti_enhanced.py
- ✅ Added color-coded terminal output
- ✅ Implemented progress tracking and reporting
- ✅ Created comprehensive logging system
- ✅ Added input validation for all operations

### 2025-10-15: Initial Replit Setup
- Installed Python 3.11 and all dependencies
- Configured workflow for console output
- Added .gitignore for Python projects
- Verified tool functionality with sample documents

---

## 💡 Best Practices

### For Best Results:
1. **Validate First** - Use system info to check configuration
2. **Preview Output** - Always preview QTI files before importing to Canvas
3. **Clean Regularly** - Use cleanup utility to manage disk space
4. **Check Logs** - Review logs/ directory for detailed operation history
5. **Test Small Batches** - Process a few files first to validate format

### Troubleshooting:
1. Check system info (option 7) for configuration status
2. Review logs in logs/ directory for detailed errors
3. Use preview (option 4) to validate QTI file structure
4. Ensure proper file formats and permissions
5. Verify S3 configuration if using S3 mode

---

## 🔒 Replit Environment Setup

- ✅ Python 3.11 installed via programming_language_install_tool
- ✅ All dependencies from requirements.txt installed
- ✅ Workflow configured to run enhanced main.py
- ✅ Shell scripts made executable (run_*.sh)
- ✅ Output directory created and functional
- ✅ Logs directory created for logging
- ✅ Utils and config modules integrated

---

## 🎓 User Preferences

_This section will track user preferences and customizations as they're specified_

---

## 📚 Additional Notes

- The enhanced version maintains backward compatibility with all original generators
- All original shell scripts (run_*.sh) continue to work
- Color-coded output improves readability in terminal
- Validation prevents common errors before processing
- Statistics help track processing efficiency
