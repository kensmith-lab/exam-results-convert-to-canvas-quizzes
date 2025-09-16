#!/usr/bin/env python3
"""
Canvas QTI Quiz Generator with S3 Integration
Downloads exam documents from S3 bucket and converts them into Canvas LMS importable QTI .zip files
Supports HTML and PDF files from S3
"""

import os
import re
import sys
import uuid
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import io

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()

# Import required libraries with auto-install
try:
    from bs4 import BeautifulSoup
    import PyPDF2
    from docx import Document
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Installing required dependencies...")
    os.system("pip install beautifulsoup4 PyPDF2 python-docx lxml boto3")
    from bs4 import BeautifulSoup
    import PyPDF2
    from docx import Document
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError


class S3DocumentManager:
    """Handles S3 operations for downloading exam documents"""
    
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.folder_prefix = os.getenv('S3_FOLDER_PREFIX', 'exams/')
        self.temp_dir = Path(os.getenv('TEMP_DIR', 'temp_downloads'))
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize S3 client
        try:
            # Try to use AWS profile first, then access keys
            aws_profile = os.getenv('AWS_PROFILE')
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
                self.s3_client = session.client('s3')
            else:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
                )
            print(f"✅ Connected to S3 bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ Failed to connect to S3: {e}")
            print("Please check your AWS credentials and configuration.")
            sys.exit(1)
    
    def list_exam_files(self) -> List[str]:
        """List all exam files in the S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.folder_prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    # Filter for supported file types
                    if key.lower().endswith(('.html', '.htm', '.pdf', '.docx')):
                        files.append(key)
            
            return files
        except ClientError as e:
            print(f"❌ Error listing S3 objects: {e}")
            return []
    
    def download_file(self, s3_key: str) -> Optional[Path]:
        """Download a file from S3 to local temp directory"""
        try:
            # Create local filename
            filename = Path(s3_key).name
            local_path = self.temp_dir / filename
            
            # Download file
            self.s3_client.download_file(self.bucket_name, s3_key, str(local_path))
            print(f"📥 Downloaded: {filename}")
            return local_path
            
        except ClientError as e:
            print(f"❌ Error downloading {s3_key}: {e}")
            return None
    
    def download_all_exams(self) -> List[Path]:
        """Download all exam files from S3"""
        exam_files = self.list_exam_files()
        
        if not exam_files:
            print(f"❌ No exam files found in S3 bucket '{self.bucket_name}' with prefix '{self.folder_prefix}'")
            print("Supported formats: .html, .htm, .pdf, .docx")
            return []
        
        print(f"📋 Found {len(exam_files)} exam files in S3:")
        for file in exam_files:
            print(f"   - {file}")
        
        downloaded_files = []
        for s3_key in exam_files:
            local_path = self.download_file(s3_key)
            if local_path:
                downloaded_files.append(local_path)
        
        print(f"✅ Downloaded {len(downloaded_files)} files")
        return downloaded_files
    
    def cleanup_temp_files(self):
        """Clean up temporary downloaded files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up temporary files")
        except Exception as e:
            print(f"⚠️  Warning: Could not cleanup temp files: {e}")


class Question:
    """Represents a quiz question"""
    def __init__(self, question_text: str, question_type: str, choices: List[str], 
                 correct_answers: List[int], points: int = 1):
        self.id = str(uuid.uuid4())
        self.question_text = question_text.strip()
        self.question_type = question_type  # 'multiple_choice' or 'multiple_select'
        self.choices = [choice.strip() for choice in choices]
        self.correct_answers = correct_answers  # List of indices (0-based)
        self.points = points


