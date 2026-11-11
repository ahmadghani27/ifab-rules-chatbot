import os
import json

# Setup Path Direktori
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed", "rules.json")
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "data", "knowledge_base")

def create_knowledge_base():
    print("=== Membangun Knowledge Base Chatbot ===")
    
    # Pastikan folder data/knowledge_base/ dibuat
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
    
    if not os.path.exists(PROCESSED_FILE):
        print(f"[Error] File {PROCESSED_FILE} tidak ditemukan. Jalankan extract_pdf.py terlebih dahulu!")
        return

    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)

    # 1. Offside Knowledge (LAW 11)
    offside_kb = {
        "law": "Law 11 - Offside",
        "raw_reference": extracted_data.get("LAW11", {}).get("raw_text", ""),
        "rules": [
            {
                "id": "offside_position",
                "condition": "Pemain berada lebih dekat ke garis gawang lawan daripada bola dan pemain bertahan lawan kedua terakhir.",
                "note": "Berada di posisi offside bukan merupakan pelanggaran."
            },
            {
                "id": "offside_offence",
                "condition": "Pemain di posisi offside terlibat dalam permainan aktif (menyentuh bola, mengganggu lawan, atau mendapat keuntungan pantulan).",
                "sanction": "Indirect Free Kick untuk lawan."
            },
            {
                "id": "offside_exceptions",
                "condition": "Pemain menerima bola langsung dari Throw-in, Goal Kick, atau Corner Kick.",
                "sanction": "Bukan Pelanggaran Offside."
            }
        ]
    }

    # 2. Handball & Fouls Knowledge (LAW 12)
    law12_text = extracted_data.get("LAW12", {}).get("raw_text", "")
    
    handball_kb = {
        "law": "Law 12 - Handball",
        "raw_reference": law12_text,
        "rules": [
            {
                "id": "attacker_handball",
                "condition": "Penyerang menyentuh bola dengan tangan/lengan (meski tidak sengaja) yang langsung menghasilkan gol atau peluang gol.",
                "sanction": "Pelanggaran (Gol Dianulir / Direct Free Kick)."
            },
            {
                "id": "defender_unnatural_hand",
                "condition": "Bek menyentuh bola dengan tangan yang berada di posisi tidak alami (memperbesar ruang tubuh).",
                "sanction": "Pelanggaran (Direct Free Kick / Penalti jika di dalam kotak penalti)."
            },
            {
                "id": "defender_natural_hand",
                "condition": "Bola mengenai tangan bek yang berada di posisi alami dekat tubuh.",
                "sanction": "Bukan Pelanggaran."
            }
        ]
    }

    fouls_cards_kb = {
        "law": "Law 12 - Fouls & Misconduct",
        "raw_reference": law12_text,
        "rules": [
            {
                "id": "dogso",
                "name": "Denial of an Obvious Goal-Scoring Opportunity",
                "condition": "Menggagalkan peluang emas mencetak gol lawan dengan pelanggaran sengaja.",
                "sanction": "Kartu Merah Langsung."
            },
            {
                "id": "spa",
                "name": "Stopping a Promising Attack",
                "condition": "Menghentikan serangan menjanjikan lawan dengan pelanggaran taktis.",
                "sanction": "Kartu Kuning."
            },
            {
                "id": "advantage",
                "name": "Advantage Rule",
                "condition": "Wasit membiarkan permainan berlanjut karena tim yang dilanggar tetap menguasai bola secara menguntungkan.",
                "sanction": "Kartu (jika ada) diberikan saat bola mati."
            }
        ]
    }

    # 3. Penalty Knowledge (LAW 14)
    penalty_kb = {
        "law": "Law 14 - Penalty Kick",
        "raw_reference": extracted_data.get("LAW14", {}).get("raw_text", ""),
        "rules": [
            {
                "id": "goalkeeper_position",
                "condition": "Kiper wajib menapakkan minimal 1 kaki di atas garis gawang saat bola ditendang.",
                "violation_result": "Jika kiper maju lebih dulu dan menepis bola, penalti diulang."
            },
            {
                "id": "encroachment",
                "condition": "Pemain lawan atau rekan penendang menerobos masuk ke kotak penalti sebelum bola ditendang.",
                "violation_result": "Penalti diulang tergantung tim mana yang melanggar dan hasil tendangan."
            }
        ]
    }

    # 4. VAR Protocol Knowledge
    var_kb = {
        "protocol": "VAR Protocol",
        "raw_reference": extracted_data.get("VAR_Protocol", {}).get("raw_text", ""),
        "eligible_categories": [
            "Goal / No Goal",
            "Penalty / No Penalty",
            "Direct Red Card",
            "Mistaken Identity"
        ],
        "principle": "Clear and Obvious Error (Kesalahan yang jelas dan nyata)."
    }

    # 5. Glossary / Synonym Dictionary
    glossary_kb = {
        "synonyms": {
            "DOGSO": ["orang terakhir", "pemain terakhir", "ditarik pas mau gol", "peluang emas"],
            "SPA": ["tarik baju", "tackle dari belakang", "potong serangan balik"],
            "Advantage": ["dibiarkan main", "gak ditiup", "main terus", "keuntungan"],
            "Encroachment": ["nyelonong masuk", "masuk kotak penalti duluan"],
            "Handball": ["kena tangan", "tangan aktif", "bola kena lengan"]
        }
    }

    # Daftar Simpan File
    files_to_save = {
        "offside.json": offside_kb,
        "handball.json": handball_kb,
        "fouls_cards.json": fouls_cards_kb,
        "penalty.json": penalty_kb,
        "var.json": var_kb,
        "glossary.json": glossary_kb
    }

    for filename, content in files_to_save.items():
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  └─ Berhasil membuat: data/knowledge_base/{filename}")

    print("\n=== Knowledge Base Berhasil Dibuat ===")

if __name__ == "__main__":
    create_knowledge_base()