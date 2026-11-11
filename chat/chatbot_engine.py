from chat.intent_classifier import IntentClassifier
from rules.offside_rules import evaluate_offside
from rules.handball_rules import evaluate_handball

class ChatbotEngine:
    def __init__(self):
        self.classifier = IntentClassifier()

    def process_message(self, user_message: str) -> dict:
        """Mengolah pesan pengguna dan mengembalikan respon aturan."""
        intent = self.classifier.classify(user_message)
        entities = self.classifier.extract_entities(user_message)

        # 1. Penanganan Intent: Offside
        if intent == "offside":
            # Set default jika tidak ada pengecualian restart
            restart_type = entities.get("restart_type", "open_play")
            
            # Jika user menyebutkan aktif/pasif atau posisi
            player_pos = "offside_position"
            action = "touch_ball" if entities.get("is_goal_result") else "passive"
            
            result = evaluate_offside(
                player_position=player_pos, 
                action_type=action, 
                restart_type=restart_type
            )
            return self._format_response(result)

        # 2. Penanganan Intent: Handball
        elif intent == "handball":
            player_role = entities.get("player_role")
            hand_pos = entities.get("hand_position")
            is_goal = entities.get("is_goal_result", False)

            # Jika slot belum lengkap (Slot Filling Trigger)
            if not player_role:
                return {
                    "response": "Untuk menentukan apakah itu handball, bisa beri tahu saya: Apakah bola mengenai tangan pemain penyerang atau pemain bertahan (bek)?",
                    "status": "need_clarification"
                }
            if player_role == "defender" and not hand_pos:
                return {
                    "response": "Apakah posisi tangan bek tersebut berada di posisi alami (di samping badan) atau terangkat lebar membuat tubuhnya makin besar?",
                    "status": "need_clarification"
                }

            result = evaluate_handball(
                player_role=player_role,
                hand_position=hand_pos,
                is_goal_result=is_goal
            )
            return self._format_response(result)

        # 3. Unknown Intent
        return {
            "response": "Maaf, saya belum memahami pertanyaan Anda. Anda bisa menanyakan kejadian tentang Offside, Handball, Penalti, atau Keputusan VAR berdasarkan aturan IFAB.",
            "status": "unknown"
        }

    def _format_response(self, result: dict) -> dict:
        """Format tampilan teks balasan akhir."""
        text = f"**Keputusan Aturan:** {result['decision']}\n\n"
        text += f"**Alasan:** {result['reason']}\n\n"
        text += f"*(Dasar Hukum: {result['law_reference']})*"
        
        return {
            "response": text,
            "status": "success",
            "data": result
        }