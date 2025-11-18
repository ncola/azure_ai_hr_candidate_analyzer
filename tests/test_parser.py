from gpt_cv_parser import GPTCVParser

def test_parse_cv_valid_json():
    parser = GPTCVParser()
    result = parser.parse_cv_with_gpt(MOCK_AZURE_DATA)
    assert "personal_info" in result
    assert result["personal_info"]["name"] is not None
 
def test_parse_cv_malformed_json():
    parser = GPTCVParser()
    # Mock GPT zwracający invalid JSON
    result = parser.parse_cv_with_gpt(MOCK_BAD_DATA)
    assert result == parser._create_empty_cv_structure()
 
