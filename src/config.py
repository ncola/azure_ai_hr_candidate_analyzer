"""
Configuration Module for HR CV Analyzer Project
Azure Document Intelligence & OpenAI Integration

This module handles:
- Environment variables loading
- Azure credentials management
- Client initialization
- Configuration validation
"""

import os
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()


class AzureConfig:
    """
    Centralized configuration for Azure Document Intelligence & OpenAI
    """
    
    # Azure Document Intelligence Configuration
    DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    DOCUMENT_INTELLIGENCE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    # Azure OpenAI Configuration
    OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
    
    # Project Configuration
    PROJECT_ROOT = os.getenv('PROJECT_ROOT', '/home/azure_ai_hr_candidate_analyzer')
    DATA_PATH = os.getenv('DATA_PATH', '/home/azure_ai_hr_candidate_analyzer/data')

    @staticmethod
    def validate_document_intelligence_config():
        """Validate Document Intelligence configuration"""
        if not AzureConfig.DOCUMENT_INTELLIGENCE_ENDPOINT or not AzureConfig.DOCUMENT_INTELLIGENCE_KEY:
            raise ValueError(
                "Document Intelligence credentials not found. "
                "Please set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY in .env file."
            )
        
        if not AzureConfig.DOCUMENT_INTELLIGENCE_ENDPOINT.startswith('https://'):
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT must start with https://")
        
        print("Document Intelligence configuration validated")
        return True
    
    @staticmethod
    def validate_openai_config():
        """Validate OpenAI configuration"""
        if not AzureConfig.OPENAI_ENDPOINT or not AzureConfig.OPENAI_KEY:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in .env file."
            )
        
        if not AzureConfig.OPENAI_ENDPOINT.startswith('https://'):
            raise ValueError("AZURE_OPENAI_ENDPOINT must start with https://")
        
        print("Azure OpenAI configuration validated")
        return True
    
    @staticmethod
    def get_document_intelligence_client():
        """
        Initialize and return Document Intelligence client
        
        Returns:
            DocumentIntelligenceClient: Initialized client for Document Intelligence API
        """
        AzureConfig.validate_document_intelligence_config()
        
        credential = AzureKeyCredential(AzureConfig.DOCUMENT_INTELLIGENCE_KEY)
        client = DocumentIntelligenceClient(
            endpoint=AzureConfig.DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=credential
        )
        
        print(f"Document Intelligence client initialized (Endpoint: {AzureConfig.DOCUMENT_INTELLIGENCE_ENDPOINT})")
        return client
    
    @staticmethod
    def get_openai_client():
        """
        Initialize and return Azure OpenAI client
        
        Returns:
            AzureOpenAI: Initialized client for Azure OpenAI API
        """
        AzureConfig.validate_openai_config()
        
        client = AzureOpenAI(
            azure_endpoint=AzureConfig.OPENAI_ENDPOINT,
            api_key=AzureConfig.OPENAI_KEY,
            api_version=AzureConfig.OPENAI_API_VERSION
        )
        
        print(f"Azure OpenAI client initialized (Deployment: {AzureConfig.OPENAI_DEPLOYMENT_NAME})")
        return client


class GPTConfig:
    """GPT parsing configuration"""
    
    # Default temperature for parsing tasks
    TEMPERATURE = 0.0  # Low temperature for consistent parsing
    
    # Maximum tokens for parsing response
    MAX_TOKENS = 2000
    
    # System prompt for CV parsing
    SYSTEM_PROMPT = """You are an expert HR assistant that extracts structured data from CV document.
Extract the following information from the JSON with raw data and return it as a clean JSON object:

{
  "personal_info": {
    "name": "Full name",
    "email": "email@example.com", 
    "phone": "phone number",
    "linkedin": "LinkedIn URL or null"
  },
  "experience": [
    {
      "position": "Job title",
      "company": "Company name",
      "start_date": "Start date",
      "end_date": "End date or Current",
      "description": "Brief description of responsibilities",
      "technologies": ["tech1", "tech2"]
    }
  ],
  "education": [
    {
      "degree": "Degree type",
      "field_of_study": "Field of study", 
      "institution": "University/School name",
      "graduation_year": "Year or null",
      "gpa": "GPA or null"
    }
  ],
  "skills": ["skill1", "skill2", "skill3"]
}

Return only the JSON object, no additional text."""


class GPTMatcherConfig:
    """GPT configuration for CV-job matching"""
    
    # Temperature for matching tasks
    TEMPERATURE = 0.0  # Very low temperature for consistent ranking
    
    # Maximum tokens for matching response
    MAX_TOKENS = 2000
    
    # System prompt for CV-job matching
    SYSTEM_PROMPT = """You are an AI HR assistant that compares job descriptions with multiple candidate CVs.
You MUST return output strictly as JSON, compact, with no explanations, markdown, or formatting.

Focus ONLY on the skills section. For each CV:
- matched_skills: skills literally present both in the CV and required by the job
- missing_skills: skills required by the job but not present in CV

Only consider skills literally listed in the job offer and in the candidate's CV, without any additional or assumed skills.

Sort candidates by score descending and return ONLY the top 3 candidates. The best candidate is the one that matches the most required skills.

Return JSON strictly in this structure:

{
  "top_3": [
    {
      "candidate_id": "candidate number",
      "matched_skills": ["skill1", "skill2"],
      "missing_skills": ["skill3"]
    }
  ]
}"""


# Utility functions
def check_configuration():
    """Check if all required configuration is present"""
    print("\n=== HR CV Analyzer Configuration Check ===\n")
    
    print("1. Azure Document Intelligence Configuration:")
    try:
        AzureConfig.validate_document_intelligence_config()
    except ValueError as e:
        print(f"   Error: {e}")
        return False
    
    print("\n2. Azure OpenAI Configuration:")
    try:
        AzureConfig.validate_openai_config()
    except ValueError as e:
        print(f"   Error: {e}")
        return False
    
    print("\n=== All configurations valid ===\n")
    return True
