def evaluate_offside(player_position: str, action_type: str, restart_type: str = None) -> dict:
    """
    Evaluasi Aturan Law 11 - Offside berdasarkan variabel kejadian.
    
    Parameters:
    - player_position: 'offside_position' | 'onside_position'
    - action_type: 'touch_ball' | 'interfere_opponent' | 'gain_advantage' | 'passive'
    - restart_type: 'throw_in' | 'goal_kick' | 'corner_kick' | 'open_play'
    """
    # 1. Pengecualian Aturan (Exceptions)
    if restart_type in ['throw_in', 'goal_kick', 'corner_kick']:
        return {
            "is_offence": False,
            "decision": "Bukan Pelanggaran Offside",
            "reason": f"Offside tidak pernah berlaku jika bola diterima langsung dari {restart_type.replace('_', ' ').title()}.",
            "law_reference": "Law 11.4 IFAB - Exceptions"
        }
    
    # 2. Pengecekan Posisi Dasar
    if player_position == 'onside_position':
        return {
            "is_offence": False,
            "decision": "Bukan Pelanggaran Offside",
            "reason": "Pemain berada di posisi onside saat bola ditendang/diumpan oleh rekan tim.",
            "law_reference": "Law 11.1 IFAB - Offside Position"
        }
    
    # 3. Pengecekan Keterlibatan Aktif (Offside Offence)
    if player_position == 'offside_position':
        if action_type in ['touch_ball', 'interfere_opponent', 'gain_advantage']:
            action_desc = {
                'touch_ball': 'menyentuh/memainkan bola',
                'interfere_opponent': 'menghalangi pandangan/pergerakan kiper atau bek lawan',
                'gain_advantage': 'memanfaatkan pantulan bola dari tiang gawang atau penyelamatan lawan'
            }
            return {
                "is_offence": True,
                "decision": "Pelanggaran Offside (Tendangan Bebas Tidak Langsung)",
                "reason": f"Pemain berada di posisi offside dan aktif secara fisik/taktis dengan {action_desc.get(action_type)}.",
                "law_reference": "Law 11.2 IFAB - Offside Offence"
            }
        elif action_type == 'passive':
            return {
                "is_offence": False,
                "decision": "Bukan Pelanggaran Offside (Permainan Berlanjut)",
                "reason": "Pemain memang berada di posisi offside, namun ia diam/pasif dan tidak terlibat dalam aksi permainan.",
                "law_reference": "Law 11.2 IFAB - Offside Offence"
            }

    return {
        "is_offence": False,
        "decision": "Informasi Kurang",
        "reason": "Detail pergerakan pemain belum cukup untuk mengambil keputusan.",
        "law_reference": "Law 11 IFAB"
    }