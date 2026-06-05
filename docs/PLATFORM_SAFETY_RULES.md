# Platform Safety Rules - DIL Content & Income Agent

## Aturan Keamanan Platform

Dokumen ini menjelaskan aturan keamanan yang harus dipatuhi saat menggunakan agent penghasilan.

## Larangan Mutlak

### 1. Login Scraping
**DILANGKAN SECARA MUTLAK**

- Jangan mengambil data dari halaman yang butuh login
- Jangan menggunakan cookie akun user
- Jangan membuat bot yang membuka halaman login
- Jangan menyimpan credential login

### 2. Cookie Stealing
**DILANGKAN SECARA MUTLAK**

- Jangan mengambil cookie dari browser user
- Jangan menyimpan session cookie
- Jangan menggunakan cookie untuk akses API

### 3. Automated Browsing
**DILANGKAN SECARA MUTLAK**

- Jangan membuka banyak halaman secara otomatis
- Jangan menggunakan headless browser untuk scraping
- Jangan melanggar rate limit platform

### 4. Spam
**DILANGKAN SECARA MUTLAK**

- Jangan posting komentar spam
- Jangan kirim DM spam
- Jangan posting konten berulang
- Jangan menggunakan bot untuk engagement

### 5. Fake News
**DILANGKAN SECARA MUTLAK**

- Jangan membuat berita palsu
- Jangan menyebarkan hoaks
- Jangan membuat klaim tanpa sumber
- Jangan menyalin artikel penuh

### 6. Copyright Violation
**DILANGKAN SECARA MUTLAK**

- Jangan menyalin artikel penuh
- Jangan menggunakan gambar tanpa izin
- Jangan mengklaim karya orang lain

## Sumber Data yang Diizinkan

### ✅ Diizinkan
1. **API Resmi** — Menggunakan API yang disediakan platform secara resmi
2. **RSS Feed** — Menggunakan RSS feed publik dari media resmi
3. **Halaman Publik** — Mengakses halaman yang tidak butuh login
4. **Input Manual** — User memasukkan data secara manual
5. **CSV Upload** — User mengupload data dalam format CSV
6. **Situs Resmi** — Mengakses situs resmi lembaga/organisasi

### ❌ Dilarang
1. **Login Scraping** — Mengambil data dari halaman login
2. **Cookie Access** — Menggunakan cookie untuk akses
3. **Automated Browsing** — Membuka banyak halaman otomatis
4. **Rate Limit Abuse** — Melanggar batas request
5. **Full Article Copy** — Menyalin artikel penuh
6. **Fake Sources** — Menggunakan sumber palsu

## Aturan Platform Spesifik

### Tokopedia
- ✅ API resmi jika tersedia
- ✅ Halaman produk publik
- ✅ Input manual
- ❌ Scraping halaman login
- ❌ Menggunakan cookie
- ❌ Bot otomatis

### Shopee
- ✅ API resmi jika tersedia
- ✅ Halaman produk publik
- ✅ Input manual
- ❌ Scraping halaman login
- ❌ Menggunakan cookie
- ❌ Bot otomatis

### Threads
- ✅ Posting manual
- ✅ Draft konten
- ❌ Auto-post tanpa approval
- ❌ Spam
- ❌ Bot engagement

### Google/Blog
- ✅ Konten berkualitas
- ✅ Sumber yang jelas
- ❌ Auto-post tanpa approval
- ❌ Konten spam
- ❌ Plagiarisme

## Aturan Konten Affiliate

### Disclosure Wajib
Setiap konten affiliate WAJIB menyertakan disclosure:

> Catatan: tautan ini bisa berupa link affiliate. Jika Anda membeli melalui link ini, saya bisa mendapat komisi tanpa biaya tambahan untuk Anda.

### Klaim yang Dilarang
- ❌ "Produk ini pasti menghasilkan uang"
- ❌ "Jaminan keberhasilan 100%"
- ❌ "Penghasilan pasif tanpa kerja"
- ❌ "Beli sekarang!!! Jangan sampai terlewat!"
- ❌ Testimoni palsu

### Klaim yang Diizinkan
- ✅ "Produk ini cocok untuk [target audiens]"
- ✅ "Berdasarkan riset, produk ini memiliki [fitur]"
- ✅ "Harga produk ini berkisar [rentang]"
- ✅ "Produk ini berguna untuk [tujuan praktis]"

## Aturan Konten Berita

### Sumber Wajib
Setiap konten berita WAJIB mencantumkan sumber:
- Nama media/organisasi
- URL artikel asli
- Tanggal publikasi

### Label Wajib
- **Ringkasan** — Jika konten berupa ringkasan
- **Analisis singkat** — Jika konten berupa analisis
- **Opini** — Jika konten berupa pendapat
- **Sumber:** — Selalu cantumkan sumber

### Kutipan
- Maksimal 50 kata untuk kutipan langsung
- Selalu cantumkan atribusi
- Jangan mengubah konteks kutipan

### Larangan Berita
- ❌ Berita palsu/hoaks
- ❌ Judul menyesatkan
- ❌ Konten politik provokatif
- ❌ Ujaran kebencian
- ❌ Klaim tanpa sumber
- ❌ Menyalin artikel penuh

## Batasan Posting

### Per Hari
- Maksimal 3 posting per hari
- Maksimal 15 posting per minggu
- Jeda minimal 2 jam antar posting di platform sama

### Konten
- Tidak boleh posting konten yang sama berulang
- Harus ada variasi konten
- Maksimal 2 konten serupa per minggu

### Waktu Posting
- Jam 08:00 - 21:00 WIB
- Tidak posting antara 00:00 - 06:00 WIB
- Pengurangan frekuensi di akhir pekan

## Approval Gate

Semua tindakan berikut memerlukan approval:

1. **Publikasi konten** — Posting ke platform
2. **Promosi affiliate** — Mempromosikan link affiliate
3. **Penggunaan API berbayar** — Menggunakan API yang berbayar

Tindakan berikut TIDAK memerlukan approval:

1. **Riset** — Mencari produk atau berita
2. **Draft** — Membuat draf konten
3. **Validasi** — Mengecek kepatuhan
4. **Laporan** — Membuat laporan

## Cost Guard

Semua agent memiliki cost guard:

- Batas token per run
- Batas biaya per run
- Tracking penggunaan
- Peringatan jika mendekati batas

## Compliance Agent

Compliance Agent memeriksa:

### Affiliate
- ✅ Ada disclosure
- ✅ Tidak ada klaim palsu
- ✅ Tidak ada janji penghasilan
- ✅ Tidak ada produk berbahaya
- ✅ Tidak ada spam CTA
- ✅ Tidak ada manipulasi

### Berita
- ✅ Ada sumber
- ✅ Tidak menyalin penuh
- ✅ Tidak ada hoaks
- ✅ Tidak ada klaim tanpa sumber
- ✅ Tidak ada judul menyesatkan
- ✅ Fakta dan opini dipisah

## Pelaporan Masalah

Jika Anda menemukan:

1. **Agent melanggar aturan** — Laporkan di Issue
2. **Konten tidak pantas** — Jangan publikasikan
3. **API error** — Cek log dan laporkan
4. **Saran perbaikan** — Buat Issue dengan label enhancement

## Kesimpulan

Keamanan adalah prioritas utama. Semua agent dirancang untuk:

1. **Aman** — Tidak melanggar aturan platform
2. **Legal** — Sesuai hukum dan etika
3. **Terukur** — Bisa dimonitor dan dikontrol
4. **Manual** — Tetap butuh review manusia

**Jangan pernah mengorbankan keamanan demi kecepatan atau keuntungan.**
