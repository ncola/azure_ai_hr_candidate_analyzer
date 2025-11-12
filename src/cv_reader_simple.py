"""
Simple CV Reader using Azure Document Intelligence prebuilt model
"""
import sys
import os
import json
from typing import Dict, Any
from pathlib import Path
from config import AzureConfig

class SimpleCVReader:
    def __init__(self):
        self.config = AzureConfig()
        self.client = self.config.get_document_intelligence_client()
    
    def read_cv_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Reads CV from PDF and returns raw data from Azure Document Intelligence
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
            
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        print(f"Analyzing file: {file_path}")
        
        poller = self.client.begin_analyze_document(
            "prebuilt-layout", 
            file_content,
            content_type="application/pdf"
        )
        
        result = poller.result()
        print("Analysis completed!")
        
        return self._extract_raw_data(result)
    
    def _extract_raw_data(self, result) -> Dict[str, Any]:
        """
        Extracts raw data from Azure Document Intelligence response
        """
        data = {
            "pages": [],
            "tables": [],
            "paragraphs": [],
            "key_value_pairs": [],
            "all_text": ""
        }
        
        pages = getattr(result, 'pages', [])
        if pages:
            for page in pages:
                page_data = {
                    "page_number": page.page_number,
                    "lines": []
                }
                
                lines = getattr(page, 'lines', [])
                if lines:
                    for line in lines:
                        page_data["lines"].append({
                            "content": line.content,
                            "bounding_box": getattr(line, 'polygon', None)
                        })
                
                data["pages"].append(page_data)
        
        paragraphs = getattr(result, 'paragraphs', [])
        if paragraphs:
            for paragraph in paragraphs:
                data["paragraphs"].append({
                    "content": paragraph.content,
                    "role": getattr(paragraph, 'role', None)
                })
        
        tables = getattr(result, 'tables', [])
        if tables:
            for table in tables:
                table_data = {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": []
                }
                
                cells = getattr(table, 'cells', [])
                if cells:
                    for cell in cells:
                        table_data["cells"].append({
                            "content": cell.content,
                            "row_index": cell.row_index,
                            "column_index": cell.column_index
                        })
                
                data["tables"].append(table_data)
        
        key_value_pairs = getattr(result, 'key_value_pairs', [])
        if key_value_pairs:
            for kvp in key_value_pairs:
                data["key_value_pairs"].append({
                    "key": kvp.key.content if kvp.key else None,
                    "value": kvp.value.content if kvp.value else None
                })
        
        data["all_text"] = getattr(result, 'content', "")
        
        return data

def process_cv_to_raw_json(cv_file_path: str, output_dir: str = "data/results") -> str:
    """
    Processes CV to raw JSON and saves file
    
    Args:
        cv_file_path: Path to PDF file with CV
        output_dir: Output directory (default data/results)
        
    Returns:
        str: Path to saved JSON file
    """
    reader = SimpleCVReader()
    
    if not os.path.exists(cv_file_path):
        raise FileNotFoundError(f"CV file does not exist: {cv_file_path}")
    
    cv_path = Path(cv_file_path)
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_file = Path(output_dir) / f"{cv_path.stem}_raw_data.json"
    
    try:
        raw_data = reader.read_cv_pdf(cv_file_path)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        print(f"Raw data saved to: {output_file}")
        print(f"Statistics:")
        print(f"   - Pages: {len(raw_data['pages'])}")
        print(f"   - Paragraphs: {len(raw_data['paragraphs'])}")
        print(f"   - Tables: {len(raw_data['tables'])}")
        print(f"   - Text characters: {len(raw_data['all_text'])}")
        
        return str(output_file)
        
    except Exception as e:
        print(f"Processing error: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cv_reader_simple.py <path_to_cv.pdf>")
        print("Example: python cv_reader_simple.py sample_cv.pdf")
        sys.exit(1)
    
    cv_file = sys.argv[1]
    
    try:
        output_json = process_cv_to_raw_json(cv_file)
        print(f"\nSuccess! File ready: {output_json}")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
