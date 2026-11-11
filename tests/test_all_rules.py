import unittest
import sys
import os

# Menambahkan root directory ke sys.path agar modul rules dan chatbot dapat di-import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rules.offside_rules import evaluate_offside
from rules.handball_rules import evaluate_handball
from rules.penalty_rules import evaluate_penalty
from rules.var_rules import evaluate_var
from rules.fouls_cards_rules import evaluate_foul_misconduct
from chat.intent_classifier import IntentClassifier
from chat.chatbot_engine import ChatbotEngine


class TestOffsideRules(unittest.TestCase):
    """Pengujian Unit untuk Law 11 - Offside"""

    def test_offside_exception_throw_in(self):
        result = evaluate_offside(player_position='offside_position', action_type='touch_ball', restart_type='throw_in')
        self.assertFalse(result['is_offence'])
        self.assertIn("Bukan Pelanggaran Offside", result['decision'])

    def test_offside_active_player(self):
        result = evaluate_offside(player_position='offside_position', action_type='touch_ball', restart_type='open_play')
        self.assertTrue(result['is_offence'])
        self.assertIn("Pelanggaran Offside", result['decision'])

    def test_offside_passive_player(self):
        result = evaluate_offside(player_position='offside_position', action_type='passive', restart_type='open_play')
        self.assertFalse(result['is_offence'])
        self.assertIn("Bukan Pelanggaran Offside", result['decision'])


class TestHandballRules(unittest.TestCase):
    """Pengujian Unit untuk Law 12 - Handball"""

    def test_attacker_accidental_handball_goal(self):
        result = evaluate_handball(player_role='attacker', hand_position='natural', is_goal_result=True)
        self.assertTrue(result['is_handball'])
        self.assertIn("Pelanggaran Handball", result['decision'])

    def test_defender_natural_hand_position(self):
        result = evaluate_handball(player_role='defender', hand_position='natural', is_goal_result=False)
        self.assertFalse(result['is_handball'])
        self.assertIn("Bukan Handball", result['decision'])

    def test_defender_unnatural_hand_position(self):
        result = evaluate_handball(player_role='defender', hand_position='unnatural', is_goal_result=False)
        self.assertTrue(result['is_handball'])
        self.assertIn("Pelanggaran Handball", result['decision'])


class TestPenaltyRules(unittest.TestCase):
    """Pengujian Unit untuk Law 14 - Tendangan Penalti"""

    def test_goalkeeper_off_line_saved(self):
        result = evaluate_penalty(goalkeeper_feet='off_the_line_early', encroachment='none', kick_result='saved')
        self.assertTrue(result['is_violation'])
        self.assertIn("Penalti Diulang", result['decision'])

    def test_goalkeeper_off_line_scored(self):
        result = evaluate_penalty(goalkeeper_feet='off_the_line_early', encroachment='none', kick_result='scored')
        self.assertFalse(result['is_violation'])
        self.assertEqual(result['decision'], "Gol Sah")


class TestVARRules(unittest.TestCase):
    """Pengujian Unit untuk Protokol VAR"""

    def test_var_yellow_card_not_allowed(self):
        result = evaluate_var(incident_type='yellow_card')
        self.assertFalse(result['can_review'])
        self.assertIn("VAR Tidak Boleh Berintervensi", result['decision'])

    def test_var_red_card_allowed(self):
        result = evaluate_var(incident_type='direct_red_card', error_severity='clear_and_obvious')
        self.assertTrue(result['can_review'])
        self.assertIn("VAR Boleh Berintervensi", result['decision'])


class TestFoulsAndMisconduct(unittest.TestCase):
    """Pengujian Unit untuk Law 12 - Pelanggaran & Kartu"""

    def test_dogso_red_card(self):
        result = evaluate_foul_misconduct(contact_intensity='careless', is_dogso=True)
        self.assertEqual(result['sanction'], "Kartu Merah Langsung")

    def test_advantage_rule(self):
        result = evaluate_foul_misconduct(contact_intensity='reckless', is_advantage=True)
        self.assertIn("Advantage", result['sanction'])


class TestChatbotEngine(unittest.TestCase):
    """Pengujian Unit Integrasi Intent Classifier & Chatbot Engine"""

    def setUp(self):
        self.classifier = IntentClassifier()
        self.engine = ChatbotEngine()

    def test_intent_classification(self):
        self.assertEqual(self.classifier.classify("Apakah lemparan kedalam bisa offside?"), "offside")
        self.assertEqual(self.classifier.classify("Kenapa VAR gak cek kartu kuning tadi?"), "var")
        self.assertEqual(self.classifier.classify("Apakah penalti bisa diulang kalau kiper maju?"), "penalty")

    def test_engine_process_offside_throw_in(self):
        response = self.engine.process_message("Apakah lemparan kedalam bisa offside?")
        self.assertEqual(response['status'], "success")
        self.assertIn("Bukan Pelanggaran Offside", response['response'])


if __name__ == '__main__':
    unittest.main()