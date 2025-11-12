#!/usr/bin/env python3
"""
Dataset downloader for HR CV Analyzer
Downloads resume dataset from Kaggle for testing and development

Requirements:
1. Kaggle account and API key
2. KAGGLE_USERNAME and KAGGLE_API_KEY in .env file

Usage: python src/download_dataset.py
Output: data/resume/ (CV files for testing)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def download_resume_dataset():
    """Download resume dataset from Kaggle"""
    
    print("=" * 60)
    print("HR CV ANALYZER - Dataset Downloader")
    print("=" * 60)
    
    # Check environment variables
    kaggle_username = os.getenv("KAGGLE_USERNAME")
    kaggle_api_key = os.getenv("KAGGLE_KEY")
    
    if not kaggle_username or not kaggle_api_key:
        print("ERROR: Missing Kaggle credentials!")
        print("\nPlease add to your .env file:")
        print("KAGGLE_USERNAME=your_kaggle_username")
        print("KAGGLE_API_KEY=your_kaggle_api_key")
        print("\nTo get your API key:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New API Token'")
        print("4. Add credentials to .env file")
        sys.exit(1)
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("ERROR: Kaggle package not found!")
        print("Please install it: pip install kaggle")
        sys.exit(1)
    
    # Initialize Kaggle API
    print("Initializing Kaggle API...")
    try:
        api = KaggleApi()
        api.authenticate()
        print("Kaggle authentication successful")
    except Exception as e:
        print(f"ERROR: Kaggle authentication failed: {e}")
        print("\nCheck your credentials in .env file")
        sys.exit(1)
    
    # Set dataset and path
    dataset_name = 'snehaanbhawal/resume-dataset'
    output_path = Path('data/resume')
    
    print(f"\nDownloading dataset: {dataset_name}")
    print(f"Output directory: {output_path.resolve()}")
    
    # Create directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download and extract dataset
        print("Downloading files...")
        api.dataset_download_files(dataset_name, path=str(output_path), unzip=True)
        print("Dataset downloaded successfully!")
        
        # List downloaded files
        downloaded_files = list(output_path.rglob('*.pdf'))  # Recursive search
        if downloaded_files:
            print(f"\n✓ Found {len(downloaded_files)} PDF files:")
            for i, file in enumerate(downloaded_files[:5], 1):  # Show first 5 files
                # Show relative path from data/resume
                relative_path = file.relative_to(output_path)
                print(f"  {i}. {relative_path}")
            if len(downloaded_files) > 5:
                print(f"  ... and {len(downloaded_files) - 5} more files")
        else:
            print("No PDF files found in dataset")
            all_files = list(output_path.rglob('*'))  # Recursive search for any files
            if all_files:
                print(f"Found {len(all_files)} other files:")
                for file in all_files[:3]:
                    if file.is_file():  # Only show files, not directories
                        relative_path = file.relative_to(output_path)
                        print(f"  - {relative_path}")
        
        print(f"\n✓ Dataset ready in: {output_path.resolve()}")
        print("\nYou can now test the system with:")
        print("  python src/test_config.py")
        if downloaded_files:
            # Show example with actual first file found
            first_file = downloaded_files[0].relative_to(Path('data'))
            print(f"  python src/process_cv.py data/{first_file}")
        else:
            print("  python src/process_cv.py data/resume/path/to/your_cv.pdf")
        
    except Exception as e:
        print(f"ERROR: Download failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_resume_dataset()