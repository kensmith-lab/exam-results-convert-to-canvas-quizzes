#!/usr/bin/env python3
"""
Canvas QTI Quiz Generator - Interactive Menu
Main entry point for the Replit environment
"""

import os
import sys
import subprocess

def print_header():
    print("\n" + "="*60)
    print("📚 Canvas QTI Quiz Generator".center(60))
    print("="*60)

def print_menu():
    print("\n🚀 Available Modes:\n")
    print("1. 📁 Local Files Mode")
    print("   Process documents from the 'documents/' folder")
    print()
    print("2. 🌐 S3 Bucket Mode")
    print("   Process exam documents from an S3 bucket")
    print()
    print("3. ⭐ Enhanced Multi-Format Mode (Recommended)")
    print("   Process entire folder structures with all formats")
    print()
    print("4. 📖 View README")
    print()
    print("5. 🚪 Exit")

def run_local_mode():
    print("\n🔄 Running Local Files Mode...")
    print("-" * 60)
    subprocess.run(["python3", "generate_qti.py"])

def run_s3_mode():
    if not os.path.exists(".env"):
        print("\n⚠️  S3 mode requires configuration!")
        print("\nTo use S3 mode:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your S3 credentials")
        print("3. Run this option again")
        return
    
    print("\n🔄 Running S3 Mode...")
    print("-" * 60)
    subprocess.run(["python3", "generate_qti_s3.py"])

def run_enhanced_mode():
    print("\n🔄 Running Enhanced Multi-Format Mode...")
    print("-" * 60)
    folder_path = input("\nEnter folder path (or press Enter for 'documents/'): ").strip()
    
    if folder_path:
        subprocess.run(["python3", "generate_qti_enhanced.py", folder_path])
    else:
        subprocess.run(["python3", "generate_qti_enhanced.py"])

def view_readme():
    print("\n📖 README Contents:")
    print("-" * 60)
    with open("README.md", "r") as f:
        print(f.read())
    print("-" * 60)
    input("\nPress Enter to continue...")

def main():
    while True:
        print_header()
        print_menu()
        
        choice = input("\n👉 Select an option (1-5): ").strip()
        
        if choice == "1":
            run_local_mode()
        elif choice == "2":
            run_s3_mode()
        elif choice == "3":
            run_enhanced_mode()
        elif choice == "4":
            view_readme()
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please select 1-5.")
        
        input("\n✅ Press Enter to return to menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
