# HR CV Analyzer - Instrukcje użycia

System do automatycznej analizy CV przy użyciu Azure Document Intelligence i GPT-4o.

## Quick Start

### 0. Pobranie testowych danych (OPCJONALNE)
```bash
python src/download_dataset.py
```
**Wymaga**: Konto Kaggle i klucze API w `.env`  
**Output**: `data/resume/` - testowe pliki CV do analizy

### 1. Kompletne przetwarzanie CV (REKOMENDOWANE)
```bash
python src/process_cv.py data/resume/candidate_cv.pdf
```
**Output**: `data/results/candidate_cv_parsed_data.json` - gotowe, strukturalne dane CV
**Output**: `data/results/candidate_cv_raw_data.json` - surowe dane z Azure (backup)

### 2. Przetwarzanie krok po kroku

#### Krok 1: Wyciągnij surowe dane z PDF
```bash
python src/cv_reader_simple.py data/resume/candidate_cv.pdf
```
**Output**: `data/results/candidate_cv_raw_data.json` - surowe dane z Azure Document Intelligence

#### Krok 2: Sparsuj dane przez GPT-4o

**Tryb domyślny (czysty tekst)**:
```bash
python src/gpt_cv_parser.py data/results/candidate_cv_raw_data.json
```

**Tryb strukturalny (paragrafy + tabele)**:
```bash
python src/gpt_cv_parser.py data/results/candidate_cv_raw_data.json --structured
```
**Output**: `data/results/candidate_cv_parsed_data.json` - strukturalne dane CV

## 🎛️ Tryby przetwarzania GPT

### Tryb domyślny (czysty tekst)
- Używa tylko surowego tekstu OCR
- Szybszy i prostszy
- Dobry dla standardowych CV

### Tryb strukturalny (--structured)
- Wykorzystuje paragrafy z rolami (sectionHeading, pageFooter, etc.)
- Analizuje tabele z pozycjami komórek
- Uwzględnia pary klucz-wartość
- Lepszy dla złożonych formatów CV

## Wymagania

### Struktura folderów
```
hr_ai_analizer/
├── .gitignore             # Ignorowanie .env i danych
├── src/                    # Kod źródłowy
│   ├── .env               # Konfiguracja Azure (NIE COMMITUJ!)
│   └── *.py               # Pliki Python
├── data/
│   ├── resume/            # Wejściowe pliki PDF (ignorowane przez Git)
│   ├── results/           # Wyniki przetwarzania (ignorowane przez Git)
│   └── job_offers/        # Opisy stanowisk (ignorowane przez Git)
├── venv/                  # Środowisko wirtualne
├── streamlit_app.py       # Frontend                
└── requirements.txt       # Zależności Python
```

### Konfiguracja Azure (.env file)

#### 1. Uzyskanie kluczy Azure

