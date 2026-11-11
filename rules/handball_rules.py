def evaluate_handball(player_role: str, hand_position: str, is_goal_result: bool = False) -> dict:
    """
    Evaluasi Aturan Law 12 - Handball berdasarkan peran dan posisi tangan.
    
    Parameters:
    - player_role: 'attacker' | 'defender' | 'goalkeeper'
    - hand_position: 'natural' | 'unnatural' | 'above_shoulder'
    - is_goal_result: True | False (Apakah aksi berujung langsung pada gol/peluang gol)
    """
    # 1. Aturan Khusus Penyerang (Attacker)
    if player_role == 'attacker':
        if is_goal_result or hand_position in ['unnatural', 'above_shoulder']:
            return {
                "is_handball": True,
                "decision": "Pelanggaran Handball (Gol Dianulir / Tendangan Bebas)",
                "reason": "Penyerang yang bola menyentuh tangan/lengannya (meski tidak sengaja) dan langsung menghasilkan gol atau peluang gol bersih adalah pelanggaran.",
                "law_reference": "Law 12.1 IFAB - Handling the ball (Attacker)"
            }
        else:
            return {
                "is_handball": False,
                "decision": "Bukan Handball",
                "reason": "Bola menyentuh tangan secara tidak sengaja dan tidak langsung menciptakan gol atau peluang emas.",
                "law_reference": "Law 12.1 IFAB"
            }

    # 2. Aturan Khusus Bek (Defender)
    elif player_role == 'defender':
        if hand_position in ['unnatural', 'above_shoulder']:
            return {
                "is_handball": True,
                "decision": "Pelanggaran Handball (Penalti / Tendangan Bebas Langsung)",
                "reason": "Posisi tangan bek terangkat/melebar secara tidak alami sehingga membuat area tubuh menjadi secara tidak wajar lebih besar.",
                "law_reference": "Law 12.1 IFAB - Handling the ball (Defender)"
            }
        elif hand_position == 'natural':
            return {
                "is_handball": False,
                "decision": "Bukan Handball (Permainan Berlanjut)",
                "reason": "Tangan bek berada di posisi alami dekat tubuh dan pergerakan tangan merupakan konsekuensi normal dari gerakan tubuhnya.",
                "law_reference": "Law 12.1 IFAB - Handling the ball (Defender)"
            }

    # 3. Kiper di Area Sendiri
    elif player_role == 'goalkeeper':
        return {
            "is_handball": False,
            "decision": "Bukan Handball",
            "reason": "Kiper bebas menyentuh bola dengan tangan di dalam area penaltinya sendiri (kecuali bola berasal dari back-pass rekan).",
            "law_reference": "Law 12.1 IFAB"
        }

    return {
        "is_handball": False,
        "decision": "Informasi Kurang",
        "reason": "Peran pemain atau posisi tangan belum ditentukan.",
        "law_reference": "Law 12 IFAB"
    }