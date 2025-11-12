#!/usr/bin/env python3
"""
Test configuration for HR CV Analyzer
"""

from config import check_configuration, AzureConfig

def main():
    """Test main configuration functionality"""
    
    print("Testing HR CV Analyzer Configuration\n")
    
    # Check configuration
    if not check_configuration():
        print("Configuration test failed!")
        return False
    
    print("Configuration test passed!")
    
    # Test client initialization (without real API calls)
    print("\nTesting client initialization...")
    
    try:
        print("Testing Document Intelligence client...")
        doc_client = AzureConfig.get_document_intelligence_client()
        print("Document Intelligence client OK")
        
        print("Testing OpenAI client...")
        openai_client = AzureConfig.get_openai_client()
        print("OpenAI client OK")
        
        print("\nAll tests passed! System is ready to use.")
        print("\nYou can now run:")
        print("  - python src/cv_reader_simple.py <cv_file.pdf>")
        print("  - python src/gpt_cv_parser.py <raw_data.json>")
        print("  - python src/process_cv.py <cv_file.pdf>")
        return True
        
    except Exception as e:
        print(f"Client initialization failed: {e}")
        print("\nMake sure you have valid Azure credentials in .env file")
        print("\nUpdate .env file with:")
        print("""
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_api_key_here

# Azure OpenAI  
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
        """)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
