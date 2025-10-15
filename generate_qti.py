#!/usr/bin/env python3
"""
Canvas QTI Quiz Generator
Converts documents (HTML/PDF) containing multiple-choice and multiple-select questions 
into Canvas LMS importable QTI .zip files
"""

import os
import re
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    from bs4 import BeautifulSoup
    import PyPDF2
    from docx import Document
except ImportError:
    print("Installing required dependencies...")
    os.system("pip install beautifulsoup4 PyPDF2 python-docx lxml")
    from bs4 import BeautifulSoup
    import PyPDF2
    from docx import Document


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
    """Parses documents to extract questions"""
    
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
        
        # Pattern for questions with numbered choices
        question_pattern = r'(?:Question\s*\d*[:.]\s*)?(.*?)\n\s*(?:[A-Za-z]\)|\d+\.|[A-Za-z]\.)\s*(.*?)(?=\n\s*(?:[A-Za-z]\)|\d+\.|[A-Za-z]\.)|\n\s*(?:Question|\n\n|$))'
        
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
    def _extract_question_from_text(text: str) -> Optional[Question]:
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
    def _extract_question_from_block(text: str) -> Optional[Question]:
        """Extract question from HTML block"""
        return DocumentParser._extract_question_from_text(text)


class QTIGenerator:
    """Generates QTI-compliant XML and zip files"""
    
    def __init__(self, quiz_title: str = "Imported Quiz"):
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
            
            print(f"QTI zip file created: {output_path}")
            
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
        interaction_type = "choiceInteraction" if question.question_type == "multiple_choice" else "choiceInteraction"
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


def main():
    """Main function to process documents and generate QTI"""
    
    documents_dir = Path("documents")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    if not documents_dir.exists():
        print(f"Creating {documents_dir} directory...")
        documents_dir.mkdir(exist_ok=True)
        print(f"Please place your HTML/PDF/DOCX files in the '{documents_dir}' directory and run again.")
        return
    
    # Find document files
    document_files = []
    for ext in ['*.html', '*.htm', '*.pdf', '*.docx']:
        document_files.extend(documents_dir.glob(ext))
    
    if not document_files:
        print(f"No documents found in {documents_dir}/")
        print("Supported formats: HTML, PDF, DOCX")
        return
    
    all_questions = []
    
    # Process each document
    for doc_file in document_files:
        print(f"Processing {doc_file.name}...")
        
        try:
            if doc_file.suffix.lower() in ['.html', '.htm']:
                questions = DocumentParser.parse_html(str(doc_file))
            elif doc_file.suffix.lower() == '.pdf':
                questions = DocumentParser.parse_pdf(str(doc_file))
            elif doc_file.suffix.lower() == '.docx':
                questions = DocumentParser.parse_docx(str(doc_file))
            else:
                continue
            
            all_questions.extend(questions)
            print(f"  Found {len(questions)} questions")
            
        except Exception as e:
            print(f"  Error processing {doc_file.name}: {e}")
    
    if not all_questions:
        print("No questions found in any documents.")
        print("\nExpected format:")
        print("Question: What is 2+2?")
        print("A) 3")
        print("B) 4 *")  # * indicates correct answer
        print("C) 5")
        return
    
    print(f"\nTotal questions found: {len(all_questions)}")
    
    # Generate QTI zip
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"canvas_quiz_{timestamp}.zip"
    
    generator = QTIGenerator(f"Quiz Import {timestamp}")
    generator.generate_qti_zip(all_questions, str(output_file))
    
    print(f"\n✅ QTI zip file ready for Canvas import: {output_file}")
    print("\nTo import into Canvas:")
    print("1. Go to your Canvas course")
    print("2. Navigate to Quizzes")
    print("3. Click 'Import Quiz'")
    print("4. Upload the generated .zip file")


if __name__ == "__main__":
    main()