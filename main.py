#!/usr/bin/env python3
"""
Canvas QTI Quiz Generator - Enhanced Interactive Interface
Main entry point with comprehensive features and validation
"""

import os
import sys
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

try:
    from utils import (
        Color, Validator, Logger, QuestionValidator, 
        Statistics, print_banner, confirm_action
    )
    from config import Config, S3Config
except ImportError:
    print("Installing utils and config modules...")
    Color = type('Color', (), {'RED': '', 'GREEN': '', 'CYAN': '', 'YELLOW': '', 'BOLD': '', 'END': ''})()


class CanvasQTIGenerator:
    """Main application controller"""
    
    def __init__(self):
        self.logger = Logger(log_file=str(Config.get_log_dir() / f"qti_gen_{datetime.now().strftime('%Y%m%d')}.log"))
        self.stats = Statistics()
    
    def print_header(self):
        """Print application header"""
        print_banner("📚 Canvas QTI Quiz Generator - Enhanced Edition")
        print(f"{Color.CYAN}Version 2.0 - With Validation & Statistics{Color.END}\n")
    
    def print_menu(self):
        """Print main menu"""
        print(f"\n{Color.BOLD}🚀 Available Modes:{Color.END}\n")
        print(f"{Color.GREEN}1.{Color.END} 📁 Local Files Mode")
        print(f"   {Color.CYAN}Process documents from the 'documents/' folder{Color.END}")
        print()
        print(f"{Color.GREEN}2.{Color.END} 🌐 S3 Bucket Mode")
        print(f"   {Color.CYAN}Process exam documents from an AWS S3 bucket{Color.END}")
        print()
        print(f"{Color.GREEN}3.{Color.END} ⭐ Enhanced Multi-Format Mode (Recommended)")
        print(f"   {Color.CYAN}Process folder structures with comprehensive validation{Color.END}")
        print()
        print(f"{Color.GREEN}4.{Color.END} 📊 Preview Generated QTI Files")
        print(f"   {Color.CYAN}Inspect and validate existing QTI zip files{Color.END}")
        print()
        print(f"{Color.GREEN}5.{Color.END} 🧹 Cleanup Old Files")
        print(f"   {Color.CYAN}Remove old generated files and logs{Color.END}")
        print()
        print(f"{Color.GREEN}6.{Color.END} 📖 View README")
        print()
        print(f"{Color.GREEN}7.{Color.END} ℹ️  System Info & Configuration")
        print()
        print(f"{Color.GREEN}8.{Color.END} 🚪 Exit")
    
    def run_local_mode(self):
        """Run local files mode with validation"""
        print_banner("📁 Local Files Mode")
        
        docs_dir = str(Config.get_documents_dir())
        is_valid, msg = Validator.validate_folder_path(docs_dir)
        
        if not is_valid:
            self.logger.error(msg)
            return
        
        self.logger.info(f"Processing documents from: {docs_dir}")
        
        doc_files = list(Path(docs_dir).glob("*"))
        supported_files = [f for f in doc_files if f.suffix.lower() in Config.SUPPORTED_FORMATS]
        
        if not supported_files:
            self.logger.warning(f"No supported files found in {docs_dir}")
            self.logger.info(f"Supported formats: {Config.get_supported_format_display()}")
            return
        
        self.logger.info(f"Found {len(supported_files)} supported files")
        
        if confirm_action("Proceed with processing?"):
            print()
            subprocess.run(["python3", "generate_qti.py"])
        else:
            self.logger.info("Cancelled by user")
    
    def run_s3_mode(self):
        """Run S3 mode with configuration validation"""
        print_banner("🌐 S3 Bucket Mode")
        
        if not os.path.exists(".env"):
            self.logger.error("S3 mode requires configuration!")
            print(f"\n{Color.YELLOW}To use S3 mode:{Color.END}")
            print("1. Copy .env.example to .env")
            print("2. Edit .env with your S3 credentials")
            print("3. Run this option again\n")
            return
        
        if not S3Config.is_configured():
            missing = S3Config.get_missing_vars()
            self.logger.error(f"Missing S3 configuration: {', '.join(missing)}")
            return
        
        self.logger.success("S3 configuration validated")
        
        if confirm_action("Proceed with S3 processing?"):
            print()
            subprocess.run(["python3", "generate_qti_s3.py"])
        else:
            self.logger.info("Cancelled by user")
    
    def run_enhanced_mode(self):
        """Run enhanced mode with full validation"""
        print_banner("⭐ Enhanced Multi-Format Mode")
        
        print(f"{Color.CYAN}Supported formats:{Color.END} {Config.get_supported_format_display()}\n")
        
        folder_path = input(f"{Color.YELLOW}Enter folder path (or press Enter for 'documents/'): {Color.END}").strip()
        
        if not folder_path:
            folder_path = str(Config.get_documents_dir())
        
        is_valid, msg = Validator.validate_folder_path(folder_path)
        
        if not is_valid:
            self.logger.error(msg)
            return
        
        self.logger.success(f"Folder validated: {folder_path}")
        
        file_count = sum(1 for _ in Path(folder_path).rglob("*") if _.is_file() and _.suffix.lower() in Config.SUPPORTED_FORMATS)
        
        if file_count == 0:
            self.logger.warning("No supported files found in folder")
            return
        
        self.logger.info(f"Found {file_count} files to process")
        
        if confirm_action("Proceed with enhanced processing?"):
            print()
            subprocess.run(["python3", "generate_qti_enhanced.py", folder_path])
        else:
            self.logger.info("Cancelled by user")
    
    def preview_qti_files(self):
        """Preview and validate generated QTI files"""
        print_banner("📊 QTI File Preview & Validation")
        
        output_dir = Config.get_output_dir()
        qti_files = list(output_dir.glob("*.zip"))
        
        if not qti_files:
            self.logger.warning(f"No QTI files found in {output_dir}")
            return
        
        print(f"{Color.CYAN}Found {len(qti_files)} QTI file(s):{Color.END}\n")
        
        for i, qti_file in enumerate(sorted(qti_files, key=lambda x: x.stat().st_mtime, reverse=True), 1):
            file_size = qti_file.stat().st_size / 1024
            file_time = datetime.fromtimestamp(qti_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{Color.GREEN}{i}.{Color.END} {qti_file.name}")
            print(f"   Size: {file_size:.1f} KB | Created: {file_time}")
            
            try:
                with zipfile.ZipFile(qti_file, 'r') as zf:
                    file_list = zf.namelist()
                    print(f"   Contains: {len(file_list)} files")
                    
                    xml_files = [f for f in file_list if f.endswith('.xml')]
                    if xml_files:
                        print(f"   {Color.CYAN}✓ Valid QTI structure{Color.END}")
                    else:
                        print(f"   {Color.YELLOW}⚠ No XML files found{Color.END}")
            except Exception as e:
                print(f"   {Color.RED}✗ Error reading file: {e}{Color.END}")
            print()
        
        choice = input(f"{Color.YELLOW}Enter file number to inspect (or press Enter to skip): {Color.END}").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(qti_files):
            selected_file = sorted(qti_files, key=lambda x: x.stat().st_mtime, reverse=True)[int(choice)-1]
            self._inspect_qti_file(selected_file)
    
    def _inspect_qti_file(self, file_path: Path):
        """Detailed inspection of QTI file"""
        print(f"\n{Color.BOLD}Inspecting: {file_path.name}{Color.END}\n")
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                print(f"{Color.CYAN}File Contents:{Color.END}")
                for name in sorted(zf.namelist()):
                    file_info = zf.getinfo(name)
                    print(f"  • {name} ({file_info.file_size} bytes)")
                
                manifest = [f for f in zf.namelist() if 'manifest' in f.lower()]
                if manifest:
                    print(f"\n{Color.CYAN}Manifest:{Color.END}")
                    with zf.open(manifest[0]) as f:
                        content = f.read().decode('utf-8')
                        lines = content.split('\n')[:15]
                        for line in lines:
                            if line.strip():
                                print(f"  {line}")
                        total_lines = len(content.split('\n'))
                        if total_lines > 15:
                            print(f"  ... ({total_lines - 15} more lines)")
        except Exception as e:
            self.logger.error(f"Error inspecting file: {e}")
    
    def cleanup_old_files(self):
        """Clean up old generated files and logs"""
        print_banner("🧹 Cleanup Old Files")
        
        output_dir = Config.get_output_dir()
        log_dir = Config.get_log_dir()
        
        qti_files = list(output_dir.glob("*.zip"))
        log_files = list(log_dir.glob("*.log"))
        
        print(f"{Color.CYAN}Files to clean:{Color.END}")
        print(f"  • QTI files: {len(qti_files)}")
        print(f"  • Log files: {len(log_files)}")
        
        if len(qti_files) == 0 and len(log_files) == 0:
            self.logger.info("Nothing to clean")
            return
        
        print(f"\n{Color.YELLOW}Options:{Color.END}")
        print("1. Keep last 5 QTI files, remove older")
        print("2. Keep last 10 QTI files, remove older")
        print("3. Remove all QTI files")
        print("4. Remove all log files")
        print("5. Remove everything")
        print("6. Cancel")
        
        choice = input(f"\n{Color.YELLOW}Select option (1-6): {Color.END}").strip()
        
        removed_count = 0
        
        if choice == "1":
            sorted_files = sorted(qti_files, key=lambda x: x.stat().st_mtime, reverse=True)
            for f in sorted_files[5:]:
                f.unlink()
                removed_count += 1
            self.logger.success(f"Removed {removed_count} old QTI files, kept last 5")
        
        elif choice == "2":
            sorted_files = sorted(qti_files, key=lambda x: x.stat().st_mtime, reverse=True)
            for f in sorted_files[10:]:
                f.unlink()
                removed_count += 1
            self.logger.success(f"Removed {removed_count} old QTI files, kept last 10")
        
        elif choice == "3":
            for f in qti_files:
                f.unlink()
                removed_count += 1
            self.logger.success(f"Removed all {removed_count} QTI files")
        
        elif choice == "4":
            for f in log_files:
                f.unlink()
                removed_count += 1
            self.logger.success(f"Removed all {removed_count} log files")
        
        elif choice == "5":
            if confirm_action(f"{Color.RED}Remove ALL files? This cannot be undone!{Color.END}"):
                for f in qti_files + log_files:
                    f.unlink()
                    removed_count += 1
                self.logger.success(f"Removed all {removed_count} files")
        
        elif choice == "6":
            self.logger.info("Cleanup cancelled")
        else:
            self.logger.error("Invalid choice")
    
    def view_readme(self):
        """View README with paging"""
        print_banner("📖 README")
        
        try:
            with open("README.md", "r") as f:
                lines = f.readlines()
                
            page_size = 30
            for i in range(0, len(lines), page_size):
                page = lines[i:i+page_size]
                for line in page:
                    print(line, end='')
                
                if i + page_size < len(lines):
                    cont = input(f"\n{Color.YELLOW}[Press Enter for more, 'q' to quit]{Color.END} ").strip().lower()
                    if cont == 'q':
                        break
                    print()
        except Exception as e:
            self.logger.error(f"Error reading README: {e}")
    
    def show_system_info(self):
        """Display system information and configuration"""
        print_banner("ℹ️  System Info & Configuration")
        
        print(f"{Color.BOLD}Directories:{Color.END}")
        print(f"  • Documents: {Config.get_documents_dir()}")
        print(f"  • Output: {Config.get_output_dir()}")
        print(f"  • Logs: {Config.get_log_dir()}")
        
        print(f"\n{Color.BOLD}Supported Formats:{Color.END}")
        print(f"  {Config.get_supported_format_display()}")
        
        print(f"\n{Color.BOLD}Configuration:{Color.END}")
        print(f"  • Max file size: {Config.MAX_FILE_SIZE_MB} MB")
        print(f"  • Min choices per question: {Config.MIN_CHOICES}")
        print(f"  • Max choices per question: {Config.MAX_CHOICES}")
        print(f"  • QTI Version: {Config.QTI_VERSION}")
        
        print(f"\n{Color.BOLD}S3 Configuration:{Color.END}")
        if S3Config.is_configured():
            print(f"  {Color.GREEN}✓ Configured{Color.END}")
            print(f"  • Bucket: {os.getenv(S3Config.BUCKET_NAME_ENV, 'N/A')}")
            print(f"  • Region: {os.getenv(S3Config.REGION_ENV, S3Config.DEFAULT_REGION)}")
        else:
            print(f"  {Color.YELLOW}✗ Not configured{Color.END}")
            missing = S3Config.get_missing_vars()
            if missing:
                print(f"  • Missing: {', '.join(missing)}")
        
        print(f"\n{Color.BOLD}File Statistics:{Color.END}")
        output_files = list(Config.get_output_dir().glob("*.zip"))
        doc_files = list(Config.get_documents_dir().glob("*"))
        supported_docs = [f for f in doc_files if f.suffix.lower() in Config.SUPPORTED_FORMATS]
        
        print(f"  • Generated QTI files: {len(output_files)}")
        print(f"  • Documents ready: {len(supported_docs)}")
        print(f"  • Total document files: {len(doc_files)}")
        
        print()
    
    def run(self):
        """Main application loop"""
        try:
            while True:
                self.print_header()
                self.print_menu()
                
                choice = input(f"\n{Color.YELLOW}👉 Select an option (1-8): {Color.END}").strip()
                print()
                
                if choice == "1":
                    self.run_local_mode()
                elif choice == "2":
                    self.run_s3_mode()
                elif choice == "3":
                    self.run_enhanced_mode()
                elif choice == "4":
                    self.preview_qti_files()
                elif choice == "5":
                    self.cleanup_old_files()
                elif choice == "6":
                    self.view_readme()
                elif choice == "7":
                    self.show_system_info()
                elif choice == "8":
                    print(f"{Color.GREEN}👋 Thank you for using Canvas QTI Generator!{Color.END}\n")
                    sys.exit(0)
                else:
                    self.logger.error("Invalid choice. Please select 1-8.")
                
                input(f"\n{Color.CYAN}✅ Press Enter to return to menu...{Color.END}")
                print("\n" * 2)
        
        except KeyboardInterrupt:
            print(f"\n\n{Color.GREEN}👋 Goodbye!{Color.END}\n")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    app = CanvasQTIGenerator()
    app.run()
