# WasitBot: IFAB Football Rules Explanation Chatbot

A deterministic, rule-based (No-LLM) football rules assistant that explains official IFAB Laws of the Game using an optimized NLP pipeline, Sastrawi stemming, hybrid similarity scoring, and dynamic slot filling.

## Overview

WasitBot helps players, coaches, referees, and fans understand football regulations without relying on unpredictable large language models. The system processes natural language queries in Indonesian (including football slang and typos), extracts relevant match conditions, requests clarifications when details are missing, and evaluates decisions deterministically against official IFAB regulations.

## References
- **Offside**: IFAB Law 11  
- **Handball**: IFAB Law 12 
- **Fouls & Misconduct (Pelanggaran & Kartu)**: IFAB Law 12   
- **Penalty Kick (Penalti)**: IFAB Law 14   VAR: IFAB VAR Protocol   
- **Time & Procedures (Waktu & Prosedur)**: IFAB Laws 3, 7, 10

## Getting Started

### Installation

1. Clone or download the repository:
   ```bash
   cd Wasit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Rebuild processed data and knowledge base from source PDFs:
   ```bash
   python scripts/extract_pdf.py
   python scripts/build_knowledge.py
   ```

### Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Running Tests

Run all unit and integration tests with:
```bash
python -m unittest discover -s tests
```

## Project Structure

```text
Wasit/
├── app.py                     # Flask server and API endpoints (/api/chat, /api/reset)
├── requirements.txt           # Python dependencies
├── chat/                      # NLP processing and dialog management
│   ├── intent_classifier.py   # FlexibleRuleFinder with hybrid scoring and startup indexing
│   ├── preprocessing.py       # Slang normalizer, symbol cleaner, and safe Sastrawi stemmer
│   └── chatbot_engine.py      # Conversation session manager and multi-turn slot filler
├── rules/                     # Deterministic IFAB rule evaluation modules
│   ├── offside_rules.py       # Law 11 evaluator
│   ├── handball_rules.py      # Law 12 handball evaluator
│   ├── fouls_cards_rules.py   # Law 12 fouls and misconduct evaluator
│   ├── penalty_rules.py       # Law 14 penalty kick evaluator
│   └── var_rules.py           # VAR protocol evaluator
├── data/
│   ├── raw/                   # Official IFAB Laws of the Game PDF documents
│   ├── processed/             # Extracted raw text (rules.json)
│   └── knowledge_base/        # Structured intent, pattern, slot, and prompt JSON files
├── scripts/
│   ├── extract_pdf.py         # PDF text extractor using pdfplumber/pypdf
│   └── build_knowledge.py     # Generates structured knowledge base JSON files
├── templates/
│   └── index.html             # Web chat UI template
├── static/
│   ├── css/style.css          # Styling and responsive themes
│   └── js/chat.js             # Client-side asynchronous chat controller
└── tests/
    ├── test_all_rules.py      # Unit tests for rule evaluation engines
    └── test_nlp_pipeline.py   # Integration tests for the 14-step NLP pipeline
```
