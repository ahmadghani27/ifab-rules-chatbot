def evaluate_foul_misconduct(contact_intensity: str, is_dogso: bool = False, is_spa: bool = False, is_advantage: bool = False) -> dict:
    """
    Evaluasi Aturan Law 12 - Pelanggaran & Kartu (Fouls and Misconduct).
    """
    # 1. Aturan Keuntungan (Advantage Rule)
    if is_advantage:
        return {
            "sanction": "Advantage (Permainan Berlanjut)",
            "decision": "Wasit Membiarkan Permainan Berjalan",
            "reason": "Wasit menerapkan aturan Advantage karena tim yang dilanggar tetap memegang kontrol bola dalam posisi yang menguntungkan.",
            "law_reference": "Law 12.3 IFAB - Advantage"
        }

    # 2. DOGSO (Denial of an Obvious Goal-Scoring Opportunity)
    if is_dogso:
        return {
            "sanction": "Kartu Merah Langsung",
            "decision": "Pelanggaran Kartu Merah (DOGSO)",
            "reason": "Menggagalkan peluang emas mencetak gol lawan (Denial of an Obvious Goal-Scoring Opportunity).",
            "law_reference": "Law 12.3 IFAB - Disciplinary Action (DOGSO)"
        }

    # 3. SPA (Stopping a Promising Attack)
    if is_spa:
        return {
            "sanction": "Kartu Kuning",
            "decision": "Pelanggaran Kartu Kuning (SPA)",
            "reason": "Menghentikan serangan yang menjanjikan (Stopping a Promising Attack) dengan pelanggaran taktis.",
            "law_reference": "Law 12.3 IFAB - Disciplinary Action (SPA)"
        }

    # 4. Berdasarkan Intensitas Kontak
    if contact_intensity == 'excessive_force':
        return {
            "sanction": "Kartu Merah Langsung",
            "decision": "Pelanggaran Serious Foul Play / Violent Conduct",
            "reason": "Menggunakan tenaga berlebihan (Excessive Force) yang membahayakan keselamatan lawan.",
            "law_reference": "Law 12.1 & 12.3 IFAB"
        }
    elif contact_intensity == 'reckless':
        return {
            "sanction": "Kartu Kuning",
            "decision": "Pelanggaran Ceroboh (Reckless Foul)",
            "reason": "Melakukan tindakan ceroboh tanpa memperhitungkan risiko atau bahaya bagi lawan.",
            "law_reference": "Law 12.1 IFAB"
        }

    return {
        "sanction": "Tendangan Bebas / Pelanggaran Biasa",
        "decision": "Pelanggaran Tanpa Kartu (Careless Foul)",
        "reason": "Pelanggaran biasa akibat kurang hati-hati tanpa unsur kecerobohan atau tenaga berlebihan.",
        "law_reference": "Law 12.1 IFAB"
    }