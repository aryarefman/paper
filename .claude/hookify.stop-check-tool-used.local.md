---
name: stop-check-tool-used
enabled: true
event: stop
pattern: .*
---

Sebelum selesai, cek:
- [ ] Ada baris `Tool:` di awal kerja dan daftar tool yang dipakai di akhir?
- [ ] Tugas non-sepele sudah diserahkan ke agent `agent-office:<id>` sesuai routing?
- [ ] Klaim diverifikasi (sumber/angka), bukan dari ingatan?
