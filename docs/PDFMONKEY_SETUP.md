# PDFMonkey Setup Guide

Dokumen ini menjelaskan cara mengaktifkan integrasi PDFMonkey tanpa menulis API key ke repository.

## Tujuan

Repository ini sudah disiapkan agar DIL tinggal menambahkan secret berikut di GitHub Actions:

- `PDFMONKEY_API_KEY`
- `PDFMONKEY_TEMPLATE_ID`
- `PDFMONKEY_BASE_URL` opsional

## Cara Menambahkan Secret

1. Buka repository GitHub.
2. Masuk ke `Settings`.
3. Pilih `Secrets and variables`.
4. Pilih `Actions`.
5. Klik `New repository secret`.
6. Tambahkan:

```text
Name:
PDFMONKEY_API_KEY

Secret:
isi API key PDFMonkey Anda
```

7. Tambahkan lagi:

```text
Name:
PDFMONKEY_TEMPLATE_ID

Secret:
isi Template ID PDFMonkey Anda
```

8. Opsional jika endpoint perlu diganti:

```text
Name:
PDFMONKEY_BASE_URL

Secret:
https://api.pdfmonkey.io/api/v1
```

## File Integrasi yang Sudah Disiapkan

- `src/integrations/pdfmonkey_client.py`
- `scripts/generate_pdfmonkey_sample.py`

## Cara Kerja

1. Script membaca secret dari environment variable.
2. Script membuat payload ebook contoh.
3. Payload dikirim ke PDFMonkey.
4. PDFMonkey membuat dokumen dari template.
5. Hasil respons disimpan ke folder `output/`.

## Catatan Keamanan

- Jangan menulis API key di file kode.
- Jangan menulis API key di Notion.
- Jangan menulis API key di issue GitHub.
- Jangan menulis API key di README publik.
- Jika API key pernah terkirim di chat, rotate atau revoke dari dashboard PDFMonkey.

## Langkah Berikutnya

Setelah secret ditambahkan, workflow GitHub Actions dapat dibuat atau dijalankan untuk menguji integrasi PDFMonkey.