class DocumentParser:
    """Enhanced parser for documents from S3"""
    
    @staticmethod
    def parse_file(file_path: Path) -> List[Question]:
        """Parse any supported file type"""
        questions = []
        
        try:
            if file_path.suffix.lower() in ['.html', '.htm']:
                questions = DocumentParser.parse_html(str(file_path))
            elif file_path.suffix.lower() == '.pdf':
                questions = DocumentParser.parse_pdf(str(file_path))
            elif file_path.suffix.lower() == '.docx':
                questions = DocumentParser.parse_docx(str(file_path))
            else:
                print(f"⚠️  Unsupported file format: {file_path.suffix}")
                
        except Exception as e:
            print(f"❌ Error parsing {file_path.name}: {e}")
        
        return questions
    
    @staticmethod
    def parse_html(file_path: str) -> List[Question]:
        """Parse HTML file for questions"""
        questions = []
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Look for common question patterns
        question_blocks = soup.find_all(['div', 'p', 'section'], 
                                      class_=re.compile(r'question|quiz|item', re.I))
        
        if not question_blocks:
            # Fallback: parse text content directly
            text_content = soup.get_text()
            questions = DocumentParser._parse_text_content(text_content)
        else:
            for block in question_blocks:
                question = DocumentParser._extract_question_from_block(block.get_text())
                if question:
                    questions.append(question)
        
        return questions
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[Question]:
        """Parse PDF file for questions"""
        questions = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        
        questions = DocumentParser._parse_text_content(text_content)
        return questions
    
    @staticmethod
    def parse_docx(file_path: str) -> List[Question]:
        """Parse DOCX file for questions"""
        doc = Document(file_path)
        text_content = "\n".join([para.text for para in doc.paragraphs])
        return DocumentParser._parse_text_content(text_content)
    
    @staticmethod
    def _parse_text_content(text: str) -> List[Question]:
        """Parse text content for question patterns"""
        questions = []
        
        # Split text into potential question blocks
        blocks = re.split(r'\n\s*\n', text)
        
        for block in blocks:
            if DocumentParser._looks_like_question(block):
                question = DocumentParser._extract_question_from_text(block)
                if question:
                    questions.append(question)
        
        return questions
    
    @staticmethod
    def _looks_like_question(text: str) -> bool:
        """Check if text block looks like a question"""
        text = text.strip()
        if len(text) < 10:
            return False
        
        # Check for question markers
        has_question_marker = bool(re.search(r'(?:question\s*\d*[:.?]|\?)', text, re.I))
        has_choices = bool(re.search(r'[A-Za-z]\)|\d+\.', text))
        
        return has_question_marker or has_choices
    
    @staticmethod
    def _extract_question_from_text(text: str) -> Question:
        """Extract question from text block"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) < 3:  # Need at least question + 2 choices
            return None
        
        # Find question text (usually first line or contains ?)
        question_text = ""
        choice_start_idx = 0
        
        for i, line in enumerate(lines):
            if '?' in line or re.match(r'question\s*\d*[:.]\s*', line, re.I):
                question_text = re.sub(r'question\s*\d*[:.]\s*', '', line, flags=re.I).strip()
                choice_start_idx = i + 1
                break
        
        if not question_text and lines:
            question_text = lines[0]
            choice_start_idx = 1
        
        # Extract choices
        choices = []
        for line in lines[choice_start_idx:]:
            # Remove choice markers (A), 1., etc.
            clean_choice = re.sub(r'^[A-Za-z]\)|\d+\.\s*', '', line).strip()
            if clean_choice:
                choices.append(clean_choice)
        
        if len(choices) < 2:
            return None
        
        # Determine correct answers (look for markers like *, CORRECT, etc.)
        correct_answers = []
        for i, choice in enumerate(choices):
            if re.search(r'\*|correct|right|answer', choice, re.I):
                correct_answers.append(i)
                choices[i] = re.sub(r'\s*\*|correct|right|answer', '', choice, flags=re.I).strip()
        
        # Default to first choice if no correct answer found
        if not correct_answers:
            correct_answers = [0]
        
        # Determine question type
        question_type = 'multiple_select' if len(correct_answers) > 1 else 'multiple_choice'
        
        return Question(question_text, question_type, choices, correct_answers)
    
    @staticmethod
    def _extract_question_from_block(text: str) -> Question:
        """Extract question from HTML block"""
        return DocumentParser._extract_question_from_text(text)


class QTIGenerator:
    """Generates QTI-compliant XML and zip files"""
    
    def __init__(self, quiz_title: str = "S3 Imported Quiz"):
        self.quiz_title = quiz_title
        self.quiz_id = str(uuid.uuid4())
        
    def generate_qti_zip(self, questions: List[Question], output_path: str):
        """Generate complete QTI zip file"""
        
        # Create temporary directory structure
        temp_dir = Path("temp_qti")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Generate manifest file
            self._create_manifest(temp_dir, questions)
            
            # Generate assessment XML
            self._create_assessment_xml(temp_dir, questions)
            
            # Create zip file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_dir))
                        zipf.write(file_path, arcname)
            
            print(f"📦 QTI zip file created: {output_path}")
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _create_manifest(self, temp_dir: Path, questions: List[Question]):
        """Create imsmanifest.xml"""
        
        manifest = ET.Element("manifest")
        manifest.set("xmlns", "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1")
        manifest.set("xmlns:lom", "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource")
        manifest.set("xmlns:imsqti", "http://www.imsglobal.org/xsd/imsqti_v2p1")
        manifest.set("identifier", f"man_{self.quiz_id}")
        
        # Metadata
        metadata = ET.SubElement(manifest, "metadata")
        lom_general = ET.SubElement(metadata, "lom:general")
        lom_title = ET.SubElement(lom_general, "lom:title")
        lom_string = ET.SubElement(lom_title, "lom:string")
        lom_string.text = self.quiz_title
        
        # Organizations
        organizations = ET.SubElement(manifest, "organizations")
        organizations.set("default", f"org_{self.quiz_id}")
        
        organization = ET.SubElement(organizations, "organization")
        organization.set("identifier", f"org_{self.quiz_id}")
        
        title = ET.SubElement(organization, "title")
        title.text = self.quiz_title
        
        # Resources
        resources = ET.SubElement(manifest, "resources")
        
        # Assessment resource
        assessment_resource = ET.SubElement(resources, "resource")
        assessment_resource.set("identifier", f"assessment_{self.quiz_id}")
        assessment_resource.set("type", "imsqti_xmlv2p1")
        assessment_resource.set("href", "assessment.xml")
        
        file_elem = ET.SubElement(assessment_resource, "file")
        file_elem.set("href", "assessment.xml")
        
        # Write manifest
        tree = ET.ElementTree(manifest)
        ET.indent(tree, space="  ", level=0)
        tree.write(temp_dir / "imsmanifest.xml", encoding="utf-8", xml_declaration=True)
    
    def _create_assessment_xml(self, temp_dir: Path, questions: List[Question]):
        """Create assessment.xml with questions"""
        
        assessment = ET.Element("assessmentTest")
        assessment.set("xmlns", "http://www.imsglobal.org/xsd/imsqti_v2p1")
        assessment.set("identifier", f"assessment_{self.quiz_id}")
        assessment.set("title", self.quiz_title)
        
        # Test part
        test_part = ET.SubElement(assessment, "testPart")
        test_part.set("identifier", "testpart_1")
        test_part.set("navigationMode", "linear")
        test_part.set("submissionMode", "individual")
        
        # Assessment section
        section = ET.SubElement(test_part, "assessmentSection")
        section.set("identifier", "section_1")
        section.set("title", "Questions")
        section.set("visible", "true")
        
        # Add questions
        for i, question in enumerate(questions):
            item_ref = ET.SubElement(section, "assessmentItemRef")
            item_ref.set("identifier", f"item_{question.id}")
            item_ref.set("href", f"item_{question.id}.xml")
            
            # Create individual question file
            self._create_question_xml(temp_dir, question)
        
        # Write assessment
        tree = ET.ElementTree(assessment)
        ET.indent(tree, space="  ", level=0)
        tree.write(temp_dir / "assessment.xml", encoding="utf-8", xml_declaration=True)
    
    def _create_question_xml(self, temp_dir: Path, question: Question):
        """Create individual question XML file"""
        
        item = ET.Element("assessmentItem")
        item.set("xmlns", "http://www.imsglobal.org/xsd/imsqti_v2p1")
        item.set("identifier", f"item_{question.id}")
        item.set("title", question.question_text[:50] + "...")
        item.set("adaptive", "false")
        item.set("timeDependent", "false")
        
        # Response declaration
        response_decl = ET.SubElement(item, "responseDeclaration")
        response_decl.set("identifier", "RESPONSE")
        response_decl.set("cardinality", "multiple" if question.question_type == "multiple_select" else "single")
        response_decl.set("baseType", "identifier")
        
        # Correct response
        correct_response = ET.SubElement(response_decl, "correctResponse")
        for correct_idx in question.correct_answers:
            value = ET.SubElement(correct_response, "value")
            value.text = f"choice_{correct_idx}"
        
        # Outcome declaration
        outcome_decl = ET.SubElement(item, "outcomeDeclaration")
        outcome_decl.set("identifier", "SCORE")
        outcome_decl.set("cardinality", "single")
        outcome_decl.set("baseType", "float")
        
        default_value = ET.SubElement(outcome_decl, "defaultValue")
        value = ET.SubElement(default_value, "value")
        value.text = "0"
        
        # Item body
        item_body = ET.SubElement(item, "itemBody")
        
        # Question text
        div = ET.SubElement(item_body, "div")
        p = ET.SubElement(div, "p")
        p.text = question.question_text
        
        # Choice interaction
        interaction_type = "choiceInteraction"
        interaction = ET.SubElement(item_body, interaction_type)
        interaction.set("responseIdentifier", "RESPONSE")
        interaction.set("shuffle", "false")
        
        if question.question_type == "multiple_select":
            interaction.set("maxChoices", str(len(question.choices)))
        else:
            interaction.set("maxChoices", "1")
        
        # Add choices
        for i, choice_text in enumerate(question.choices):
            simple_choice = ET.SubElement(interaction, "simpleChoice")
            simple_choice.set("identifier", f"choice_{i}")
            simple_choice.text = choice_text
        
        # Response processing
        response_processing = ET.SubElement(item, "responseProcessing")
        response_processing.set("template", "http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct")
        
        # Write question file
        tree = ET.ElementTree(item)
        ET.indent(tree, space="  ", level=0)
        tree.write(temp_dir / f"item_{question.id}.xml", encoding="utf-8", xml_declaration=True)


def check_configuration():
    """Check if S3 configuration is properly set"""
    required_vars = ['S3_BUCKET_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your S3 configuration")
        print("3. Run the script again")
        return False
    
    # Check AWS credentials
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_profile = os.getenv('AWS_PROFILE')
    
    if not aws_access_key and not aws_profile:
        print("❌ AWS credentials not configured")
        print("Please set either:")
        print("- AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY in .env")
        print("- AWS_PROFILE in .env (if using AWS CLI profiles)")
        return False
    
    return True


def main():
    """Main function to process S3 documents and generate QTI"""
    
    print("🚀 Canvas QTI Generator - S3 Edition")
    print("====================================")
    
    # Check configuration
    if not check_configuration():
        return
    
    # Initialize S3 manager
    try:
        s3_manager = S3DocumentManager()
    except Exception as e:
        print(f"❌ Failed to initialize S3 connection: {e}")
        return
    
    # Create output directory
    output_dir = Path(os.getenv('OUTPUT_DIR', 'output'))
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Download all exam files from S3
        print("\n📥 Downloading exam files from S3...")
        document_files = s3_manager.download_all_exams()
        
        if not document_files:
            return
        
        all_questions = []
        
        # Process each document
        print(f"\n🔍 Processing {len(document_files)} exam files...")
        for doc_file in document_files:
            print(f"Processing {doc_file.name}...")
            
            questions = DocumentParser.parse_file(doc_file)
            all_questions.extend(questions)
            print(f"  ✅ Found {len(questions)} questions")
        
        if not all_questions:
            print("\n❌ No questions found in any documents.")
            print("\nExpected format in your S3 files:")
            print("Question: What is 2+2?")
            print("A) 3")
            print("B) 4 *")  # * indicates correct answer
            print("C) 5")
            return
        
        print(f"\n📊 Total questions found: {len(all_questions)}")
        
        # Generate QTI zip
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"s3_canvas_quiz_{timestamp}.zip"
        
        print(f"\n📦 Generating QTI zip file...")
        generator = QTIGenerator(f"S3 Quiz Import {timestamp}")
        generator.generate_qti_zip(all_questions, str(output_file))
        
        print(f"\n✅ SUCCESS! QTI zip file ready for Canvas import:")
        print(f"   📁 {output_file}")
        print(f"   📝 {len(all_questions)} questions from {len(document_files)} exam files")
        
        print(f"\n🎯 Canvas Import Instructions:")
        print("1. Go to your Canvas course")
        print("2. Navigate to Quizzes")
        print("3. Click 'Import Quiz'")
        print("4. Select 'QTI .zip file'")
        print("5. Upload the generated .zip file")
        print("6. Review and publish your quiz")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        
    finally:
        # Cleanup temporary files
        print(f"\n🧹 Cleaning up...")
        s3_manager.cleanup_temp_files()


if __name__ == "__main__":
    main()