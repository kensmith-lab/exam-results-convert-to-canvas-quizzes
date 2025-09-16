# Canvas QTI Quiz Generator

Convert multiple document formats containing quiz questions into Canvas LMS importable QTI zip files.

## 🚀 **Three Modes Available:**

### 1. **Local Files Mode** (Original)
Process documents from local `documents/` folder

### 2. **S3 Bucket Mode** 
Process exam documents directly from S3 bucket

### 3. **Enhanced Multi-Format Mode** (NEW!)
Process entire folder structures with comprehensive format support

---

## 📁 **Enhanced Multi-Format Mode** (Recommended for Complex Exam Folders)

### **Supported File Types:**
- ✅ **HTML** (.html, .htm) - Web pages with questions
- ✅ **PDF** (.pdf) - Practice tests and exam documents  
- ✅ **Word** (.docx) - Microsoft Word documents
- ✅ **Excel** (.xlsx, .xls) - Spreadsheets with question data
- ✅ **Text** (.txt) - Plain text files
- ✅ **AWS Exam Formats** - Specialized parsing for AWS certification materials

### **Quick Start:**

#### **Process Entire Folder Structure:**
```bash
# Install enhanced dependencies
pip install -r requirements.txt

# Process any folder (e.g., your dop-c02-organized folder)
./run_enhanced_generator.sh /path/to/your/exam/folder

# Or process local documents folder
./run_enhanced_generator.sh
```

#### **Command Examples:**
```bash
# Process AWS DevOps exam folder
./run_enhanced_generator.sh "C:/dop-co2/dop-c02-organized"

# Process local documents
./run_enhanced_generator.sh

# Direct Python usage
python generate_qti_enhanced.py "/path/to/exam/folder"
```

### **Features:**
- 🔍 **Recursive folder scanning** - Processes all subfolders
- 📊 **Excel support** - Handles .xlsx/.xls files with questions
- 🎯 **AWS exam patterns** - Specialized parsing for AWS certification formats
- 📝 **Source tracking** - Shows which file each question came from
- 🏷️ **Smart question detection** - Multiple pattern recognition algorithms

---

## 📁 **S3 Bucket Mode**

### Quick Setup:

1. **Configure S3 credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your S3 settings
   ```

2. **Run S3 generator:**
   ```bash
   ./run_s3_generator.sh
   ```

---

## 📝 **Local Files Mode**

### Quick Start:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place documents in `documents/` folder:**
   - Add your exam files to the documents folder

3. **Run generator:**
   ```bash
   ./run_generator.sh
   ```

---

## 📋 **Question Format** (Same for All Modes)

Your documents should contain questions in these formats:

### **Standard Format:**
```
Question: What is 2+2?
A) 3
B) 4 *
C) 5
D) 6
```

### **AWS Exam Format:**
```
Question 1: Which AWS service provides object storage?
A) EC2
B) S3 *
C) RDS
D) Lambda

Q2. What is the maximum size for an S3 object?
A. 5TB *
B. 1TB
C. 100GB
D. 500GB
```

### **Multiple Select:**
```
Question: Which are AWS compute services?
A) EC2 *
B) S3
C) Lambda *
D) RDS
```

**Notes:**
- Use `*` after correct answers
- Multiple correct answers = multiple-select question type
- Single correct answer = multiple-choice question type

---

## ✨ **Enhanced Features**

- ✅ **Multi-format support**: HTML, PDF, DOCX, XLSX, TXT
- ✅ **Folder batch processing**: Process entire directory structures
- ✅ **AWS exam patterns**: Specialized parsing for certification materials
- ✅ **S3 Integration**: Pull exams from S3 buckets automatically
- ✅ **Excel support**: Parse spreadsheet-based question banks
- ✅ **Source tracking**: Know which file each question came from
- ✅ **Smart parsing**: Multiple question detection algorithms
- ✅ **Error handling**: Robust parsing with detailed feedback

---

## 🗂️ **File Structure**

```
├── generate_qti_enhanced.py    # Enhanced multi-format generator ⭐
├── generate_qti.py            # Original local generator
├── generate_qti_s3.py         # S3 bucket generator
├── run_enhanced_generator.sh   # Enhanced launcher ⭐
├── run_generator.sh           # Local launcher
├── run_s3_generator.sh        # S3 launcher
├── requirements.txt           # All dependencies
├── .env.example              # S3 configuration template
├── documents/                # Local input documents
├── output/                   # Generated QTI files
└── README.md
```

---

## 🎯 **Canvas Import Steps**

1. Go to your Canvas course
2. Navigate to **Quizzes**
3. Click **Import Quiz**
4. Select **QTI .zip file**
5. Upload the generated file from `output/`
6. Review and publish your quiz

---

## 🔧 **Usage Examples**

### **Process AWS DevOps Exam Folder:**
```bash
# Your folder structure:
# dop-c02-organized/
# ├── practice-tests/
# │   ├── Practice Test 1 DOP-C02.pdf
# │   ├── Practice Test 2 DOP-C02.pdf
# │   └── testing.xlsx
# ├── web-resources/
# │   └── AWSDevOps_v100v100v100.html
# └── documentation/

./run_enhanced_generator.sh "dop-c02-organized"
```

### **Process Local Documents:**
```bash
# Place files in documents/ folder
./run_enhanced_generator.sh
```

### **Process S3 Bucket:**
```bash
# Configure .env file first
./run_s3_generator.sh
```

---

## 🚨 **Troubleshooting**

### **Multi-Format Issues:**
- **Excel files not parsing**: Ensure pandas and openpyxl are installed
- **PDF text extraction**: Some PDFs may need OCR for scanned content
- **Complex layouts**: HTML files with nested structures work best

### **General Issues:**
- **No questions found**: Check document format and question markers
- **Import failed**: Ensure questions have at least 2 choices and 1 correct answer
- **Missing dependencies**: Run `pip install -r requirements.txt`

---

## 📊 **Performance**

- **Enhanced Mode**: Handles complex folder structures with mixed file types
- **Batch processing**: Processes hundreds of files efficiently  
- **Memory efficient**: Streams large files without loading entirely
- **Format detection**: Automatic file type recognition
- **Canvas optimized**: Generated QTI files import seamlessly

---

## 💡 **Tips for Best Results**

1. **Organize your files**: Use clear folder structures
2. **Mark correct answers**: Use `*` or "correct" markers consistently
3. **Test with samples**: Try with a few files first
4. **Check output**: Review questions in Canvas before publishing
5. **Mixed formats**: The enhanced generator handles multiple formats in one run
