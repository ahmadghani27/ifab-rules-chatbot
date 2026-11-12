import os
import json
import difflib
import re
from typing import Dict, List, Tuple, Any, Optional

from chat.preprocessing import TextPreprocessor
from rules.offside_rules import evaluate_offside
from rules.handball_rules import evaluate_handball
from rules.penalty_rules import evaluate_penalty
from rules.var_rules import evaluate_var
from rules.fouls_cards_rules import evaluate_foul_misconduct

class FlexibleRuleFinder:
    """
    Mesin Pencocokan Intent & Knowledge Base IFAB berbasis NLP deterministik (No-LLM):
    1. Pre-tokenisasi pola aturan di memori saat startup.
    2. Menghitung kombinasi skor kemiripan:
       Score = (0.4 * Jaccard Similarity) + (0.3 * Fuzzy SequenceMatcher Ratio) + (0.3 * Pattern Coverage)
    3. Evaluasi ambang batas (Threshold >= 0.45).
    4. Slot Filling & Klarifikasi Dinamis.
    5. Eksekusi Rule Engine IFAB di modul rules/*.py.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    KB_DIR = os.path.join(BASE_DIR, "data", "knowledge_base")

    def __init__(self, kb_dir: Optional[str] = None):
        self.kb_dir = kb_dir or self.KB_DIR
        self.intents: Dict[str, dict] = {}
        self.pretokenized_patterns: List[dict] = []
        
        # Step 4: Pre-tokenisasi pola aturan sekali saja saat server startup
        self._load_and_pretokenize_knowledge_base()

    def _load_and_pretokenize_knowledge_base(self):
        """Memuat semua berkas JSON knowledge base dan melakukan pre-tokenisasi."""
        self.intents.clear()
        self.pretokenized_patterns.clear()

        if not os.path.exists(self.kb_dir):
            print(f"[Warning] Direktori knowledge base tidak ditemukan di: {self.kb_dir}")
            return

        kb_files = [f for f in os.listdir(self.kb_dir) if f.endswith(".json")]

        for filename in kb_files:
            file_path = os.path.join(self.kb_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    intents_list = data.get("intents", [])
                    for item in intents_list:
                        tag = item.get("tag") or item.get("intent")
                        if not tag:
                            continue
                        
                        self.intents[tag] = item
                        patterns = item.get("patterns", [])
                        
                        for p in patterns:
                            # Preprocess pola sekali saja di memori
                            prep = TextPreprocessor.preprocess(p)
                            stemmed_tokens = set(prep["stemmed_tokens"])
                            
                            self.pretokenized_patterns.append({
                                "tag": tag,
                                "raw_pattern": p,
                                "normalized": prep["normalized"],
                                "tokens": prep["tokens"],
                                "stemmed_tokens": stemmed_tokens,
                                "stemmed_text": prep["stemmed_text"],
                                "intent_data": item
                            })
            except Exception as e:
                print(f"[Error] Gagal memuat knowledge base {filename}: {e}")

        print(f"[FlexibleRuleFinder] Pre-tokenisasi selesai: {len(self.intents)} intents, {len(self.pretokenized_patterns)} pola terindeks.")

    def calculate_similarity_score(self, user_stemmed_tokens: set, user_stemmed_text: str, pattern_item: dict) -> float:
        """
        Step 7: Menghitung skor kemiripan gabungan:
        Score = (0.4 * Jaccard Similarity) + (0.3 * Fuzzy SequenceMatcher Ratio) + (0.3 * Pattern Coverage)
        """
        p_tokens = pattern_item["stemmed_tokens"]
        p_text = pattern_item["stemmed_text"]

        # 1. Jaccard Similarity
        intersection = user_stemmed_tokens.intersection(p_tokens)
        union = user_stemmed_tokens.union(p_tokens)
        jaccard = (len(intersection) / len(union)) if union else 0.0

        # 2. Fuzzy SequenceMatcher Ratio (berbasis teks yang sudah distem/dinormalisasi)
        fuzzy_ratio = difflib.SequenceMatcher(None, user_stemmed_text, p_text).ratio()

        # 3. Pattern Coverage (Seberapa banyak token pola yang tercakup dalam input user)
        pattern_coverage = (len(intersection) / len(p_tokens)) if p_tokens else 0.0

        # Formula gabungan
        score = (0.4 * jaccard) + (0.3 * fuzzy_ratio) + (0.3 * pattern_coverage)
        return min(max(score, 0.0), 1.0)

    def find_best_intent(self, user_message: str) -> Tuple[Optional[str], float, Optional[dict]]:
        """
        Step 8: Mencari intent aturan dengan skor tertinggi.
        Mengembalikan: (best_intent_tag, best_score, best_pattern_item)
        """
        prep = TextPreprocessor.preprocess(user_message)
        user_tokens = set(prep["stemmed_tokens"])
        user_text = prep["stemmed_text"]

        if not user_tokens and not user_text:
            return None, 0.0, None

        best_score = 0.0
        best_intent_tag = None
        best_pattern_item = None

        for item in self.pretokenized_patterns:
            score = self.calculate_similarity_score(user_tokens, user_text, item)
            if score > best_score:
                best_score = score
                best_intent_tag = item["tag"]
                best_pattern_item = item

        return best_intent_tag, round(best_score, 4), best_pattern_item

    def extract_slots(self, text: str) -> dict:
        """Ekstraksi entitas / slot nilai dari pesan pengguna."""
        text_lower = text.lower()
        prep = TextPreprocessor.preprocess(text)
        all_words = set(prep["tokens"]).union(set(prep["stemmed_tokens"]))
        all_str = f" {prep['normalized']} "

        slots = {}

        # 1. Peran Pemain
        if any(w in all_words for w in ["penyerang", "striker", "ujung", "tombak", "forward", "attacker"]):
            slots["player_role"] = "attacker"
        elif any(w in all_words for w in ["bek", "bertahan", "defender", "belakang", "stopper"]):
            slots["player_role"] = "defender"
        elif any(w in all_words for w in ["kiper", "penjaga", "gawang", "goalkeeper", "goalie"]):
            slots["player_role"] = "goalkeeper"

        # 2. Posisi Tangan
        if any(w in all_words for w in ["lebar", "melebar", "terangkat", "buka", "bentang", "bahu", "besar"]):
            slots["hand_position"] = "unnatural"
        elif any(w in all_words for w in ["tempel", "menempel", "rapat", "nempel", "wajar", "alami", "natural", "badan", "tumpuan"]):
            slots["hand_position"] = "natural"

        # 3. Hasil Gol
        if any(w in all_words for w in ["gol", "goal", "bobol", "masuk"]):
            if any(neg in all_words for neg in ["tidak", "gagal", "bukan"]):
                slots["is_goal_result"] = False
            else:
                slots["is_goal_result"] = True

        # 4. Jenis Restart (Offside Exceptions)
        if "throw in" in all_str or "lemparan dalam" in all_str or "lemparan" in all_words:
            slots["restart_type"] = "throw_in"
        elif "goal kick" in all_str or "tendangan gawang" in all_str:
            slots["restart_type"] = "goal_kick"
        elif "corner" in all_words or "sepak pojok" in all_str or "tendangan sudut" in all_str:
            slots["restart_type"] = "corner_kick"

        # 5. Posisi Pemain (Offside)
        if any(w in all_words for w in ["posisi offside", "mendahului", "terjebak", "dibelakang", "belakang bek"]):
            slots["player_position"] = "offside_position"
        elif any(w in all_words for w in ["onside", "daerah sendiri", "sejajar"]):
            slots["player_position"] = "onside_position"

        # 6. Aksi Pemain (Offside)
        if any(w in all_words for w in ["pasif", "diam", "diamkan"]):
            slots["action_type"] = "passive"
        elif any(w in all_words for w in ["sentuh", "main", "oper", "tendang", "sambut", "terima"]):
            slots["action_type"] = "touch_ball"
        elif any(w in all_words for w in ["ganggu", "halang", "tutup"]):
            slots["action_type"] = "interfere_opponent"
        elif any(w in all_words for w in ["pantul", "rebound", "untung"]):
            slots["action_type"] = "gain_advantage"

        # 7. Posisi Kaki Kiper (Penalty)
        if any(w in all_words for w in ["maju", "keluar garis", "lewat"]):
            slots["goalkeeper_feet"] = "off_the_line_early"
        elif any(w in all_words for w in ["injak", "garis", "menapak", "tetap"]):
            slots["goalkeeper_feet"] = "on_the_line"

        # 8. Pelanggaran Encroachment (Penalty)
        if any(w in all_words for w in ["penyerang masuk", "teman masuk", "rekan masuk"]):
            slots["encroachment"] = "attacker_entered"
        elif any(w in all_words for w in ["bek masuk", "lawan masuk"]):
            slots["encroachment"] = "defender_entered"
        elif any(w in all_words for w in ["dua tim", "keduanya"]):
            slots["encroachment"] = "both_entered"

        # 9. Kategori VAR
        if any(w in all_words for w in ["gol", "goal"]):
            slots["incident_type"] = "goal"
        elif any(w in all_words for w in ["penalti", "penalty"]):
            slots["incident_type"] = "penalty"
        elif any(w in all_words for w in ["kartu merah", "red card"]):
            slots["incident_type"] = "direct_red_card"
        elif any(w in all_words for w in ["kartu kuning", "yellow card"]):
            slots["incident_type"] = "yellow_card"
        elif any(w in all_words for w in ["salah orang", "salah pemain", "identitas"]):
            slots["incident_type"] = "mistaken_identity"

        # 10. Jenis Pelanggaran & Kartu
        if any(w in all_words for w in ["dogso", "orang terakhir", "peluang emas"]):
            slots["foul_type"] = "dogso"
            slots["is_dogso"] = True
        elif any(w in all_words for w in ["spa", "tarik baju", "serangan balik", "taktis"]):
            slots["foul_type"] = "spa"
            slots["is_spa"] = True
        elif any(w in all_words for w in ["advantage", "keuntungan", "dibiarkan"]):
            slots["foul_type"] = "advantage"
            slots["is_advantage"] = True
        elif any(w in all_words for w in ["brutal", "keras", "bahaya", "injil"]):
            slots["foul_type"] = "excessive_force"
            slots["contact_intensity"] = "excessive_force"

        return slots


class IntentClassifier:
    """
    Kelas kompatibilitas wrapper yang menghubungkan IntentClassifier dengan FlexibleRuleFinder.
    """
    def __init__(self, rule_finder: Optional[FlexibleRuleFinder] = None):
        self.rule_finder = rule_finder or FlexibleRuleFinder()

    def classify(self, text: str) -> str:
        tag, score, _ = self.rule_finder.find_best_intent(text)
        if tag and score >= 0.45:
            # Sederhanakan tag ke kategori dasar jika diperlukan
            if "offside" in tag:
                return "offside"
            elif "handball" in tag:
                return "handball"
            elif "penalty" in tag:
                return "penalty"
            elif "var" in tag:
                return "var"
            elif "fouls" in tag:
                return "fouls_cards"
            elif "glossary" in tag:
                return "glossary"
            return tag
        return "unknown"

    def extract_entities(self, text: str) -> dict:
        return self.rule_finder.extract_slots(text)
