# HOW TO USE
# DIL Autonomous Ebook Agent
# Versi: 1.0

## Langkah 1: Tambahkan API Key ke GitHub Secrets

1. Buka repository di GitHub.
2. Klik Settings.
3. Klik Secrets and variables di sidebar.
4. Klik Actions.
5. Klik New repository secret.
6. Tambahkan setiap API key sesuai nama di config/model_pool.json.

## Langkah 2: Buat GitHub Issue

1. Buka tab Issues di repository.
2. Klik New issue.
3. Pilih template Generate Ebook.
4. Isi semua field.
5. Klik Submit new issue.

## Langkah 3: Mulai Pipeline

1. Setelah issue dibuat, tambahkan label agent-run.
2. Pipeline akan otomatis berjalan di GitHub Actions.

## Langkah 4: Pantau Progress

1. Buka tab Actions di repository.
2. Klik run yang sedang berjalan untuk melihat log.

## Langkah 5: Unduh Hasil

1. Setelah pipeline selesai, buka tab Actions.
2. Klik run yang sudah selesai.
3. Scroll ke bawah ke bagian Artifacts.
4. Klik artifact untuk mengunduh.

## Langkah 6: Baca Laporan

Buka run_report.json dan cost_report.json untuk melihat status, skor kualitas, dan biaya yang terpakai.
