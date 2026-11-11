def evaluate_penalty(goalkeeper_feet: str, encroachment: str = None, kick_result: str = 'scored') -> dict:
    """
    Evaluasi Aturan Law 14 - Tendangan Penalti.
    
    Parameters:
    - goalkeeper_feet: 'on_the_line' | 'off_the_line_early'
    - encroachment: 'attacker_entered' | 'defender_entered' | 'both_entered' | 'none'
    - kick_result: 'scored' | 'saved' | 'missed'
    """
    # 1. Pelanggaran Pergerakan Kiper
    if goalkeeper_feet == 'off_the_line_early':
        if kick_result in ['saved', 'missed']:
            return {
                "is_violation": True,
                "decision": "Tendangan Penalti Diulang & Kiper Diberi Peringatan",
                "reason": "Kiper melangkah keluar dari garis gawang dengan kedua kaki sebelum bola ditendang, dan berhasil memengaruhi hasil tendangan (penyelamatan).",
                "law_reference": "Law 14.2 IFAB - Offences and Sanctions (Goalkeeper)"
            }
        elif kick_result == 'scored':
            return {
                "is_violation": False,
                "decision": "Gol Sah",
                "reason": "Kiper memang melangkah keluar lebih awal, namun karena bola tetap masuk menjadi gol, pelanggaran diabaikan.",
                "law_reference": "Law 14.2 IFAB"
            }

    # 2. Pelanggaran Encroachment (Pemain Menerobos Kotak Penalti)
    if encroachment == 'attacker_entered':
        if kick_result == 'scored':
            return {
                "is_violation": True,
                "decision": "Penalti Diulang",
                "reason": "Rekan penendang masuk ke kotak penalti sebelum bola ditendang dan gol tercipta.",
                "law_reference": "Law 14.2 IFAB - Encroachment"
            }
        else:
            return {
                "is_violation": True,
                "decision": "Tendangan Bebas Tidak Langsung untuk Tim Defensif",
                "reason": "Rekan penendang masuk ke kotak penalti lebih awal dan eksekusi gagal.",
                "law_reference": "Law 14.2 IFAB - Encroachment"
            }

    elif encroachment == 'defender_entered':
        if kick_result == 'scored':
            return {
                "is_violation": False,
                "decision": "Gol Sah",
                "reason": "Pemain bertahan menerobos masuk duluan, namun penendang tetap berhasil mencetak gol.",
                "law_reference": "Law 14.2 IFAB"
            }
        else:
            return {
                "is_violation": True,
                "decision": "Penalti Diulang",
                "reason": "Pemain bertahan menerobos masuk ke kotak penalti lebih awal dan memengaruhi kegagalan eksekusi.",
                "law_reference": "Law 14.2 IFAB"
            }

    elif encroachment == 'both_entered':
        return {
            "is_violation": True,
            "decision": "Penalti Diulang",
            "reason": "Pemain dari kedua tim sama-sama menerobos masuk ke kotak penalti sebelum bola ditendang.",
            "law_reference": "Law 14.2 IFAB"
        }

    return {
        "is_violation": False,
        "decision": "Eksekusi Penalti Sah",
        "reason": "Seluruh prosedur penalti dilaksanakan sesuai aturan Law 14.",
        "law_reference": "Law 14.1 IFAB"
    }