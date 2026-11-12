import re
import os
import json
from typing import Dict, List, Set, Any

class TextPreprocessor:
    """
    NLP Preprocessing Engine:
    - Lowercasing
    - Pembersihan Simbol / Punctuation
    - Kamus Normalisasi Slang & Istilah Sepak Bola Indonesia
    - Sastrawi Stemming (aman terhadap empty string, typo, & slang ekstrem)
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GLOSSARY_PATH = os.path.join(BASE_DIR, "data", "knowledge_base", "glossary.json")

    # Kamus ekstensif normalisasi slang & variasi ejaan bahasa sepak bola Indonesia
    SLANG_DICTIONARY = {
        # Offside
        "ofsai": "offside",
        "ofside": "offside",
        "ofset": "offside",
        "off-side": "offside",
        "off side": "offside",
        "onside": "onside",
        "on-side": "onside",
        "on side": "onside",
        "mendahului bek": "offside",
        "dibelakang bek": "offside",
        "di belakang bek": "offside",

        # Handball & Posisi Tangan
        "hansbal": "handball",
        "handsbal": "handball",
        "handsball": "handball",
        "hand-ball": "handball",
        "hands": "handball",
        "hand": "handball",
        "kena tangan": "handball",
        "terkena tangan": "handball",
        "kesentuh tangan": "handball",
        "bola kena tangan": "handball",
        "kena lengan": "handball",
        "terkena lengan": "handball",
        "sentuh tangan": "handball",
        "nempel": "tempel",
        "menempel": "tempel",
        "rapat": "tempel",
        "tangan nempel": "tangan tempel",
        "melebar": "lebar",
        "membentang": "lebar",
        "kebuka": "lebar",
        "terbuka": "lebar",
        "bentang": "lebar",
        "terangkat": "lebar",
        "angkat tangan": "lebar",
        "memperbesar tubuh": "lebar",
        "memperbesar badan": "lebar",
        "tangan aktif": "tangan aktif",

        # Penalti
        "pinalti": "penalty",
        "penalti": "penalty",
        "penalty kick": "penalty",
        "titik putih": "penalty",
        "kotak 16": "kotak penalti",
        "nyelonong masuk": "encroachment",
        "nyelonong": "encroachment",
        "masuk kotak duluan": "encroachment",
        "masuk duluan": "encroachment",
        "menerobos": "encroachment",
        "diulang": "ulang",
        "tos tosan": "adu penalti",
        "tos-tosan": "adu penalti",

        # Aksi Pemain & Bola
        "ditarik": "tarik",
        "narik": "tarik",
        "tarik baju": "spa tarik baju",
        "tarik jersey": "spa tarik baju",
        "ditepis": "tepis",
        "nepis": "tepis",
        "umpan": "oper",
        "ngoper": "oper",
        "operan": "oper",
        "passing": "oper",
        "crossing": "umpan silang",
        "krosing": "umpan silang",
        "ngegolin": "gol",
        "bobol": "gol",
        "cetak gol": "gol",
        "goal": "gol",

        # Restart
        "lemparan ke dalam": "lemparan kedalam",
        "lemparan dalam": "lemparan kedalam",
        "throw in": "throw-in",
        "throw-in": "throw-in",
        "throwin": "throw-in",
        "lemparan out": "throw-in",
        "tendangan gawang": "goal kick",
        "goalkick": "goal kick",
        "tendangan sudut": "corner kick",
        "tendangan pojok": "corner kick",
        "sepak pojok": "corner kick",
        "corner": "corner kick",

        # Peran Pemain
        "striker": "penyerang",
        "forward": "penyerang",
        "attacker": "penyerang",
        "ujung tombak": "penyerang",
        "pemain depan": "penyerang",
        "defender": "bek",
        "back": "bek",
        "centre back": "bek",
        "center back": "bek",
        "pemain belakang": "bek",
        "pemain bertahan": "bek",
        "kiper": "kiper",
        "keeper": "kiper",
        "goalkeeper": "kiper",
        "goalie": "kiper",
        "penjaga gawang": "kiper",

        # Pelanggaran & Kartu
        "orang terakhir": "dogso",
        "pemain terakhir": "dogso",
        "ditarik pas mau gol": "dogso",
        "peluang emas": "dogso",
        "kartu merah": "kartu merah",
        "red card": "kartu merah",
        "kartu kuning": "kartu kuning",
        "yellow card": "kartu kuning",
        "dibiarkan main": "advantage",
        "gak ditiup": "advantage",
        "main terus": "advantage",
        "tekel brutal": "excessive force kartu merah",
        "tekel keras": "excessive force kartu merah",
        "cedera kepala": "gegar otak",
        "injury time": "waktu tambahan",
        "tambahan waktu": "waktu tambahan",
        "extra time": "waktu tambahan",
        "clear and obvious": "clear and obvious",

        # Kata umum / Singkatan
        "gak": "tidak",
        "nggak": "tidak",
        "ga": "tidak",
        "enggak": "tidak",
        "kalo": "kalau",
        "gimana": "bagaimana",
        "knp": "kenapa",
        "pas": "saat"
    }

    _stemmer_instance = None
    _glossary_cache = None

    @classmethod
    def get_stemmer(cls):
        """Membuat stemmer Sastrawi dengan penanganan fallback yang aman."""
        if cls._stemmer_instance is None:
            try:
                from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
                factory = StemmerFactory()
                cls._stemmer_instance = factory.create_stemmer()
            except Exception as e:
                print(f"[Warning] Sastrawi gagal diinisialisasi: {e}. Menggunakan fallback stemmer.")
                cls._stemmer_instance = None
        return cls._stemmer_instance

    @classmethod
    def safe_stem_word(cls, word: str) -> str:
        """Melakukan stemming pada satu kata dengan proteksi crash."""
        if not word or not isinstance(word, str):
            return ""
        word = word.strip()
        if len(word) <= 3:
            return word

        stemmer = cls.get_stemmer()
        if stemmer:
            try:
                stemmed = stemmer.stem(word)
                return stemmed if stemmed else word
            except Exception:
                pass

        # Fallback regex stemmer jika Sastrawi gagal atau error
        stemmed = re.sub(r'^(me|men|meng|mem|meny|ber|ter|di|pe|per)', '', word)
        stemmed = re.sub(r'(kan|an|i|nya|lah|kah)$', '', stemmed)
        return stemmed if len(stemmed) >= 3 else word

    @classmethod
    def safe_stem_text(cls, text: str) -> str:
        """Melakukan stemming pada keseluruhan teks dengan proteksi crash."""
        if not text or not isinstance(text, str):
            return ""
        text = text.strip()
        if not text:
            return ""

        stemmer = cls.get_stemmer()
        if stemmer:
            try:
                stemmed = stemmer.stem(text)
                if stemmed:
                    return stemmed
            except Exception:
                pass

        # Token by token fallback
        tokens = text.split()
        return " ".join([cls.safe_stem_word(t) for t in tokens if t])

    @classmethod
    def load_glossary(cls) -> dict:
        """Memuat kamus istilah dari data/knowledge_base/glossary.json."""
        if cls._glossary_cache is not None:
            return cls._glossary_cache
        if os.path.exists(cls.GLOSSARY_PATH):
            try:
                with open(cls.GLOSSARY_PATH, "r", encoding="utf-8") as f:
                    cls._glossary_cache = json.load(f).get("synonyms", {})
                    return cls._glossary_cache
            except Exception:
                pass
        cls._glossary_cache = {}
        return cls._glossary_cache

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Membersihkan tanda baca, symbol, dan menormalkan slang kata sepak bola."""
        if not text or not isinstance(text, str):
            return ""
        
        # 1. Lowercase
        text = text.lower().strip()

        # 2. Hapus karakter simbol non-alfanumerik kecuali strip
        text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # 3. Ganti frasa slang majemuk (diurutkan dari terpanjang ke terpendek)
        sorted_phrases = sorted(cls.SLANG_DICTIONARY.keys(), key=lambda x: len(x), reverse=True)
        for phrase in sorted_phrases:
            if " " in phrase or "-" in phrase:
                pattern = r'(?<!\w)' + re.escape(phrase) + r'(?!\w)'
                text = re.sub(pattern, cls.SLANG_DICTIONARY[phrase], text)

        # 4. Ganti kata slang tunggal
        words = text.split()
        normalized_words = []
        for w in words:
            normalized_words.append(cls.SLANG_DICTIONARY.get(w, w))

        normalized_text = " ".join(normalized_words)
        normalized_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', normalized_text)
        return re.sub(r'\s+', ' ', normalized_text).strip()

    @classmethod
    def preprocess(cls, text: str) -> Dict[str, Any]:
        """
        Pipeline lengkap preprocessing teks query:
        1. Lowercase & symbol cleaning
        2. Slang & typo normalization
        3. Tokenization
        4. Sastrawi stemming pada tiap token dan teks
        """
        if not text or not isinstance(text, str):
            return {
                "raw": "",
                "normalized": "",
                "tokens": [],
                "stemmed_tokens": [],
                "stemmed_text": ""
            }

        raw_clean = text.strip()
        normalized = cls.normalize_text(raw_clean)
        tokens = [t for t in normalized.split() if t]

        # Stemming setiap token secara aman
        stemmed_tokens = []
        for t in tokens:
            st = cls.safe_stem_word(t)
            if st:
                stemmed_tokens.append(st)

        stemmed_text = " ".join(stemmed_tokens)

        return {
            "raw": raw_clean,
            "normalized": normalized,
            "tokens": tokens,
            "stemmed_tokens": stemmed_tokens,
            "stemmed_text": stemmed_text
        }
