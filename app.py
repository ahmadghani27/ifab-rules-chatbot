from flask import Flask, render_template, request, jsonify
from chat.chatbot_engine import ChatbotEngine

app = Flask(__name__)
bot_engine = ChatbotEngine()

@app.route("/")
def index():
    """Halaman utama interface chat."""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint API untuk memproses pesan dari user."""
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "status": "error",
            "response": "Pesan tidak boleh kosong."
        }), 400

    # Proses pesan lewat Chatbot Engine
    bot_result = bot_engine.process_message(user_message)
    return jsonify(bot_result)

if __name__ == "__main__":
    print("=== Server Chatbot Aturan Sepak Bola Berjalan ===")
    print("Akses web interface di: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)