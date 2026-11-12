import os
import csv
import random
from typing import Dict, Any, Optional, List
from chat.intent_classifier import FlexibleRuleFinder
from rules.offside_rules import evaluate_offside
from rules.handball_rules import evaluate_handball
from rules.penalty_rules import evaluate_penalty
from rules.var_rules import evaluate_var
from rules.fouls_cards_rules import evaluate_foul_misconduct

class ChatbotEngine:
    """
    Manajer Dialog & Pipeline NLP Chatbot Aturan Sepak Bola IFAB:
    Mengimplementasikan 14 tahapan alur pipeline secara deterministik tanpa LLM,
    dilengkapi Response Variation Engine (CSV template & JSON conversational variants).
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_TEMPLATES_PATH = os.path.join(BASE_DIR, "data", "response_templates.csv")

    def __init__(self, rule_finder: Optional[FlexibleRuleFinder] = None):
        # Step 4: Rule finder dengan pre-tokenisasi pola aturan di memori saat startup
        self.rule_finder = rule_finder or FlexibleRuleFinder()
        # Penyimpanan sesi percakapan untuk Slot Filling multi-turn
        self.sessions: Dict[str, dict] = {}
        # Memuat template kalimat variasi dari CSV
        self.csv_templates: Dict[str, List[dict]] = self._load_csv_templates()

    def _load_csv_templates(self) -> Dict[str, List[dict]]:
        """Memuat variasi template kalimat dari data/response_templates.csv."""
        templates = {}
        if os.path.exists(self.CSV_TEMPLATES_PATH):
            try:
                with open(self.CSV_TEMPLATES_PATH, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        intent = row.get("intent", "").strip()
                        if intent:
                            if intent not in templates:
                                templates[intent] = []
                            templates[intent].append(row)
            except Exception as e:
                print(f"[Warning] Gagal memuat response_templates.csv: {e}")
        return templates

    def get_csv_template(self, intent: str, category: Optional[str] = None) -> Optional[str]:
        """Mengambil acak salah satu template kalimat dari CSV sesuai intent/kategori."""
        items = self.csv_templates.get(intent, [])
        if category:
            filtered = [it["template_text"] for it in items if it.get("category") == category]
            if filtered:
                return random.choice(filtered)
        if items:
            return random.choice([it["template_text"] for it in items])
        return None

    def get_or_create_session(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "awaiting_slot": None,
                "current_intent": None,
                "slots": {}
            }
        return self.sessions[session_id]

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id] = {
                "awaiting_slot": None,
                "current_intent": None,
                "slots": {}
            }

    def process_message(self, user_message: str, session_id: str = "default_session") -> dict:
        """
        Menjalankan pipeline pemrosesan pesan dari user:
        Step 6 - Step 14.
        """
        session = self.get_or_create_session(session_id)
        extracted_slots = self.rule_finder.extract_slots(user_message)

        # 1. Pengecekan apakah user sedang menjawab pertanyaan klarifikasi sebelumnya
        awaiting_slot = session.get("awaiting_slot")
        current_intent = session.get("current_intent")

        if awaiting_slot and current_intent:
            # Update slot dari jawaban user
            if awaiting_slot in extracted_slots:
                session["slots"][awaiting_slot] = extracted_slots[awaiting_slot]
            else:
                # Coba deteksi jawaban singkat (angka / kata kunci langsung)
                msg_lower = user_message.lower().strip()
                if awaiting_slot == "hand_position":
                    if any(w in msg_lower for w in ["1", "nempel", "menempel", "rapat", "alami", "wajar"]):
                        session["slots"]["hand_position"] = "natural"
                    elif any(w in msg_lower for w in ["2", "lebar", "melebar", "angkat", "buka", "kebuka"]):
                        session["slots"]["hand_position"] = "unnatural"
                elif awaiting_slot == "player_role":
                    if any(w in msg_lower for w in ["penyerang", "striker", "depan", "forward"]):
                        session["slots"]["player_role"] = "attacker"
                    elif any(w in msg_lower for w in ["bek", "defender", "bertahan", "belakang"]):
                        session["slots"]["player_role"] = "defender"
                    elif any(w in msg_lower for w in ["kiper", "gawang"]):
                        session["slots"]["player_role"] = "goalkeeper"
                elif awaiting_slot == "restart_type":
                    if any(w in msg_lower for w in ["lemparan", "throw in", "throw-in"]):
                        session["slots"]["restart_type"] = "throw_in"
                    elif any(w in msg_lower for w in ["tendangan gawang", "goal kick"]):
                        session["slots"]["restart_type"] = "goal_kick"
                    elif any(w in msg_lower for w in ["sudut", "pojok", "corner"]):
                        session["slots"]["restart_type"] = "corner_kick"
                elif awaiting_slot == "action_type":
                    if any(w in msg_lower for w in ["pasif", "diam"]):
                        session["slots"]["action_type"] = "passive"
                    elif any(w in msg_lower for w in ["aktif", "sentuh", "bola", "main"]):
                        session["slots"]["action_type"] = "touch_ball"
                elif awaiting_slot == "incident_type":
                    if "gol" in msg_lower:
                        session["slots"]["incident_type"] = "goal"
                    elif "penalti" in msg_lower:
                        session["slots"]["incident_type"] = "penalty"
                    elif "merah" in msg_lower:
                        session["slots"]["incident_type"] = "direct_red_card"
                    elif "identitas" in msg_lower or "salah" in msg_lower:
                        session["slots"]["incident_type"] = "mistaken_identity"
                    elif "kuning" in msg_lower:
                        session["slots"]["incident_type"] = "yellow_card"

            # Jika slot yang ditunggu sudah terisi
            if awaiting_slot in session["slots"]:
                session["awaiting_slot"] = None
                intent_data = self.rule_finder.intents.get(current_intent, {})
                return self._check_slots_and_execute(current_intent, intent_data, session, confidence=88)

        # 2. Step 7 & 8: Intent Matching dengan Kombinasi Similarity Score
        best_intent_tag, best_score, best_pattern = self.rule_finder.find_best_intent(user_message)

        # Step 9: Pengecekan Threshold (Score >= 0.45)
        if not best_intent_tag or best_score < 0.45:
            # Step 10: Fallback Handling
            return self._generate_fallback(best_score)

        # Simpan slot yang diekstraksi dari input terkini
        session["current_intent"] = best_intent_tag
        session["slots"].update(extracted_slots)

        intent_data = best_pattern["intent_data"]
        confidence_percent = min(max(int(best_score * 100) + 10, 50), 98)

        # Step 11 & 12 & 13: Slot Filling Check, Dynamic Clarification, dan Rule Execution
        return self._check_slots_and_execute(best_intent_tag, intent_data, session, confidence=confidence_percent)

    def _check_slots_and_execute(self, intent_tag: str, intent_data: dict, session: dict, confidence: int) -> dict:
        """Pemeriksaan slot yang dibutuhkan dan eksekusi Rule Engine."""
        required_slots = intent_data.get("required_slots", [])
        slots = session.get("slots", {})

        # Pengecekan slot yang masih kosong
        missing_slots = [slot for slot in required_slots if not slots.get(slot)]

        if missing_slots:
            # Step 12: Dynamic Clarification dengan Variasi Kalimat
            target_slot = missing_slots[0]
            session["awaiting_slot"] = target_slot
            session["current_intent"] = intent_tag

            # Prioritas 1: Ambil variasi dari CSV template
            prompt_text = self.get_csv_template("need_clarification", category=target_slot)

            # Prioritas 2: Ambil variasi dari JSON intent
            if not prompt_text:
                json_variants = intent_data.get("clarification_variants", [])
                if json_variants:
                    prompt_text = random.choice(json_variants)

            # Prioritas 3: Fallback ke clarification_prompts standar
            if not prompt_text:
                clarification_prompts = intent_data.get("clarification_prompts", {})
                prompt_text = clarification_prompts.get(
                    target_slot, 
                    f"Mohon informasikan detail tambahan mengenai kondisi {target_slot} pada insiden tersebut."
                )

            return {
                "status": "need_clarification",
                "response": prompt_text,
                "confidence": 75,
                "intent": intent_tag,
                "missing_slot": target_slot
            }

        # Step 13: Rule Engine Execution (Seluruh slot telah terpenuhi)
        session["awaiting_slot"] = None
        executed_result = self._execute_rule_engine(intent_tag, intent_data, slots)

        return {
            "status": "success",
            "response": executed_result["formatted_text"],
            "confidence": confidence,
            "intent": intent_tag,
            "data": executed_result
        }

    def _execute_rule_engine(self, intent_tag: str, intent_data: dict, slots: dict) -> dict:
        """Mengeksekusi aturan logika deterministik IFAB di modul rules/*.py dengan kalimat pengantar natural."""
        responses_meta = intent_data.get("responses", {})
        law_ref = responses_meta.get("law_reference", "IFAB Laws of the Game")
        decision = "Sesuai Regulasi IFAB"
        explanation = responses_meta.get("explanation", "")
        restart = responses_meta.get("restart", "Pertandingan dilanjutkan.")

        # Ambil kalimat pembuka natural dari CSV atau JSON
        csv_intro = self.get_csv_template(intent_tag)
        json_intros = responses_meta.get("conversational_intros", [])
        chosen_intro = csv_intro or (random.choice(json_intros) if json_intros else "")

        # 1. Domain: Offside
        if "offside" in intent_tag:
            restart_type = slots.get("restart_type", "open_play")
            player_pos = slots.get("player_position", "offside_position")
            action = slots.get("action_type", "touch_ball")

            result = evaluate_offside(
                player_position=player_pos,
                action_type=action,
                restart_type=restart_type
            )
            decision = result.get("decision", decision)
            explanation = result.get("reason", explanation)
            law_ref = result.get("law_reference", law_ref)
            restart = "Indirect Free Kick untuk tim lawan." if result.get("is_offence") else "Pertandingan dilanjutkan."

        # 2. Domain: Handball
        elif "handball" in intent_tag:
            player_role = slots.get("player_role", "defender")
            hand_pos = slots.get("hand_position", "natural")
            is_goal = slots.get("is_goal_result", False)

            result = evaluate_handball(
                player_role=player_role,
                hand_position=hand_pos,
                is_goal_result=is_goal
            )
            decision = result.get("decision", decision)
            explanation = result.get("reason", explanation)
            law_ref = result.get("law_reference", law_ref)
            restart = "Direct Free Kick / Penalti untuk tim lawan." if result.get("is_handball") else "Permainan berlanjut secara normal."

        # 3. Domain: Penalty
        elif "penalty" in intent_tag:
            gk_feet = slots.get("goalkeeper_feet", "on_the_line")
            encroachment = slots.get("encroachment", "none")
            kick_result = slots.get("kick_result", "scored")

            result = evaluate_penalty(
                goalkeeper_feet=gk_feet,
                encroachment=encroachment,
                kick_result=kick_result
            )
            decision = result.get("decision", decision)
            explanation = result.get("reason", explanation)
            law_ref = result.get("law_reference", law_ref)
            restart = "Tendangan Penalti Diulang." if result.get("is_violation") else "Permainan dilanjutkan."

        # 4. Domain: VAR
        elif "var" in intent_tag:
            incident_type = slots.get("incident_type", "goal")
            error_severity = slots.get("error_severity", "clear_and_obvious")

            result = evaluate_var(
                incident_type=incident_type,
                error_severity=error_severity
            )
            decision = result.get("decision", decision)
            explanation = result.get("reason", explanation)
            law_ref = result.get("law_reference", law_ref)
            restart = "Sesuai keputusan akhir wasit."

        # 5. Domain: Fouls & Cards
        elif "fouls" in intent_tag:
            foul_type = slots.get("foul_type")
            is_dogso = (foul_type == "dogso") or slots.get("is_dogso", False)
            is_spa = (foul_type == "spa") or slots.get("is_spa", False)
            is_advantage = (foul_type == "advantage") or slots.get("is_advantage", False)
            contact = slots.get("contact_intensity", "excessive_force" if foul_type == "excessive_force" else "careless")

            result = evaluate_foul_misconduct(
                contact_intensity=contact,
                is_dogso=is_dogso,
                is_spa=is_spa,
                is_advantage=is_advantage
            )
            decision = result.get("decision", decision)
            explanation = result.get("reason", explanation)
            law_ref = result.get("law_reference", law_ref)
            restart = "Permainan dilanjutkan (Advantage)" if is_advantage else "Tendangan Bebas / Penalti untuk tim yang dilanggar."

        # Rangkai format teks yang profesional & natural
        formatted_lines = []
        if chosen_intro:
            formatted_lines.append(f"{chosen_intro}\n")

        formatted_lines.extend([
            f"Keputusan: {decision}",
            f"Dasar Regulasi: {law_ref}",
            "",
            "Penjelasan:",
            explanation,
            "",
            f"Tindakan Lanjutan (Restart): {restart}"
        ])
        formatted_text = "\n".join(formatted_lines)

        return {
            "decision": decision,
            "law_reference": law_ref,
            "explanation": explanation,
            "restart": restart,
            "formatted_text": formatted_text
        }

    def _generate_fallback(self, score: float) -> dict:
        """Step 10: Fallback handling yang ramah dan mencantumkan topik tercakup."""
        percentage = min(int(score * 100), 40)
        
        # Ambil variasi kalimat ramah dari CSV jika ada
        csv_fallback = self.get_csv_template("fallback", category="friendly")
        intro_fallback = csv_fallback if csv_fallback else "Maaf, informasi pada pertanyaan Anda belum cukup spesifik atau berada di luar cakupan regulasi IFAB yang terdaftar."

        fallback_text = (
            f"{intro_fallback}\n\n"
            "WasitBot siap membantu menjelaskan aturan resmi IFAB Laws of the Game berikut:\n"
            "• Law 11 (Offside): Posisi offside, aktif vs pasif, serta pengecualian lemparan ke dalam, goal kick, dan sepak pojok.\n"
            "• Law 12 (Handball): Sentuhan tangan penyerang vs bek, posisi tangan alami vs tidak alami memperbesar tubuh.\n"
            "• Law 12 (Pelanggaran & Kartu): Pelanggaran DOGSO (Kartu Merah), SPA (Kartu Kuning), dan aturan Advantage.\n"
            "• Law 14 (Tendangan Penalti): Posisi kaki kiper di garis dan pelanggaran encroachment (menerobos kotak penalti).\n"
            "• VAR Protocol: Kewenangan intervensi VAR untuk Gol, Penalti, Kartu Merah Langsung, dan Salah Identitas.\n\n"
            "Silakan ceritakan kembali situasi insiden pertandingan yang ingin Anda ketahui!"
        )
        return {
            "status": "fallback",
            "response": fallback_text,
            "confidence": percentage,
            "intent": "unknown"
        }
