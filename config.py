#!/usr/bin/env python3
"""
Configuration management for Canvas QTI Generator
Centralized settings and defaults
"""

import os
from pathlib import Path
from typing import List

class Config:
    """Configuration settings"""
    
    SUPPORTED_FORMATS = ['.html', '.htm', '.pdf', '.docx', '.xlsx', '.xls', '.txt']
    
    DEFAULT_QUIZ_TITLE = "Imported Quiz"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_DOCUMENTS_DIR = "documents"
    DEFAULT_TEMP_DIR = "temp_qti"
    DEFAULT_LOG_DIR = "logs"
    
    MAX_FILE_SIZE_MB = 100
    MIN_QUESTION_LENGTH = 5
    MIN_CHOICES = 2
    MAX_CHOICES = 20
    
    DEFAULT_POINTS_PER_QUESTION = 1
    
    QTI_VERSION = "1.2"
    
    @staticmethod
    def get_output_dir():
        """Get output directory, create if doesn't exist"""
        output_dir = Path(Config.DEFAULT_OUTPUT_DIR)
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    @staticmethod
    def get_documents_dir():
        """Get documents directory, create if doesn't exist"""
        docs_dir = Path(Config.DEFAULT_DOCUMENTS_DIR)
        docs_dir.mkdir(exist_ok=True)
        return docs_dir
    
    @staticmethod
    def get_log_dir():
        """Get logs directory, create if doesn't exist"""
        log_dir = Path(Config.DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    @staticmethod
    def get_supported_format_display():
        """Get human-readable list of supported formats"""
        return ", ".join(Config.SUPPORTED_FORMATS)


class S3Config:
    """S3-specific configuration"""
    
    BUCKET_NAME_ENV = "S3_BUCKET_NAME"
    FOLDER_PREFIX_ENV = "S3_FOLDER_PREFIX"
    ACCESS_KEY_ENV = "AWS_ACCESS_KEY_ID"
    SECRET_KEY_ENV = "AWS_SECRET_ACCESS_KEY"
    REGION_ENV = "AWS_DEFAULT_REGION"
    PROFILE_ENV = "AWS_PROFILE"
    
    DEFAULT_REGION = "us-east-1"
    DEFAULT_TEMP_DIR = "temp_downloads"
    
    @staticmethod
    def is_configured():
        """Check if S3 is properly configured"""
        bucket = os.getenv(S3Config.BUCKET_NAME_ENV)
        has_keys = os.getenv(S3Config.ACCESS_KEY_ENV) and os.getenv(S3Config.SECRET_KEY_ENV)
        has_profile = os.getenv(S3Config.PROFILE_ENV)
        
        return bucket and (has_keys or has_profile)
    
    @staticmethod
    def get_missing_vars():
        """Get list of missing S3 configuration variables"""
        missing = []
        
        if not os.getenv(S3Config.BUCKET_NAME_ENV):
            missing.append(S3Config.BUCKET_NAME_ENV)
        
        has_keys = os.getenv(S3Config.ACCESS_KEY_ENV) and os.getenv(S3Config.SECRET_KEY_ENV)
        has_profile = os.getenv(S3Config.PROFILE_ENV)
        
        if not has_keys and not has_profile:
            missing.append("AWS credentials (either keys or profile)")
        
        return missing
