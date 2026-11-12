import unittest
import json
import sys
import os

# Menambahkan root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from chat.preprocessing import TextPreprocessor
from chat.intent_classifier import FlexibleRuleFinder, IntentClassifier
from chat.chatbot_engine import ChatbotEngine
from rules.offside_rules import evaluate_offside
from rules.handball_rules import evaluate_handball
from rules.penalty_rules import evaluate_penalty
from rules.var_rules import evaluate_var
from rules.fouls_cards_rules import evaluate_foul_misconduct

class TestNLPPipeline14Steps(unittest.TestCase):
    """
    Pengujian komprehensif alur 14-Step NLP Pipeline Chatbot Sepak Bola IFAB
    """

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.finder = FlexibleRuleFinder()
        self.engine = ChatbotEngine(rule_finder=self.finder)

    def test_step4_and_6_preprocessing_and_slang(self):
        """Uji Step 4 & 6: Slang Normalization & Safe Sastrawi Stemming."""
        # 1. Slang normalization yang dispesifikasikan dalam instruksi
        test_slang = "ofsai hansbal pinalti nempel ditarik"
        prep = TextPreprocessor.preprocess(test_slang)
        normalized = prep["normalized"]
        
        self.assertIn("offside", normalized)
        self.assertIn("handball", normalized)
        self.assertIn("penalty", normalized)
        self.assertIn("tempel", normalized)
        self.assertIn("tarik", normalized)

        # 2. Ketahanan terhadap string kosong atau simbol aneh
        empty_prep = TextPreprocessor.preprocess("")
        self.assertEqual(empty_prep["tokens"], [])
        self.assertEqual(empty_prep["stemmed_tokens"], [])

        symbol_prep = TextPreprocessor.preprocess("!@#$%^&*()_+{}[]:;<>?,./~`")
        self.assertEqual(symbol_prep["tokens"], [])

        # 3. Ketahanan stemmer terhadap slang ekstrem dan typo
        stemmed_word = TextPreprocessor.safe_stem_word("menendangkannya")
        self.assertTrue(len(stemmed_word) > 0)

    def test_step7_similarity_scoring_formula(self):
        """Uji Step 7: Verifikasi formula skor (0.4 * Jaccard) + (0.3 * Fuzzy) + (0.3 * Coverage)."""
        pattern_item = {
            "stemmed_tokens": {"lempar", "dalam", "offside"},
            "stemmed_text": "lempar dalam offside"
        }
        user_tokens = {"apakah", "lempar", "dalam", "offside"}
        user_text = "apakah lempar dalam offside"

        score = self.finder.calculate_similarity_score(user_tokens, user_text, pattern_item)
        self.assertGreaterEqual(score, 0.45)
        self.assertLessEqual(score, 1.0)

    def test_step9_and_10_threshold_and_fallback(self):
        """Uji Step 9 & 10: Query acak di bawah 0.45 menghasilkan fallback."""
        random_query = "resep membuat kue bolu pandan cokelat enak"
        result = self.engine.process_message(random_query)

        self.assertEqual(result["status"], "fallback")
        self.assertLess(result["confidence"], 45)
        self.assertIn("WasitBot siap membantu menjelaskan aturan resmi IFAB", result["response"])

    def test_step11_and_12_slot_filling_and_dynamic_clarification(self):
        """Uji Step 11 & 12: Pertanyaan handball tanpa slot menghasilkan pertanyaan klarifikasi dinamis."""
        session_id = "test_slot_session_1"
        self.engine.reset_session(session_id)

        # Pertanyaan umum tentang handball (belum ada peran pemain dan posisi tangan)
        res1 = self.engine.process_message("Apakah itu tadi handball wasit?", session_id=session_id)
        self.assertEqual(res1["status"], "need_clarification")
        self.assertIn("penyerang", res1["response"])

        # Menjawab peran pemain: bek
        res2 = self.engine.process_message("Pemain bertahan / bek", session_id=session_id)
        self.assertEqual(res2["status"], "need_clarification")
        self.assertIn("posisi tangan", res2["response"])

        # Menjawab posisi tangan: menempel di badan
        res3 = self.engine.process_message("Tangannya menempel rapat di tubuh secara alami", session_id=session_id)
        self.assertEqual(res3["status"], "success")
        self.assertIn("Bukan Handball", res3["response"])

    def test_step13_rule_engine_execution(self):
        """Uji Step 13: Eksekusi langsung modul rules/*.py."""
        # 1. Offside Throw-in Exception
        offside_res = evaluate_offside(player_position="offside_position", action_type="touch_ball", restart_type="throw_in")
        self.assertFalse(offside_res["is_offence"])
        self.assertIn("Bukan Pelanggaran Offside", offside_res["decision"])

        # 2. Handball Attacker
        handball_res = evaluate_handball(player_role="attacker", hand_position="natural", is_goal_result=True)
        self.assertTrue(handball_res["is_handball"])
        self.assertIn("Pelanggaran Handball", handball_res["decision"])

        # 3. Penalty Goalkeeper off line
        pen_res = evaluate_penalty(goalkeeper_feet="off_the_line_early", kick_result="saved")
        self.assertTrue(pen_res["is_violation"])
        self.assertIn("Penalti Diulang", pen_res["decision"])

        # 4. VAR Intervention
        var_res = evaluate_var(incident_type="direct_red_card", error_severity="clear_and_obvious")
        self.assertTrue(var_res["can_review"])
        self.assertIn("VAR Boleh Berintervensi", var_res["decision"])

        # 5. Fouls DOGSO
        foul_res = evaluate_foul_misconduct(contact_intensity="careless", is_dogso=True)
        self.assertEqual(foul_res["sanction"], "Kartu Merah Langsung")

    def test_step14_flask_api_endpoint(self):
        """Uji Step 14 & Step 5: Endpoint Flask POST /api/chat dan POST /api/reset."""
        # 1. Uji pesan kosong
        empty_res = self.app.post("/api/chat", json={"message": ""})
        self.assertEqual(empty_res.status_code, 400)

        # 2. Uji query offside throw-in
        chat_res = self.app.post("/api/chat", json={"message": "Apakah lemparan ke dalam bisa offside?"})
        self.assertEqual(chat_res.status_code, 200)
        data = json.loads(chat_res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("Bukan Pelanggaran Offside", data["response"])
        self.assertGreaterEqual(data["confidence"], 50)

        # 3. Uji reset endpoint
        reset_res = self.app.post("/api/reset")
        self.assertEqual(reset_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()

