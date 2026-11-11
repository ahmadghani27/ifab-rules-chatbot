football-rules-chatbot/
├── app.py                      # Main entry point (Flask / FastAPI web server)
├── config.py                   # Konfigurasi path & konstanta
├── requirements.txt            # Dependency (Flask, PyPDF2/pdfplumber, NLTK/Sastrawi)
├── README.md                   # Dokumentasi cara instalasi & menjalankan proyek
│
├── data/
│   ├── raw/
│   │   └── laws_of_the_game.pdf
│   ├── processed/
│   │   ├── rules.json
│   │   └── glossary.json
│   └── knowledge_base/
│       ├── offside.json
│       ├── handball.json
│       ├── fouls_cards.json
│       ├── penalty.json
│       ├── var.json
│       ├── time_procedure.json
│       └── glossary.json
│
├── scripts/
│   ├── extract_pdf.py
│   ├── clean_text.py
│   └── build_knowledge.py
│
├── chatbot/
│   ├── __init__.py
│   ├── preprocessing.py         # Stemming, lemmatization, tokenization (Bahasa Indonesia)
│   ├── intent_classifier.py    # Pencocokan intent berbasis aturan / TF-IDF
│   ├── entity_extractor.py     # Ekstraksi kata kunci (misal: "penyerang", "tangan", "kotak penalti")
│   ├── knowledge_retrieval.py   # Membaca data dari JSON knowledge_base
│   ├── response_generator.py   # Merangkai kalimat balasan
│   └── chatbot_engine.py       # Pengendali alur utama (Main Orchestrator)
│
├── rules/                      # Logika Evaluasi Aturan IFAB
│   ├── offside_rules.py
│   ├── handball_rules.py
│   ├── fouls_cards_rules.py
│   ├── penalty_rules.py
│   └── var_rules.py
│
├── tests/                      # Unit Testing untuk memastikan aturan tidak glitch
│   ├── test_offside.py
│   └── test_handball.py
│
├── templates/
│   └── index.html              # Interface chat Web
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── chat.js
    └── images/
        └── football-logo.png