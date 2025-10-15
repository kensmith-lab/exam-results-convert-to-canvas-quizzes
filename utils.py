#!/usr/bin/env python3
"""
Utility functions for Canvas QTI Generator
Provides validation, logging, and helper functions
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_folder_path(path: str) -> Tuple[bool, str]:
        """Validate folder path exists and is accessible"""
        if not path:
            return False, "Path cannot be empty"
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            return False, f"Path does not exist: {path}"
        
        if not path_obj.is_dir():
            return False, f"Path is not a directory: {path}"
        
        if not os.access(path, os.R_OK):
            return False, f"No read permission for: {path}"
        
        return True, "Valid folder path"
    
    @staticmethod
    def validate_output_dir(path: str) -> Tuple[bool, str]:
        """Validate output directory exists and is writable"""
        path_obj = Path(path)
        
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                return True, f"Created output directory: {path}"
            except Exception as e:
                return False, f"Cannot create output directory: {e}"
        
        if not path_obj.is_dir():
            return False, f"Output path is not a directory: {path}"
        
        if not os.access(path, os.W_OK):
            return False, f"No write permission for: {path}"
        
        return True, "Valid output directory"
    
    @staticmethod
    def validate_file_format(file_path: Path, supported_formats: List[str]) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in supported_formats
    
    @staticmethod
    def check_file_permissions(file_path: Path) -> Tuple[bool, str]:
        """Check if file is readable"""
        if not file_path.exists():
            return False, "File does not exist"
        
        if not os.access(file_path, os.R_OK):
            return False, "No read permission"
        
        try:
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False, "File is empty"
            
            if file_size > 100 * 1024 * 1024:
                return False, "File too large (>100MB)"
            
            return True, "File accessible"
        except Exception as e:
            return False, f"Cannot access file: {e}"


class Logger:
    """Enhanced logging with timestamps and colors"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.start_time = datetime.now()
    
    def log(self, message: str, level: str = "INFO", color: str = Color.WHITE):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"{color}[{timestamp}] [{level}] {message}{Color.END}"
        print(formatted_msg)
        
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def success(self, message: str):
        """Log success message"""
        self.log(f"✅ {message}", "SUCCESS", Color.GREEN)
    
    def error(self, message: str):
        """Log error message"""
        self.log(f"❌ {message}", "ERROR", Color.RED)
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(f"⚠️  {message}", "WARNING", Color.YELLOW)
    
    def info(self, message: str):
        """Log info message"""
        self.log(f"ℹ️  {message}", "INFO", Color.CYAN)
    
    def progress(self, current: int, total: int, item: str = ""):
        """Show progress"""
        percent = (current / total * 100) if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current // total) if total > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)
        msg = f"[{bar}] {percent:.1f}% ({current}/{total}) {item}"
        print(f"\r{Color.BLUE}{msg}{Color.END}", end='', flush=True)
        if current == total:
            print()
    
    def elapsed_time(self):
        """Get elapsed time since logger creation"""
        elapsed = datetime.now() - self.start_time
        return f"{elapsed.total_seconds():.2f}s"


class QuestionValidator:
    """Validates question quality and completeness"""
    
    @staticmethod
    def validate_question(question) -> Tuple[bool, List[str]]:
        """Validate a question object"""
        issues = []
        
        if not question.question_text or len(question.question_text.strip()) < 5:
            issues.append("Question text too short or empty")
        
        if len(question.choices) < 2:
            issues.append(f"Need at least 2 choices, found {len(question.choices)}")
        
        if len(question.choices) > 20:
            issues.append(f"Too many choices ({len(question.choices)}), maximum 20")
        
        if not question.correct_answers:
            issues.append("No correct answer specified")
        
        for idx in question.correct_answers:
            if idx < 0 or idx >= len(question.choices):
                issues.append(f"Invalid correct answer index: {idx}")
        
        for i, choice in enumerate(question.choices):
            if not choice or len(choice.strip()) < 1:
                issues.append(f"Choice {i+1} is empty or too short")
        
        if question.question_type not in ['multiple_choice', 'multiple_select']:
            issues.append(f"Invalid question type: {question.question_type}")
        
        if question.question_type == 'multiple_choice' and len(question.correct_answers) > 1:
            issues.append("Multiple choice question cannot have multiple correct answers")
        
        return len(issues) == 0, issues


class Statistics:
    """Track and display statistics"""
    
    def __init__(self):
        self.total_files = 0
        self.processed_files = 0
        self.failed_files = 0
        self.total_questions = 0
        self.valid_questions = 0
        self.invalid_questions = 0
        self.question_types = {'multiple_choice': 0, 'multiple_select': 0}
        self.file_stats = {}
    
    def add_file_result(self, filename: str, questions: int, success: bool = True):
        """Add file processing result"""
        self.total_files += 1
        if success:
            self.processed_files += 1
            self.file_stats[filename] = questions
        else:
            self.failed_files += 1
    
    def add_question(self, question_type: str, valid: bool = True):
        """Add question to statistics"""
        self.total_questions += 1
        if valid:
            self.valid_questions += 1
            if question_type in self.question_types:
                self.question_types[question_type] += 1
        else:
            self.invalid_questions += 1
    
    def print_summary(self):
        """Print statistics summary"""
        print(f"\n{Color.BOLD}{'='*60}{Color.END}")
        print(f"{Color.BOLD}📊 Processing Summary{Color.END}")
        print(f"{Color.BOLD}{'='*60}{Color.END}\n")
        
        print(f"{Color.CYAN}Files:{Color.END}")
        print(f"  • Total files scanned: {self.total_files}")
        print(f"  • {Color.GREEN}Successfully processed: {self.processed_files}{Color.END}")
        if self.failed_files > 0:
            print(f"  • {Color.RED}Failed: {self.failed_files}{Color.END}")
        
        print(f"\n{Color.CYAN}Questions:{Color.END}")
        print(f"  • Total questions found: {self.total_questions}")
        print(f"  • {Color.GREEN}Valid questions: {self.valid_questions}{Color.END}")
        if self.invalid_questions > 0:
            print(f"  • {Color.RED}Invalid questions: {self.invalid_questions}{Color.END}")
        
        print(f"\n{Color.CYAN}Question Types:{Color.END}")
        print(f"  • Multiple Choice: {self.question_types['multiple_choice']}")
        print(f"  • Multiple Select: {self.question_types['multiple_select']}")
        
        if self.file_stats:
            print(f"\n{Color.CYAN}Top Files by Questions:{Color.END}")
            sorted_files = sorted(self.file_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            for filename, count in sorted_files:
                print(f"  • {filename}: {count} questions")
        
        print(f"\n{Color.BOLD}{'='*60}{Color.END}")


def print_banner(text: str):
    """Print a formatted banner"""
    width = 60
    print(f"\n{Color.BOLD}{Color.CYAN}{'='*width}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{text.center(width)}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'='*width}{Color.END}\n")


def confirm_action(message: str) -> bool:
    """Ask user for confirmation"""
    while True:
        response = input(f"{Color.YELLOW}{message} (y/n): {Color.END}").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print(f"{Color.RED}Please enter 'y' or 'n'{Color.END}")
