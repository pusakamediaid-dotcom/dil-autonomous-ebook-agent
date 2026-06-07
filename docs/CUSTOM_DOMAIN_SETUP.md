# Panduan Setup Custom Domain — agent.pusakamedia.id

Dokumen ini berisi instruksi yang harus dilakukan **DIL** (sebagai pemilik domain `pusakamedia.id`) agar website pada folder `/docs` dapat diakses melalui `http://agent.pusakamedia.id/`.

---

## 1. Target

- **Domain tujuan**: `agent.pusakamedia.id`
- **Repository**: `pusakamediaid-dotcom/dil-autonomous-ebook-agent`
- **Source GitHub Pages**: branch `main`, folder `/docs`

File `docs/CNAME` sudah berisi `agent.pusakamedia.id` (tanpa `http://`, tanpa slash, tanpa spasi).

---

## 2. DNS Record yang Harus Dibuat DIL

Buka panel DNS provider domain `pusakamedia.id` (mis. Cloudflare, Niagahoster, IDwebhost, Domainesia, Rumahweb, dsb.) lalu tambahkan satu record berikut:

| Field | Nilai |
|---|---|
| Type | `CNAME` |
| Name / Host | `agent` |
| Target / Value | `pusakamediaid-dotcom.github.io` |
| TTL | `Auto` (atau `3600`) |
| Proxy (jika Cloudflare) | **DNS only** (awan abu-abu) untuk verifikasi awal. Setelah HTTPS GitHub aktif, boleh dijadikan Proxied. |

> Catatan: isi **Target** dengan `pusakamediaid-dotcom.github.io` saja. **Jangan** isi dengan path repository (jangan tambahkan `/dil-autonomous-ebook-agent`). GitHub Pages otomatis mengarahkan ke repository berdasarkan file CNAME.

### Penulisan yang benar vs salah

| Benar | Salah |
|---|---|
| `agent.pusakamedia.id` | `http://agent.pusakamedia.id/` |
| (di field CNAME repo) | `https://agent.pusakamedia.id/` |
| | `agent.pusakamedia.id/` |
| `pusakamediaid-dotcom.github.io` | `pusakamediaid-dotcom.github.io/dil-autonomous-ebook-agent` |
| (di field DNS Target) | `https://pusakamediaid-dotcom.github.io` |

---

## 3. Pengaturan GitHub Pages

Setelah DNS record dibuat:

1. Buka **Settings → Pages** pada repository.
2. Pastikan:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
3. Di kolom **Custom domain**, isi: `agent.pusakamedia.id` lalu klik **Save**.
4. Tunggu beberapa menit hingga muncul tanda centang hijau "DNS check successful".
5. Centang opsi **Enforce HTTPS** setelah sertifikat berhasil diterbitkan oleh GitHub (biasanya 5–30 menit setelah DNS valid).

---

## 4. Propagasi DNS

- Waktu propagasi DNS: **5 menit hingga 24 jam** (tergantung provider dan TTL).
- Cek propagasi:
  - <https://dnschecker.org/#CNAME/agent.pusakamedia.id>
  - atau jalankan: `dig agent.pusakamedia.id CNAME +short`
- Jika hasilnya `pusakamediaid-dotcom.github.io.` → DNS sudah benar.

---

## 5. Troubleshooting

### A. Halaman menampilkan 404
- Pastikan **Source** GitHub Pages adalah `main` / `/docs` (bukan `gh-pages`, bukan GitHub Actions saja).
- Pastikan file `docs/CNAME` ada dan isinya **persis** `agent.pusakamedia.id`.
- Pastikan field **Custom domain** di Settings → Pages terisi `agent.pusakamedia.id` dan tersimpan.

### B. "DNS check unsuccessful"
- Tunggu hingga propagasi selesai.
- Pastikan record CNAME mengarah ke `pusakamediaid-dotcom.github.io` (tanpa path).
- Jika menggunakan Cloudflare proxy, sementara matikan proxy (awan abu-abu).

### C. HTTPS tidak aktif
- Aktifkan HTTPS hanya setelah DNS valid.
- Hapus dan isi ulang field Custom domain di Settings → Pages untuk memicu re-issue sertifikat.

### D. Domain salah arah (mengarah ke repo lain)
- Pastikan tidak ada repo lain milik organisasi/user yang juga memakai CNAME `agent.pusakamedia.id`.

---

## 6. Checklist DIL

- [ ] Buat DNS CNAME `agent` → `pusakamediaid-dotcom.github.io`
- [ ] Tunggu propagasi DNS selesai (cek via dnschecker.org)
- [ ] Set **Custom domain** di Settings → Pages: `agent.pusakamedia.id`
- [ ] Tunggu HTTPS sertifikat aktif
- [ ] Centang **Enforce HTTPS**
- [ ] Buka <http://agent.pusakamedia.id/> dan verifikasi tampilan landing page

---

*Dokumen ini adalah panduan instruksi DNS. Tidak ada perubahan DNS yang dapat dilakukan otomatis dari repository — langkah-langkah di atas harus dilakukan manual oleh DIL.*
