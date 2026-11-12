import secrets
from flask import Flask, render_template, request, jsonify, session
from chat.intent_classifier import FlexibleRuleFinder
from chat.chatbot_engine import ChatbotEngine

# Step 3: Server Startup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Step 4: Inisialisasi FlexibleRuleFinder & ChatbotEngine sekali saat server startup
# Pre-tokenisasi semua pola knowledge base di memori untuk pencocokan ultra-cepat
print("=== Menginisialisasi FlexibleRuleFinder & Knowledge Base IFAB ===")
rule_finder = FlexibleRuleFinder()
chatbot_engine = ChatbotEngine(rule_finder=rule_finder)
print("=== ChatbotEngine Siap Melayani Pertanyaan ===")

@app.route("/")
def index():
    """Halaman antarmuka utama chat."""
    if "session_id" not in session:
        session["session_id"] = secrets.token_hex(8)
    return render_template("index.html")

# Step 5: API Endpoint menerima pesan pengguna
@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint API untuk memproses pesan percakapan dari user (Steps 5-14)."""
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "status": "error",
            "response": "Pesan tidak boleh kosong.",
            "confidence": 0
        }), 400

    if "session_id" not in session:
        session["session_id"] = secrets.token_hex(8)

    session_id = session["session_id"]
    
    # Eksekusi pipeline NLP 14 langkah
    result = chatbot_engine.process_message(user_message, session_id=session_id)

    # Step 14: Mengembalikan respons JSON terformat ke front-end
    return jsonify({
        "status": result.get("status", "success"),
        "response": result.get("response", ""),
        "confidence": result.get("confidence", 75),
        "intent": result.get("intent", "unknown")
    })

@app.route("/api/reset", methods=["POST"])
def reset():
    """Mereset konteks percakapan dan slot filling sesi aktif."""
    session_id = session.get("session_id")
    if session_id:
        chatbot_engine.reset_session(session_id)
    return jsonify({"status": "success", "message": "Konteks sesi berhasil direset."})

if __name__ == "__main__":
    print("=== Server Chatbot Aturan Sepak Bola (IFAB) Berjalan ===")
    print("Akses web interface di: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
