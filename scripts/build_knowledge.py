import os
import json

# Setup Path Direktori
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed", "rules.json")
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "data", "knowledge_base")

def create_knowledge_base():
    print("=== Membangun & Memperbaiki Knowledge Base Chatbot IFAB ===")
    
    # Pastikan folder data/knowledge_base/ dibuat
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
    
    extracted_data = {}
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                extracted_data = json.load(f)
        except Exception as e:
            print(f"[Warning] Gagal membaca {PROCESSED_FILE}: {e}")
    else:
        print(f"[Notice] File {PROCESSED_FILE} belum ada, menggunakan data standar.")

    # 1. Offside Knowledge (LAW 11)
    offside_kb = {
        "law": "Law 11 - Offside",
        "raw_reference": extracted_data.get("LAW11", {}).get("raw_text", ""),
        "intents": [
            {
                "tag": "offside_exception",
                "intent": "offside_exception",
                "patterns": [
                    "apakah lemparan ke dalam bisa offside",
                    "apakah lemparan kedalam bisa offside",
                    "lemparan kedalam bisa offside",
                    "lemparan kedalam ofsai gak",
                    "lemparan ke dalam offside gak",
                    "apakah throw in bisa offside",
                    "offside dari throw in",
                    "lemparan out kena ofside gak",
                    "apakah tendangan gawang bisa offside",
                    "tendangan gawang kena offside gak",
                    "goal kick ofsai gak",
                    "offside dari goal kick",
                    "apakah corner kick bisa offside",
                    "sepak pojok kena offside gak",
                    "tendangan sudut kena ofset gak",
                    "offside dari sepak pojok",
                    "terima bola langsung dari lemparan ke dalam",
                    "terima bola langsung dari tendangan gawang",
                    "terima bola langsung dari corner kick"
                ],
                "required_slots": ["restart_type"],
                "clarification_prompts": {
                    "restart_type": "Apakah bola diterima langsung dari lemparan ke dalam (throw-in), tendangan gawang (goal kick), atau sepak pojok (corner kick)?"
                },
                "clarification_variants": [
                    "Biar jelas aturannya, bola tadi diterima langsung dari mana ya? Apakah lemparan ke dalam, tendangan gawang, atau sepak pojok?",
                    "Bisa dipastikan kembali situasi awalnya? Apakah dari lemparan dalam (throw-in), goal kick, atau corner kick?"
                ],
                "responses": {
                    "law_reference": "Law 11.3 IFAB - No Offside Offence (Exceptions)",
                    "decision": "Bukan Pelanggaran Offside (Permainan Berlanjut)",
                    "explanation": "Berdasarkan Law 11.3 IFAB, seorang pemain TIDAK PERNAH dinyatakan offside jika menerima bola langsung dari: Lemparan ke dalam (Throw-in), Tendangan gawang (Goal kick), atau Sepak pojok (Corner kick).",
                    "conversational_intros": [
                        "Tenang saja, situasi tersebut dipastikan aman dari offside!",
                        "Kabar baik untuk tim penyerang, momen ini sah menurut regulasi IFAB.",
                        "Berdasarkan pengecualian resmi Law 11 IFAB:"
                    ],
                    "restart": "Permainan berlanjut secara normal.",
                    "rule_module": "rules.offside_rules",
                    "eval_func": "evaluate_offside"
                }
            },
            {
                "tag": "offside_eval",
                "intent": "offside_eval",
                "patterns": [
                    "apakah posisi begini offside",
                    "kapan pemain dinyatakan offside",
                    "kenapa wasit tiup peluit offside",
                    "kenapa ofsai",
                    "kapan kena ofside",
                    "pemain mendahului bek terakhir offside gak",
                    "pemain pasif diam saja offside gak",
                    "pemain di posisi offside tapi tidak sentuh bola",
                    "terjebak offside di daerah pertahanan lawan",
                    "aturan offside sepak bola ifab",
                    "kapan offside aktif dan kapan pasif",
                    "di belakang bek terakhir kena ofset gak",
                    "terlibat permainan aktif offside",
                    "pemain offside menghalangi pandangan kiper"
                ],
                "required_slots": ["player_position", "action_type"],
                "clarification_prompts": {
                    "player_position": "Apakah pemain berada lebih dekat ke garis gawang lawan daripada bola dan bek kedua terakhir (posisi offside) atau onside?",
                    "action_type": "Apakah pemain tersebut aktif memainkan bola / menghalangi lawan, atau hanya pasif diam?"
                },
                "clarification_variants": [
                    "Untuk menentukan offside, apakah pemain tadi bergerak aktif menyentuh/menghalangi bola atau hanya pasif diam?",
                    "Bisa diceritakan apakah pemain di depan tadi ikut mengejar bola atau sama sekali tidak mengganggu permainan lawan?"
                ],
                "responses": {
                    "law_reference": "Law 11.1 & 11.2 IFAB - Offside Position and Offence",
                    "decision": "Evaluasi Offside Berdasarkan Posisi dan Keterlibatan Aktif",
                    "explanation": "Berada di posisi offside bukanlah pelanggaran. Pelanggaran offside hanya terjadi jika pemain aktif terlibat dalam permainan (menyentuh bola, mengganggu pergerakan/pandangan lawan, atau memanfaatkan keuntungan pantulan).",
                    "conversational_intros": [
                        "Berikut penjelasan aturan offside berdasarkan posisi dan aksi pemain:",
                        "Kunci dari keputusan offside ada pada keterlibatan aktif pemain di lapangan:"
                    ],
                    "restart": "Indirect Free Kick (Tendangan Bebas Tidak Langsung) untuk tim lawan.",
                    "rule_module": "rules.offside_rules",
                    "eval_func": "evaluate_offside"
                }
            }
        ]
    }

    # 2. Handball Knowledge (LAW 12)
    law12_text = extracted_data.get("LAW12", {}).get("raw_text", "")
    handball_kb = {
        "law": "Law 12 - Handball",
        "raw_reference": law12_text,
        "intents": [
            {
                "tag": "handball_eval",
                "intent": "handball_eval",
                "patterns": [
                    "apakah handball",
                    "hansbal gak wasit",
                    "handsball gak",
                    "kena tangan penalti gak",
                    "bola kena tangan bek di kotak penalti",
                    "tangan nempel di badan kena bola handball gak",
                    "tangan menempel rapat kena bola",
                    "tangan terbuka lebar kena bola hansbal gak",
                    "tangan terangkat di atas bahu kena bola",
                    "penyerang tidak sengaja kena tangan terus gol",
                    "striker cetak gol kena tangan hansbal",
                    "bola mantul mengenai lengan pemain bertahan",
                    "tangan aktif vs pasif handball",
                    "aturan posisi tangan alami dan tidak alami ifab",
                    "tangan memperbesar area tubuh handball",
                    "apakah kiper tangkap bola di kotak penalti handball",
                    "tangan membentang kena bola penalti gak"
                ],
                "required_slots": ["player_role", "hand_position"],
                "clarification_prompts": {
                    "player_role": "Apakah bola mengenai tangan pemain penyerang (attacker), pemain bertahan (bek), atau penjaga gawang (kiper)?",
                    "hand_position": "Bagaimana posisi tangan saat kejadian? Apakah menempel wajar/alami di samping badan, atau terangkat melebar menjauhi tubuh (memperbesar tubuh)?"
                },
                "clarification_variants": [
                    "Agar analisis akurat: apakah tangan pemain menempel wajar di tubuh atau terangkat lebar membuat badan lebih besar?",
                    "Bisa diperjelas apakah sentuhan tangan tadi mengenai pemain bertahan (bek) atau penyerang yang hendak mencetak gol?"
                ],
                "responses": {
                    "law_reference": "Law 12.1 IFAB - Handling the Ball",
                    "decision": "Evaluasi Handball Berdasarkan Peran dan Posisi Tangan",
                    "explanation": "Untuk pemain bertahan: jika tangan berada pada posisi alami dan wajar, maka BUKAN handball. Jika tangan terangkat melebar memperbesar tubuh, maka merupakan pelanggaran. Untuk penyerang: bola menyentuh tangan yang langsung berujung gol selalu dianggap handball.",
                    "conversational_intros": [
                        "Mengenai insiden handball ini, berikut evaluasi resmi menurut Law 12 IFAB:",
                        "Regulasi IFAB membedakan penanganan handball antara posisi tubuh alami dan tidak alami:"
                    ],
                    "restart": "Direct Free Kick atau Tendangan Penalti jika terjadi di dalam area penalti.",
                    "rule_module": "rules.handball_rules",
                    "eval_func": "evaluate_handball"
                }
            }
        ]
    }

    # 3. Fouls & Cards Knowledge (LAW 12)
    fouls_cards_kb = {
        "law": "Law 12 - Fouls & Misconduct",
        "raw_reference": law12_text,
        "intents": [
            {
                "tag": "fouls_cards_eval",
                "intent": "fouls_cards_eval",
                "patterns": [
                    "kapan pemain dapat kartu merah langsung",
                    "apa itu dogso kartu merah",
                    "pemain terakhir ditarik pas mau gol kartu apa",
                    "ditarik pas mau gol dogso",
                    "orang terakhir narik baju striker kartu merah gak",
                    "apa itu spa pelanggaran taktis kartu kuning",
                    "tarik baju serangan balik kartu kuning",
                    "aturan advantage wasit sepak bola",
                    "kenapa wasit biarkan main padahal dilanggar advantage",
                    "main terus dikasih keuntungan wasit",
                    "tekel berbahaya excessive force red card",
                    "kapan pelanggaran berbuah kartu kuning reckless",
                    "beda careless reckless dan excessive force",
                    "pelanggaran ceroboh kartu kuning",
                    "kartu merah pelanggaran keras brutal"
                ],
                "required_slots": ["foul_type"],
                "clarification_prompts": {
                    "foul_type": "Apakah insiden tersebut merupakan penggagalan peluang emas gol (DOGSO), penghentian serangan menjanjikan (SPA), aturan keuntungan (Advantage), atau tekel keras berbahaya?"
                },
                "clarification_variants": [
                    "Mohon jelaskan situasi pelanggarannya: apakah menarik pemain terakhir (DOGSO), jegalan serangan balik (SPA), atau tekel kasar berbahaya?",
                    "Konteks pelanggarannya bagaimana? Apakah menggagalkan peluang gol bersih atau sekadar pelanggaran taktis?"
                ],
                "responses": {
                    "law_reference": "Law 12.3 IFAB - Disciplinary Action",
                    "decision": "Evaluasi Pelanggaran dan Sanksi Disiplin (Kartu)",
                    "explanation": "DOGSO (Denial of an Obvious Goal-Scoring Opportunity) diganjar Kartu Merah Langsung. SPA (Stopping a Promising Attack) diganjar Kartu Kuning. Advantage diterapkan wasit jika tim yang dilanggar tetap memiliki penguasaan bola yang menguntungkan.",
                    "conversational_intros": [
                        "Berdasarkan derajat keparahan dan dampak pelanggaran terhadap jalannya laga:",
                        "Berikut dasar pertimbangan wasit dalam pemberian sanksi kartu Law 12:"
                    ],
                    "restart": "Tendangan Bebas Langsung / Penalti (atau permainan dilanjutkan jika Advantage).",
                    "rule_module": "rules.fouls_cards_rules",
                    "eval_func": "evaluate_foul_misconduct"
                }
            }
        ]
    }

    # 4. Penalty Knowledge (LAW 14)
    penalty_kb = {
        "law": "Law 14 - Penalty Kick",
        "raw_reference": extracted_data.get("LAW14", {}).get("raw_text", ""),
        "intents": [
            {
                "tag": "penalty_eval",
                "intent": "penalty_eval",
                "patterns": [
                    "kapan tendangan penalti harus diulang",
                    "apakah penalti bisa diulang kalau kiper maju",
                    "penalti bisa diulang kalau kiper maju",
                    "apakah penalti bisa diulang",
                    "penalti diulang kalau kiper maju",
                    "kiper maju duluan keluar garis saat penalti",
                    "kedua kaki kiper keluar garis gawang penalti diulang gak",
                    "pemain nyelonong masuk kotak penalti duluan",
                    "pemain lawan menerobos kotak penalti sebelum ditendang",
                    "rekan penendang masuk kotak penalti duluan",
                    "encroachment penalti apa aturannya",
                    "kiper tepis penalti tapi kaki maju lebih dulu",
                    "aturan posisi kiper saat tendangan penalti",
                    "penalti gol tapi ada pemain masuk kotak 16",
                    "pinalti diulang atau sah",
                    "kiper harus injak garis penalti gak",
                    "kaki kiper keluar garis gawang penalti"
                ],
                "required_slots": ["goalkeeper_feet"],
                "clarification_prompts": {
                    "goalkeeper_feet": "Apakah kiper melangkah keluar garis gawang dengan kedua kaki sebelum bola ditendang, atau minimal 1 kaki tetap menapak di garis?"
                },
                "clarification_variants": [
                    "Bisa dikonfirmasi posisi kiper saat bola dieksekusi: apakah sudah melangkah maju melewati garis gawang?",
                    "Apakah kiper mempertahankan minimal satu kakinya tetap menapak di garis gawang saat tendangan diambil?"
                ],
                "responses": {
                    "law_reference": "Law 14.1 & 14.2 IFAB - The Penalty Kick",
                    "decision": "Evaluasi Pelanggaran Prosedur Tendangan Penalti",
                    "explanation": "Kiper wajib menempatkan minimal 1 kaki menyentuh atau sejajar di atas garis gawang saat bola ditendang. Jika kiper maju duluan dan menepis tendangan penalti, penalti wajib diulang dan kiper diberi peringatan. Pelanggaran encroachment oleh pemain luar juga dapat menyebabkan penalti diulang tergantung hasil tendangan.",
                    "conversational_intros": [
                        "Pada situasi penalti, Law 14 mengatur prosedur eksekusi secara ketat:",
                        "Berikut evaluasi keabsahan tendangan penalti dan posisi penjaga gawang:"
                    ],
                    "restart": "Tendangan Penalti Diulang atau Gol Disahkan.",
                    "rule_module": "rules.penalty_rules",
                    "eval_func": "evaluate_penalty"
                }
            }
        ]
    }

    # 5. VAR Protocol Knowledge
    var_kb = {
        "law": "VAR Protocol IFAB",
        "raw_reference": extracted_data.get("VAR_Protocol", {}).get("raw_text", ""),
        "intents": [
            {
                "tag": "var_eval",
                "intent": "var_eval",
                "patterns": [
                    "kapan var boleh intervensi",
                    "kenapa var gak cek kartu kuning tadi",
                    "kenapa var gak cek kartu kuning",
                    "kenapa var tidak cek kartu kuning",
                    "kejadian apa saja yang boleh dicek var",
                    "aturan protokol var ifab",
                    "kapan wasit melihat layar monitor var",
                    "on field review var",
                    "apa maksud clear and obvious error var",
                    "apakah var boleh cek pelanggaran biasa di tengah lapangan",
                    "apakah var bisa menganulir kartu merah",
                    "var cek salah identitas pemain",
                    "kenapa kartu kuning kedua gak dicek var",
                    "apakah sepak pojok bisa dicek var",
                    "kapan wasit cek monitor var di pinggir lapangan"
                ],
                "required_slots": ["incident_type"],
                "clarification_prompts": {
                    "incident_type": "Kejadian apa yang sedang Anda tanyakan terkait intervensi VAR? (Gol / Tidak Gol, Penalti / Tidak Penalti, Kartu Merah Langsung, atau Salah Identitas)?"
                },
                "clarification_variants": [
                    "Insiden apa yang ingin Anda cek wewenang VAR-nya? (Contoh: proses gol, penalti, kartu merah langsung, atau kartu kuning biasa?)",
                    "Kejadian spesifik mana yang dipersoalkan terkait pengecekan monitor VAR?"
                ],
                "responses": {
                    "law_reference": "VAR Protocol IFAB - Principles & Reviewable Categories",
                    "decision": "Evaluasi Intervensi Video Assistant Referee (VAR)",
                    "explanation": "VAR hanya berhak membantu wasit pada 4 kategori utama berdasar prinsip 'Clear and Obvious Error': (1) Gol / Tidak Gol, (2) Penalti / Tidak Penalti, (3) Kartu Merah Langsung, dan (4) Salah Identitas Pemain. VAR dilarang mengintervensi kartu kuning biasa atau pelanggaran rutin di luar kategori tersebut.",
                    "conversational_intros": [
                        "Perlu dipahami bahwa wewenang VAR sangat dibatasi oleh protokol IFAB:",
                        "Berikut prinsip kerja intervensi VAR dalam pertandingan resmi:"
                    ],
                    "restart": "Sesuai keputusan akhir wasit setelah pengecekan (OFR atau VAR-only review).",
                    "rule_module": "rules.var_rules",
                    "eval_func": "evaluate_var"
                }
            }
        ]
    }

    # 6. Glossary & Football Slang Dictionary
    glossary_kb = {
        "law": "IFAB Football Glossary & Terminology",
        "synonyms": {
            "DOGSO": ["orang terakhir", "pemain terakhir", "ditarik pas mau gol", "peluang emas", "peluang gol", "tarik striker"],
            "SPA": ["tarik baju", "tackle dari belakang", "potong serangan balik", "serangan menjanjikan", "pelanggaran taktis"],
            "Advantage": ["dibiarkan main", "gak ditiup", "main terus", "dikasih keuntungan", "tidak peluit wasit"],
            "Encroachment": ["nyelonong masuk", "masuk kotak penalti duluan", "menerobos kotak penalti", "lari duluan"],
            "Handball": ["kena tangan", "tangan aktif", "bola kena lengan", "sentuh tangan", "hansbal", "handsball"],
            "Offside": ["ofsai", "off side", "off-side", "posisi offside", "ofset"],
            "Penalty": ["pinalti", "titik putih", "kotak 16", "tendangan 12 pas"]
        },
        "intents": [
            {
                "tag": "glossary_query",
                "intent": "glossary_query",
                "patterns": [
                    "apa arti dogso dalam sepak bola",
                    "istilah dogso artinya apa",
                    "apa maksud spa di sepak bola",
                    "arti encroachment penalti",
                    "apa itu aturan advantage wasit",
                    "kamus istilah peraturan sepak bola ifab",
                    "arti direct free kick dan indirect free kick",
                    "apa maksud handball dan offside",
                    "istilah sepak bola ifab"
                ],
                "required_slots": [],
                "clarification_prompts": {},
                "responses": {
                    "law_reference": "IFAB Football Glossary",
                    "decision": "Penjelasan Glosarium Istilah Resmi Sepak Bola",
                    "explanation": "Berikut glosarium istilah resmi regulasi IFAB:\n• DOGSO: Denial of an Obvious Goal-Scoring Opportunity (menggagalkan peluang emas mencetak gol, sanksi: Kartu Merah).\n• SPA: Stopping a Promising Attack (menghentikan serangan menjanjikan, sanksi: Kartu Kuning).\n• Encroachment: Pelanggaran memasuki area terlarang (seperti kotak penalti) sebelum bola resmi ditendang.\n• Advantage: Keuntungan yang diberikan wasit agar tim yang dilanggar tetap melanjutkan penguasaan bola.\n• Handling (Handball): Sentuhan bola yang melanggar aturan oleh tangan/lengan di bawah batas bawah ketiak.",
                    "conversational_intros": [
                        "Berikut rangkuman istilah resmi dalam regulasi sepak bola:",
                        "Kamus glosarium resmi IFAB mendefinisikannya sebagai berikut:"
                    ],
                    "restart": "Informasi regulasi umum IFAB.",
                    "rule_module": None,
                    "eval_func": None
                }
            }
        ]
    }

    # Daftar Simpan File
    files_to_save = {
        "offside.json": offside_kb,
        "handball.json": handball_kb,
        "fouls_cards.json": fouls_cards_kb,
        "penalty.json": penalty_kb,
        "var.json": var_kb,
        "glossary.json": glossary_kb
    }

    for filename, content in files_to_save.items():
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  └─ Berhasil membuat/memperbarui: data/knowledge_base/{filename}")

    print("\n=== Knowledge Base Berhasil Diperbaiki & Disinkronkan ===")

if __name__ == "__main__":
    create_knowledge_base()
