import json
import os
import sys
from typing import Dict, Any
from pathlib import Path
from config import AzureConfig, GPTConfig

class GPTCVParser:
    """CV Parser using GPT-4o to transform raw Azure data to structural JSON"""
    
    def __init__(self):
        self.config = AzureConfig()
        self.gpt_config = GPTConfig()
        self.client = self.config.get_openai_client()
        self.deployment_name = self.config.OPENAI_DEPLOYMENT_NAME
    
    def parse_cv_with_gpt(self, azure_response: Dict, use_structured_data: bool = False) -> Dict[str, Any]:
        """Uses GPT-4o to parse CV from Azure Document Intelligence response"""
        
        prompt = self._create_parsing_prompt(azure_response, use_structured_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.gpt_config.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.gpt_config.TEMPERATURE,
                max_tokens=self.gpt_config.MAX_TOKENS
            )
            
            # Extract JSON from response
            json_text = response.choices[0].message.content.strip()
            
            # Remove markdown formatting if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            # Parse JSON
            parsed_cv = json.loads(json_text)
            return parsed_cv
            
        except Exception as e:
            print(f"GPT parsing error: {e}")
            return self._create_empty_cv_structure()
    
    def _create_parsing_prompt(self, azure_response: Dict, use_structured_data: bool = False) -> str:
        """Creates prompt for GPT to parse CV"""
        
        if use_structured_data:
            return self._create_structured_prompt(azure_response)
        else:
            return self._create_simple_prompt(azure_response)
    
    def _create_simple_prompt(self, azure_response: Dict) -> str:
        """Creates prompt using only clean OCR text"""
        all_text = azure_response.get('all_text', '')
        
        prompt = f"""
Analyze the CV data from Azure Document Intelligence and extract structural information.

RAW CV DATA (CLEAN TEXT):
{all_text}

Return only valid JSON according to the format defined in the system prompt."""
        
        return prompt
    
    def _create_structured_prompt(self, azure_response: Dict) -> str:
        """Creates prompt using structured Azure data (paragraphs, tables, etc.)"""
        
        # Collect structured data
        paragraphs = azure_response.get('paragraphs', [])
        tables = azure_response.get('tables', [])
        key_value_pairs = azure_response.get('key_value_pairs', [])
        all_text = azure_response.get('all_text', '')
        
        prompt = f"""
Analyze the structured CV data from Azure Document Intelligence and extract information.

PARAGRAPHS (ORDERED):
"""
        
        if paragraphs:
            for i, para in enumerate(paragraphs, 1):
                content = para.get('content', '')
                role = para.get('role', 'unknown')
                prompt += f"{i}. [{role}] {content}\n"
        else:
            prompt += "No paragraphs found\n"
        
        if tables:
            prompt += f"\nTABLES ({len(tables)} found):\n"
            for i, table in enumerate(tables, 1):
                prompt += f"Table {i} ({table.get('row_count', 0)}x{table.get('column_count', 0)}):\n"
                cells = table.get('cells', [])
                if cells:
                    for cell in cells:
                        content = cell.get('content', '')
                        row = cell.get('row_index', 0)
                        col = cell.get('column_index', 0)
                        prompt += f"  [{row},{col}]: {content}\n"
        
        if key_value_pairs:
            prompt += f"\nKEY-VALUE PAIRS ({len(key_value_pairs)} found):\n"
            for kvp in key_value_pairs:
                key = kvp.get('key', 'no key')
                value = kvp.get('value', 'no value')
                prompt += f"  {key}: {value}\n"
        
        prompt += f"""
FULL TEXT (as backup):
{all_text}

Return only valid JSON according to the format defined in the system prompt."""
        
        return prompt
    
    def _create_empty_cv_structure(self) -> Dict[str, Any]:
        """Creates empty CV structure in case of error"""
        return {
            "personal_info": {
                "name": None,
                "email": None, 
                "phone": None,
                "linkedin": None
            },
            "experience": [],
            "education": [],
            "skills": []
        }


def parse_raw_json_with_gpt(json_file_path: str, use_structured_data: bool = False, output_dir: str = "data/results") -> str:
    """
    Parses raw Azure JSON to structured CV JSON
    
    Args:
        json_file_path: Path to JSON file with Azure raw data
        use_structured_data: Whether to use structured data (paragraphs, tables) or just clean text
        output_dir: Output directory (default: data/results)
        
    Returns:
        str: Path to saved parsed JSON file
    """
    
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON file does not exist: {json_file_path}")
    
    # Prepare output filename
    json_path = Path(json_file_path)
    if json_path.stem.endswith('_raw_data'):
        base_name = json_path.stem.replace('_raw_data', '')
    else:
        base_name = json_path.stem
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_file = Path(output_dir) / f"{base_name}_parsed_data.json"
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        azure_data = json.load(f)
    
    print(f"Parsing with GPT-4o... (mode: {'structured' if use_structured_data else 'clean text'})")
    
    parser = GPTCVParser()
    parsed_cv = parser.parse_cv_with_gpt(azure_data, use_structured_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_cv, f, indent=2, ensure_ascii=False)
    
    print(f"Parsed data saved to: {output_file}")
    print(f"Results:")
    print(f"   - Name: {parsed_cv['personal_info'].get('name', 'Not found')}")
    print(f"   - Email: {parsed_cv['personal_info'].get('email', 'Not found')}")
    print(f"   - Work positions: {len(parsed_cv['experience'])}")
    print(f"   - Education: {len(parsed_cv['education'])}")
    print(f"   - Skills: {len(parsed_cv['skills'])}")
    
    return str(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python gpt_cv_parser.py <path_to_raw_data.json> [--structured]")
        print("Example: python gpt_cv_parser.py cv_raw_data.json")
        print("Example: python gpt_cv_parser.py cv_raw_data.json --structured")
        print("\nOptions:")
        print("  without --structured: Uses only clean OCR text (default)")
        print("  --structured: Uses paragraphs, tables and other structured data")
        sys.exit(1)
    
    json_file = sys.argv[1]
    use_structured = len(sys.argv) == 3 and sys.argv[2] == "--structured"
    
    try:
        output_json = parse_raw_json_with_gpt(json_file, use_structured)
        print(f"\nSuccess! Parsed file ready: {output_json}")
    except Exception as e:
        print(f"\nError: {e}")
        print("Check if you have configured Azure OpenAI keys in .env")
        sys.exit(1)
