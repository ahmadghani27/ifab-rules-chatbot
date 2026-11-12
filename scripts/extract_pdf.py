import os
import json
import re

# Penentuan Path Otomatis berbasis struktur folder project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DATA_DIR, "rules.json")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Mengekstrak seluruh teks dari satu file PDF menggunakan pdfplumber dengan fallback pypdf."""
    extracted_text = []

    # Coba dengan pdfplumber terlebih dahulu
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
        if extracted_text:
            return "\n".join(extracted_text)
    except Exception as e:
        print(f"    [Notice] pdfplumber fallback ke pypdf untuk {os.path.basename(pdf_path)}: {e}")

    # Fallback ke pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
        return "\n".join(extracted_text)
    except Exception as e:
        print(f"    [Error] Gagal ekstraksi teks dari {pdf_path}: {e}")
        return ""

def clean_extracted_text(text: str) -> str:
    """Pembersihan awal teks mentah hasil ekstraksi."""
    if not text:
        return ""
    # Menghapus spasi berlebih
    text = re.sub(r'[ \t]+', ' ', text)
    # Menghapus perulangan baris kosong berlebih
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def main():
    print("=== Memulai Ekstraksi PDF IFAB Laws of the Game ===")
    
    # Pastikan folder output data/processed/ sudah dibuat
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(RAW_DATA_DIR):
        print(f"[Error] Folder raw tidak ditemukan di: {RAW_DATA_DIR}")
        return

    # Mengambil seluruh file PDF di folder data/raw/
    pdf_files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"[Warning] Tidak ada file PDF ditemukan di {RAW_DATA_DIR}")
        return

    all_rules_data = {}

    for pdf_file in sorted(pdf_files):
        file_key = os.path.splitext(pdf_file)[0]  # Misal: LAW11, VAR_Protocol, Glossary
        pdf_path = os.path.join(RAW_DATA_DIR, pdf_file)
        
        print(f"[Processing] Ekstraksi {pdf_file}...")
        try:
            raw_text = extract_text_from_pdf(pdf_path)
            cleaned_text = clean_extracted_text(raw_text)
            
            all_rules_data[file_key] = {
                "file_name": pdf_file,
                "raw_text": cleaned_text
            }
            print(f"  └─ Selesai. Total Karakter: {len(cleaned_text)}")
        except Exception as e:
            print(f"  └─ [Error] Gagal membaca {pdf_file}: {e}")

    # Simpan hasil gabungan ke data/processed/rules.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_rules_data, f, indent=2, ensure_ascii=False)

    print(f"\n=== Ekstraksi Selesai ===")
    print(f"Hasil ekstraksi berhasil disimpan di: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
