# Knowledge Mapping: Chatbot Penjelas Aturan Sepak Bola (IFAB Laws of the Game)

---

## 1. High-Level Architecture Mapping

```
                                 [INPUT PENGGUNA (Cerita / Pertanyaan Awam)]
                                                     │
                                                     ▼
                                          [NLU Preprocessing Layer]
                                 (Tokenization, Lowercasing, Stemming Sastrawi)
                                                     │
                                                     ▼
                                         [Intent & Entity Matcher]
                                   (Pencocokan Kata Kunci & Glossary Synonym)
                                                     │
                                                     ▼
                                            [Slot Filling Engine]
                                                     │
                       ┌─────────────────────────────┴─────────────────────────────┐
                       ▼                                                           ▼
            [Informasi Belum Lengkap]                                    [Informasi Lengkap]
                       │                                                           │
                       ▼                                                           ▼
           [Pertanyaan Klarifikasi]                                    [IFAB Logic Rule Evaluator]
                                                                                   │
                                                                                   ▼
                                                                      [Template Response Generator]
                                                                                   │
                                                                                   ▼
                                                                     [Jawaban Penjelasan + Dasar Law]
```

---

## 2. Core Knowledge Domain Matrix

| Law / Regulasi | Subtopik | Entity Utama (Slots) | Trigger Keywords (Bahasa Awam) | Logic Rules & Output Pengetahuan |
| :--- | :--- | :--- | :--- | :--- |
| **Law 3** *(The Players)* | Pergantian Pemain & Pergantian Gegar Otak | `sub_reason`, `player_status`, `concussion_flag` | *ganti pemain, cedera kepala, gegar otak, slot pergantian* | • Pergantian standar maks 5 pemain dalam 3 jendela waktu.<br>• Pergantian gegar otak (*concussion sub*) bersifat tambahan dan tidak mengurangi kuota pergantian normal. |
| **Law 7** *(Match Duration)* | Waktu Tambahan & Extra Time | `stoppage_reason`, `time_added` | *waktu tambahan, injury time, knp lama banget, babak tambahan* | • Waktu tambahan diberikan untuk menguji waktu yang hilang akibat: selebrasi gol, pergantian pemain, penanganan cedera, dan VAR check. |
| **Law 10** *(Determining Outcome)* | Adu Penalti & Kriteria Pemenang | `match_phase`, `penalty_shootout_stage` | *adu penalti, penentuan penalti, seri, tos-tosan* | • Adu penalti dilakukan jika laga imbang hingga *extra time* pada fase gugur.<br>• Masing-masing tim melakukan 5 tendangan awal; jika masih imbang berlanjut ke sistem *sudden death*. |
| **Law 11** *(Offside)* | Posisi Offside, Aktif/Pasif & Pengecualian | `player_position`, `action_type`, `restart_type` | *offside, orang terakhir, gak kena bola, lemparan kedalam, goal kick* | • **Aktif:** Menyentuh bola, menghalangi pandangan lawan, atau mendapat keuntungan pantulan.<br>• **Pasif:** Berdiri di posisi offside tetapi tidak mempengaruhi permainan.<br>• **Pengecualian:** Tidak ada offside dari *Throw-in*, *Goal Kick*, dan *Corner Kick*. |
| **Law 12** *(Fouls & Misconduct)* | Handball, Kartu (Kuning/Merah), DOGSO & Advantage | `player_role`, `hand_position`, `contact_intensity`, `is_dogso`, `possession_status` | *handball, gak sengaja kena tangan, kartu merah, kartu kuning, orang terakhir, advantage, dibiarkan main* | • **Handball Penyerang:** Memegang bola/terkena tangan (meski tidak sengaja) yang berujung gol = Pelanggaran.<br>• **Handball Bek:** Kena tangan alami = Bukan handball; Tangan memperbesar area tubuh = Handball.<br>• **DOGSO:** Menggagalkan peluang emas gol = Kartu Merah.<br>• **Advantage:** Wasit melanjutkan laga jika tim yang dilanggar tetap memegang kontrol bola yang menguntungkan. |
| **Law 13** *(Free Kicks)* | Pagar Betis & Prosedur Tendangan Bebas | `freekick_type`, `wall_distance` | *tendangan bebas, pagar betis, free kick tidak langsung, jarak 9 meter* | • Tendangan bebas langsung bisa langsung cetak gol; tidak langsung harus menyentuh pemain lain terlebih dahulu.<br>• Pagar betis lawan wajib berjarak minimal 9.15 meter (10 yard) dari bola. |
| **Law 14** *(Penalty Kick)* | Prosedur Penalti & Encroachment | `goalkeeper_feet`, `encroachment`, `kick_result` | *penalti diulang, kiper maju, nyelonong masuk kotak, tendangan penalti* | • Kiper wajib menapakkan minimal 1 kaki di garis gawang saat bola ditendang.<br>• *Encroachment:* Jika pemain lawan/rekan menerobos kotak penalti sebelum bola ditendang dan mempengaruhi hasil, penalti diulang. |
| **VAR Protocol** | Intervensi VAR & Clear/Obvious Error | `incident_type`, `error_severity` | *cek VAR, gak liat monitor, kartu kuning VAR, clear and obvious error* | • **4 Kategori VAR:** (1) Gol / Tidak Gol, (2) Penalti / Tidak Penalti, (3) Kartu Merah Langsung, (4) Salah Identitas Pemain.<br>• VAR tidak berintervensi untuk kartu kuning biasa atau pelanggaran rutin di luar 4 kategori. |

