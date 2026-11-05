---
name: require-tool-line
enabled: true
event: prompt
pattern: .
---

Aturan CLAUDE.md, berlaku tiap prompt:
1. Klasifikasikan tugas. Riset, verifikasi, atau multi-langkah bukan tugas sepele: pakai skill/MCP yang cocok.
2. Tulis satu baris `Tool: <nama> (<alasan>)` sebelum mulai kerja. Di akhir sebut tool yang benar-benar dipakai.
3. Kalau `.claude/office-team.json` belum ada, bangun tim agent dulu. Tugas non-sepele diserahkan ke agent sesuai routing `description`.
