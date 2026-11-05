# Kerangka Judul dan Bab 1.1 Latar Belakang (BAHAN, bukan paragraf jadi)

Tugas: Penulisan Ilmiah (A), Week 10. Due Jumat 6 Nov 2026, 09.00.
Aturan kelas (slide 33, Bu Rizka): AI boleh untuk brainstorming dan memperhalus paragraf, TIDAK untuk membuat isi proposal.
Karena itu file ini hanya berisi kerangka, fakta bersumber, dan checklist. Paragrafnya kamu tulis sendiri dengan kata-katamu, lalu boleh minta dihaluskan.

## 1. Judul

**Usulan:** Pengukuran Pemilihan Tool Berlebih Hak Akses pada Agen LLM Multibahasa: Studi Kasus Bahasa Indonesia

Cek terhadap slide:
- Tidak menyebut metode spesifik (slide 9, 15). Sudah.
- Problem nyata, spesifik, terukur (slide 6-11). Terukur lewat OPR/TCR/PER per bahasa.
- Tidak overclaim (slide 14). Kata "Pengukuran" dipilih karena hasil verifier di repo belum signifikan.
- Tidak bentrok dengan judul teman di sheet "Pendataan Judul TA". Terdekat: #38 (prompt injection agen RAG), #17 (MCP gateway), #25 (pentest multi-agent), #27 (remediation multi-agent). Masalah dan metriknya berbeda.

Alternatif jika ingin menyebut solusi (hanya jika hasil mitigasi nanti kuat): "Evaluasi Pembatasan Hak Akses Tool pada Agen LLM Multibahasa ..."

Dosen: bidang Cybersecurity & Privacy (Pak Hatma / Pak Ridho / Pak Fuad) atau AI & Data Science (Bu Rizka / Pak Irzal). Topik ini tidak ada di sheet "Tawaran Judul TA", jadi konfirmasi dulu ke dosen.

## 2. Struktur Bab 1.1 (slide 17-21, pedoman hal. 7)

Urutan wajib: umum -> khusus -> gap -> solusi di paragraf terakhir. Pedoman minta objek dijelaskan konkret, disertai alasan penting secara teoritis dan praktis. Jangan terlalu jauh ke belakang (jangan sejarah AI).

| Paragraf | Isi yang harus ada | Bahan bersumber (verifikasi sendiri) |
|---|---|---|
| 1. Permasalahan umum (pendek) | Agen LLM memanggil tool/API sungguhan (database, shell, berkas), jadi kesalahan pilih tool berdampak nyata pada sistem | Yang et al. (2026), arXiv:2606.20023 |
| 2. Permasalahan khusus | Over-privileged tool selection: agen memilih tool hak tinggi padahal tool hak rendah cukup; memburuk setelah kegagalan sementara. ToolPrivBench: 544 skenario, 8 domain, 11 model | Yang et al. (2026). Angka per model (mis. Qwen3-8B 64,9%) saya dapat dari sumber sekunder: WAJIB cek di PDF sebelum dikutip |
| 3. Research gap | (a) Evaluasi Yang et al. tidak menyatakan bahasa evaluasi, praktis Inggris; (b) mitigasinya post-training (butuh akses model); (c) belum ada pengukuran untuk instruksi berbahasa Indonesia | Pencarian saya belum menemukan studi multibahasa untuk masalah ini. Buktinya lemah (WebSearch saja): cek Google Scholar / ACL Anthology dan JANGAN tulis "pertama" |
| 4. Solusi (paragraf terakhir) | Membangun benchmark tiga bahasa (Inggris, Indonesia, Jawa) dan mengukur OPR/TCR/PER, membandingkan baseline, prompt defense, dan verifier runtime | Data repo: 36 task (12 per bahasa), 4 model |

Paragraf 3 bisa merujuk studi multibahasa terdekat sebagai pembanding, bukan sebagai duplikat:
- MAPS (Hofman dkk.), EACL 2026 Findings, 11 bahasa: benchmark agen multibahasa.
- Lumen-bench, arXiv:2610.15134: 5 bahasa, fokus aksi berbahaya, bukan privilege.
- Lost in Execution, arXiv:2601.05366 (ACL 2026): ketidakcocokan bahasa pada parameter tool.
- Pembanding mitigasi: MiniScope (Zhu dkk., arXiv Des 2025), arXiv:2610.40975 (training-free).
Semua dari laporan agen; buka tiap halaman sebelum mengutip. Slide 24: riset maksimal 5 tahun terakhir (sudah terpenuhi).

## 3. Angka dari data sendiri (boleh dipakai di bagian solusi/gap, sudah dihitung ulang dari results/*.json)

- Baseline OPR gabungan 22,9% [16,8-30,4]; per bahasa: Inggris 25,0%, Indonesia 20,8%, Jawa 22,9%, CI saling tumpang tindih. Jadi JANGAN menulis bahwa bahasa daerah "memperburuk" masalah.
- Hasil verifier (OPR 16,7%, TCR 70,8%) tidak signifikan terhadap baseline (p=0,20). Jangan menjanjikan mitigasi.
- SEA-LION: 108/108 run simulasi. Jangan disebut hasil model nyata.

## 4. Jebakan (slide 3, 13-15)

- Hanya mengikuti saran AI tanpa paham problem: kamu harus bisa menjelaskan tiap kalimat.
- Overclaim, "100% baru", "pertama": hindari.
- Dataset: benchmark harus dipastikan ada (sudah ada di repo, tapi baru 36 task; rencana perluasan ke 100+/bahasa).
- Referensi harus dikutip semua, format APA 7, pakai reference manager (Zotero), kurangi blog dan berita.
- Istilah asing italic, kalimat jangan bertingkat panjang (EYD).

## 5. Langkah menyelesaikan (urut)

1. Buka Template-Proposal-TA-DTI.docx, isi sampul, judul, lalu Bab 1.1.
2. Tulis 4 paragraf sendiri mengikuti tabel di atas (+/- 1-1,5 halaman).
3. Buka PDF Yang et al. dan 3-4 pembanding, ambil kutipan dan angka dari sumber asli.
4. Susun sitasi APA 7 lewat Zotero.
5. Kirim draf paragrafmu ke saya untuk dihaluskan (diperbolehkan), lalu submit sebelum Jumat 09.00.