**Azure Document Intelligence:**
1. Zaloguj się do [Azure Portal](https://portal.azure.com)
2. Utworz nową usługę: `+ Create a resource` → `AI + Machine Learning` → `Document Intelligence`
3. Po utworzeniu przejdź do `Keys and Endpoint`
4. Skopiuj `KEY 1` i `Endpoint`

**Azure OpenAI:**
1. W [Azure Portal](https://portal.azure.com) znajdź `Azure OpenAI`
2. Utworz nową usługę OpenAI lub wykorzystaj już utworzoną
3. W sekcji `Model deployments` utwórz deployment modelu `gpt-4o`
4. Po utworzeniu deployment przejdź do `Keys and Endpoint`
5. Skopiuj `KEY 1` i `Endpoint`

#### 2. Konfiguracja pliku .env

Utwórz plik `.env` w folderze `src/`:
```bash
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_api_key_here

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Project configuration
PROJECT_ROOT=/home/user/klasteryzacja/projekt

# Kaggle API (OPCJONALNE - tylko do pobierania testowych danych)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_API_KEY=your_kaggle_api_key
```

#### 3. Pobieranie testowych danych (OPCJONALNE)

System zawiera skrypt do automatycznego pobierania testowych CV z Kaggle:

**Konfiguracja Kaggle API:**
1. Załóż konto na [Kaggle.com](https://www.kaggle.com)
2. Przejdź do [Account settings](https://www.kaggle.com/account)
3. W sekcji "API" kliknij "Create New API Token"
4. Dodaj dane do pliku `.env`:
   ```bash
   KAGGLE_USERNAME=twoj_username
   KAGGLE_API_KEY=twoj_api_key
   ```

**Pobieranie danych:**
```bash
python src/download_dataset.py
```

**Rezultat:**
- Automatycznie pobierze dataset z CV w formacie PDF
- Umieści pliki w `data/resume/` 
- Wyświetli listę pobranych plików
- Gotowe do testowania systemu!

### Instalacja pakietów
```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt
```

## Format danych wyjściowych

```json
{
  "personal_info": {
    "name": "Jan Kowalski",
    "email": "jan.kowalski@email.com",
    "phone": "+48 123 456 789",
    "linkedin": "linkedin.com/in/jan-kowalski"
  },
  "experience": [
    {
      "position": "Senior Software Engineer",
      "company": "Tech Company",
      "start_date": "2020",
      "end_date": "Current",
      "description": "Developing web applications...",
      "technologies": ["Python", "JavaScript", "React"]
    }
  ],
  "education": [
    {
      "degree": "M.S",
      "field_of_study": "Computer Science",
      "institution": "University of Technology",
      "graduation_year": 2019,
      "gpa": "4.5/5.0"
    }
  ],
  "skills": [
    "Python", "JavaScript", "React", "SQL", "Docker"
  ]
}
```

## Testowanie konfiguracji

```bash
python src/test_config.py
```

**Przykładowa komenda po pozytywnym teście**:
```bash
python src/process_cv.py data/resume/your_cv.pdf
```

## Organizacja plików

### Wejściowe
- Umieść pliki PDF w `data/resume/`
- Obsługiwane: tylko pliki PDF

### Wyjściowe (automatycznie w `data/results/`)
- `*_raw_data.json` - surowe dane z Azure Document Intelligence
- `*_parsed_data.json` - sparsowane dane przez GPT-4o (finałowy rezultat)

## Troubleshooting

### Problem: Import errors
**Rozwiązanie**: Uruchom z katalogu głownego projektu i sprawdź czy wszystkie pakiety są zainstalowane:
```bash
cd projekt/
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Problem: Azure authentication errors  
**Rozwiązanie**: Sprawdź klucze API w pliku `src/.env` i uruchom test:
```bash
python src/test_config.py
```

### Problem: GPT parsing errors
**Rozwiązanie**: 
1. Sprawdź czy masz dostęp do GPT-4o deployment w Azure OpenAI
2. Spróbuj trybu domyślnego zamiast --structured
3. Sprawdź czy plik raw_data.json nie jest uszkodzony

### Problem: "Plik nie istnieje"
**Rozwiązanie**: Użyj pełnych ścieżek względem katalogu głownego:
```bash
python src/process_cv.py data/resume/twoj_cv.pdf
# zamiast
python src/process_cv.py twoj_cv.pdf
```

### Problem: Kaggle authentication errors (download_dataset.py)
**Rozwiązanie**: 
1. Sprawdź czy masz konto na Kaggle.com
2. Pobierz API token z Account settings
3. Dodaj KAGGLE_USERNAME i KAGGLE_API_KEY do .env
4. Upewnij się że kaggle jest zainstalowane: `pip install kaggle`

### Problem: Brak plików PDF po download_dataset.py
**Rozwiązanie**:
1. Sprawdź czy dataset został pobrany do właściwego folderu
2. Niektóre datasety mogą mieć inne formaty plików
3. Skonwertuj pliki DOC/DOCX na PDF jeśli to konieczne

### BEZPIECZEŃSTWO: NIE commituj pliku .env!
**Rozwiązanie automatyczne**:
- Plik `.gitignore` jest już skonfigurowany
- Chroni `.env` oraz foldery `data/` przed commitowaniem
- Zachowuje strukturę folderów przez pliki `.gitkeep`


## Setup szybki (5 minut)

1. **Klonuj/pobierz projekt**
2. **Aktywuj venv**: `source venv/bin/activate`
3. **Zainstaluj**: `pip install -r requirements.txt`
4. **Skonfiguruj Azure** (zobacz sekcję wyżej)
5. **Testuj konfigurację**: `python src/test_config.py`
6. **Pobierz testowe dane** (opcjonalne): `python src/download_dataset.py`
7. **Uruchom**: `python src/process_cv.py data/resume/twoj_cv.pdf`

## Use Cases

1. **Przetowrzenie wielu CV**  - jeśli chcemy przetwarzorzyć wiele CV na raz:
   ```bash
   for cv in data/resume/*.pdf; do python src/process_cv.py "$cv"; done
   ```
2. **testowanie różnych trybów** - porównanie trybów domyślnego vs strukturalnego dla różnych typów CV
