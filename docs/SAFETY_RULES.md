# SAFETY RULES
# DIL Autonomous Ebook Agent
# Versi: 1.0

## Aturan Konten

1. Semua instruksi yang berpotensi berbahaya wajib diberi peringatan yang jelas.
2. Peringatan bahaya harus spesifik, bukan generik.
3. Dilarang memberikan instruksi yang dapat membahayakan keselamatan jiwa tanpa konteks keselamatan yang lengkap.
4. Semua contoh perhitungan harus menggunakan nilai yang realistis dan tidak menyesatkan pembaca pemula.
5. Dilarang membuat klaim teknis yang tidak dapat diverifikasi.

## Aturan API dan Sistem

1. Jangan pernah menyimpan API key di file kode atau konfigurasi.
2. Jangan pernah mencetak nilai API key di log manapun.
3. Jangan menggunakan scraping terhadap layanan yang tidak punya API resmi.
4. Semua tindakan berisiko harus melalui human approval gate.

## Aturan Log

1. Logger wajib menyensor nilai yang terlihat seperti API key.
2. Error log tidak boleh menampilkan stack trace yang mengandung secret.
3. Semua output ke console harus aman untuk dilihat di log publik.
