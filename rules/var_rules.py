def evaluate_var(incident_type: str, error_severity: str = 'clear_and_obvious') -> dict:
    """
    Evaluasi Protokol VAR IFAB.
    
    Parameters:
    - incident_type: 'goal' | 'penalty' | 'direct_red_card' | 'mistaken_identity' | 'yellow_card' | 'corner_kick' | 'foul'
    - error_severity: 'clear_and_obvious' | 'subjective'
    """
    eligible_categories = ['goal', 'penalty', 'direct_red_card', 'mistaken_identity']
    
    # 1. Pengecekan Kategori Kejadian yang Boleh Di-review
    if incident_type not in eligible_categories:
        return {
            "can_review": False,
            "decision": "VAR Tidak Boleh Berintervensi",
            "reason": f"VAR hanya berwenang untuk 4 kategori utama: Gol, Penalti, Kartu Merah Langsung, dan Salah Identitas Pemain. Kejadian '{incident_type.replace('_', ' ')}' berada di luar wewenang VAR.",
            "law_reference": "VAR Protocol IFAB - Principles 1 & 2"
        }
    
    # 2. Syarat Kesalahan yang Jelas dan Nyata (Clear and Obvious Error)
    if error_severity == 'clear_and_obvious':
        category_desc = {
            'goal': 'Penentuan keabsahan Gol / Tidak Gol (offside, handball, atau pelanggaran sebelum gol)',
            'penalty': 'Penentuan Keputusan Penalti / Tidak Penalti',
            'direct_red_card': 'Penilaian Kartu Merah Langsung (bukan kartu kuning kedua)',
            'mistaken_identity': 'Koreksi Salah Identitas Pemain yang menerima kartu'
        }
        return {
            "can_review": True,
            "decision": "VAR Boleh Berintervensi (Review / On-Field Review)",
            "reason": f"Terdapat indikasi kesalahan yang jelas dan nyata (Clear and Obvious Error) pada situasi: {category_desc.get(incident_type)}.",
            "law_reference": "VAR Protocol IFAB - Principles & Reviewable Decisions"
        }
    else:
        return {
            "can_review": False,
            "decision": "Keputusan Wasit Utama Tetap Berlaku",
            "reason": "Kejadian termasuk kategori yang boleh di-review, namun insiden bersifat subjektif/tipis dan tidak memenuhi kriteria kesalahan yang jelas dan nyata (Clear and Obvious Error).",
            "law_reference": "VAR Protocol IFAB - Principles"
        }