import re

class IntentClassifier:
    def __init__(self):
        # Pemetaan kata kunci untuk intent klasifikasi
        self.intent_patterns = {
            "offside": [
                r"\boffside\b", r"\borang terakhir\b", r"\bgak kena bola\b", 
                r"\blemparan kedalam\b", r"\bgoal kick\b", r"\btendangan gawang\b"
            ],
            "handball": [
                r"\bhandball\b", r"\bkena tangan\b", r"\blengan\b", 
                r"\btangan aktif\b", r"\btangan nempel\b"
            ],
            "var": [
                r"\bvar\b", r"\bcek monitor\b", r"\blihat layar\b", 
                r"\bclear and obvious\b", r"\blayar var\b"
            ],
            "penalty": [
                r"\bpenalti\b", r"\bdiulang\b", r"\bkiper maju\b", 
                r"\bnyelonong\b", r"\bkotak penalti\b"
            ]
        }

    def classify(self, text: str) -> str:
        """Menentukan intent utama berdasarkan teks input pengguna."""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
                    
        return "unknown"

    def extract_entities(self, text: str) -> dict:
        """Mengekstrak entitas kunci dari percakapan pengguna."""
        text_lower = text.lower()
        entities = {}

        # 1. Peran Pemain (Attacker / Defender / Goalkeeper)
        if any(w in text_lower for w in ["penyerang", "striker", "sayap", "depan"]):
            entities["player_role"] = "attacker"
        elif any(w in text_lower for w in ["bek", "defender", "bertahan", "bek tengah"]):
            entities["player_role"] = "defender"
        elif any(w in text_lower for w in ["kiper", "goalkeeper", "penjaga gawang"]):
            entities["player_role"] = "goalkeeper"

        # 2. Posisi Tangan (Handball)
        if any(w in text_lower for w in ["melebar", "terangkat", "lebar", "memperbesar"]):
            entities["hand_position"] = "unnatural"
        elif any(w in text_lower for w in ["nempel", "samping badan", "alami", "natural"]):
            entities["hand_position"] = "natural"

        # 3. Hasil Gol (Handball / Offside Impact)
        if any(w in text_lower for w in ["gol", "masuk gawang", "mencetak gol"]):
            entities["is_goal_result"] = True

        # 4. Pengecualian Restart (Offside)
        if any(w in text_lower for w in ["lemparan ke dalam", "throw in", "throw-in"]):
            entities["restart_type"] = "throw_in"
        elif any(w in text_lower for w in ["tendangan gawang", "goal kick"]):
            entities["restart_type"] = "goal_kick"
        elif any(w in text_lower for w in ["tendangan sudut", "corner kick", "pojok"]):
            entities["restart_type"] = "corner_kick"

        return entities