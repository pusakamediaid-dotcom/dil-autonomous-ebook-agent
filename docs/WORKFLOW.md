# WORKFLOW
# DIL Autonomous Ebook Agent
# Versi: 1.0

## Alur Kerja Standar

1. Buat GitHub Issue menggunakan template generate_ebook.yml.
2. Isi semua field yang diperlukan.
3. Tambahkan label agent-run untuk memulai pipeline.
4. Tunggu hasil di tab Actions.
5. Unduh artifact dari tab Actions > Artifacts.
6. Verifikasi hasil dan baca run_report.json.

## Mode yang Tersedia

- planning: hanya membuat rencana kerja.
- test: membuat 1 bab pendek untuk uji coba.
- session: membuat 1 sesi ebook.
- full: membuat ebook penuh dan memerlukan approval.
- review: hanya mengecek output yang ada.
- repair: memperbaiki output yang bermasalah.
- html: konversi Markdown ke HTML.
- pdf: konversi Markdown ke PDF.

## Artifact yang Dihasilkan

Lihat config/output_rules.json untuk daftar output per mode.