---

## 3. Slot Filling & Intent Recognition Framework

```json
{
  "intents": {
    "check_handball": {
      "law_reference": "Law 12 IFAB",
      "required_slots": ["player_role", "hand_position"],
      "optional_slots": ["is_goal_result"],
      "clarification_prompts": {
        "player_role": "Apakah bola mengenai tangan pemain penyerang atau pemain bertahan/bek?",
        "hand_position": "Apakah posisi tangan terangkat lebar (memperbesar tubuh) atau menempel alami di samping badan?"
      }
    },
    "check_offside": {
      "law_reference": "Law 11 IFAB",
      "required_slots": ["player_position", "action_type"],
      "optional_slots": ["restart_type"],
      "clarification_prompts": {
        "action_type": "Apakah pemain tersebut menyentuh bola, mengalangi kiper, atau hanya berdiri pasif?"
      }
    },
    "check_var_eligibility": {
      "law_reference": "VAR Protocol IFAB",
      "required_slots": ["incident_type"],
      "clarification_prompts": {
        "incident_type": "Kejadian apa yang ingin Anda cek? (Gol, Penalti, Kartu Merah Langsung, atau Kartu Kuning?)"
      }
    }
  }
}
```

---

## 4. Entity & Synonym Dictionary (Glossary Mapping)

```json
{
  "synonyms": {
    "DOGSO": ["orang terakhir", "pemain terakhir", "ditarik pas mau gol", "peluang emas gol", "ditarik dari belakang"],
    "SPA": ["tarik baju", "tackle dari belakang", "potong serangan balik", "pelanggaran taktis"],
    "Advantage": ["dibiarkan main", "gak ditiup", "main terus", "dikasih keuntungan", "tidak peluit"],
    "Encroachment": ["nyelonong masuk", "masuk kotak penalti duluan", "pemain lari duluan pas penalti"],
    "Handball": ["kena tangan", "tangan aktif", "bola kena lengan", "menyentuh tangan"],
    "Concussion": ["cedera kepala", "gegar otak", "kepala benturan", "ganti pemain cedera kepala"]
  }
}
```

---

## 5. Decision Tree Logic Examples

### 5.1 Decision Tree: Law 12 - Handball
```text
[Bola Menyentuh Tangan/Lengan]
  │
  ├── Is Player Attacker?
  │     ├── YES ──► Is it direct goal or goal-scoring chance?
  │     │             ├── YES ──► [HANDBALL (Gol Dianulir / Pelanggaran)]
  │     │             └── NO  ──► [HANDBALL]
  │     └── NO (Defender)
  │           │
  │           ├── Is hand position natural / close to body?
  │           │     ├── YES ──► [NOT HANDBALL (Permainan Lanjut)]
  │           │     └── NO  ──► [HANDBALL]
```

### 5.2 Decision Tree: VAR Protocol
```text
[Pengguna Bertanya Intervensi VAR]
  │
  ├── Is incident type IN ['Goal', 'Penalty', 'Direct Red Card', 'Mistaken Identity']?
  │     ├── NO  ──► [VAR TIDAK BOLEH INTERVENSI (Contoh: Kartu Kuning, Corner Kick)]
  │     └── YES ──► Is there a 'Clear and Obvious Error'?
  │                   ├── YES ──► [VAR INTERVENSI / ON-FIELD REVIEW]
  │                   └── NO  ──► [KEPUTUSAN WASIT UTAMA TETAP BERLAKU]
```

