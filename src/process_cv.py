#!/usr/bin/env python3
"""
Main CV processing script
Combines Azure Document Intelligence + GPT-4o parsing

Usage: python process_cv.py <path_to_cv.pdf>
Output: data/results/<cv_name>_parsed_data.json
"""

import sys
import os

# Import our modules
from cv_reader_simple import process_cv_to_raw_json
from gpt_cv_parser import parse_raw_json_with_gpt


def process_cv_complete(cv_file_path: str) -> str:
    """
    Complete CV processing from PDF to parsed JSON
    
    Args:
        cv_file_path: Path to PDF file with CV
        
    Returns:
        str: Path to final parsed JSON file in data/results/
    """
    
    print("Starting CV processing...")
    print(f"Input file: {cv_file_path}")
    
    # Step 1: Azure Document Intelligence - extract raw data
    print("\nSTEP 1: Extracting raw data from Azure Document Intelligence")
    try:
        raw_json_path = process_cv_to_raw_json(cv_file_path)
        print(f"Raw data ready: {raw_json_path}")
    except Exception as e:
        print(f"Error in step 1: {e}")
        raise
    
    # Step 2: GPT-4o - parse data to structure
    print("\nSTEP 2: Parsing with GPT-4o")
    try:
        parsed_json_path = parse_raw_json_with_gpt(raw_json_path)
        print(f"Parsed data ready: {parsed_json_path}")
    except Exception as e:
        print(f"Error in step 2: {e}")
        raise
    
    print(f"\nDONE! Final file: {parsed_json_path}")
    
    return parsed_json_path


def main():
    """Main script function"""
    
    print("=" * 60)
    print("HR CV ANALYZER - Complete CV Processing")
    print("=" * 60)
    
    # Check arguments
    if len(sys.argv) != 2:
        print("\nIncorrect arguments!")
        print("\nUsage:")
        print("  python process_cv.py <path_to_cv.pdf>")
        print("\nExamples:")
        print("  python process_cv.py john_doe_cv.pdf")
        print("  python process_cv.py /path/to/candidate_cv.pdf")
        print("\nOutput:")
        print("  data/results/<cv_name>_parsed_data.json - fully parsed CV")
        sys.exit(1)
    
    cv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(cv_file):
        print(f"File does not exist: {cv_file}")
        sys.exit(1)
    
    # Check extension
    if not cv_file.lower().endswith('.pdf'):
        print(f"Only PDF files are supported. Received: {cv_file}")
        print("If you have a DOC/DOCX file, convert it to PDF first")
        sys.exit(1)
    
    try:
        # Process CV
        final_json = process_cv_complete(cv_file)
        
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Input file: {cv_file}")
        print(f"Output file: {final_json}")
        print("\nYou can now use this JSON for further analysis!")
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("\nCheck:")
        print("  1. Are Azure keys configured in .env")
        print("  2. Is the PDF file readable")
        print("  3. Do you have internet connection")
        sys.exit(1)


if __name__ == "__main__":
    main()
