# X Scraper Tools

Dua script ini bertujuan untuk melakukan scraping pada platform **X (sebelumnya Twitter)**. Script pertama digunakan untuk mengambil tweet berdasarkan kata kunci atau hashtag, sedangkan script kedua digunakan untuk mengambil replies dari sebuah tweet tertentu.

## 📋 Daftar Isi
- [Fitur](#-fitur)
  - [Script 1](#script-1-scrape_tweetpy)
  - [Script 2](#script-2-scrape_repliespy)
- [Persyaratan](#%EF%B8%8F-persyaratan)
- [Instalasi Dependensi](#instalasi-dependensi)
- [Cara Menggunakan](#cara-menggunakan)
  - [Script 1: Scrape Tweet Berdasarkan Kata Kunci atau Hashtag](#script-1-scrape-tweet-berdasarkan-keyword-atau-hashtag)
  - [Script 2: Scrape Replies pada Sebuah Tweet](#script-2-scrape-replies-pada-sebuah-tweet)
- [Struktur Output CSV](#-struktur-output-csv)
- [Catatan](#%EF%B8%8F-catatan)

## ✨ Fitur
### Script 1: `scrape_tweet.py`
1. **Scrape berdasarkan Pencarian:**
   - Mengambil tweet dari tahun tertentu.
   - Memungkinkan pengguna memilih jenis pencarian (hashtag atau keyword).
2. **Autentikasi dengan Token:**
   - Menggunakan `auth_token` untuk akses yang lebih lengkap terhadap data di platform X.
3. **Filter Tahun Tweet:**
   - Memungkinkan pengguna menentukan **tahun** untuk tweet yang akan diambil.
4. **URL Encoding Otomatis:**
   - Mengubah karakter spesial di keyword menjadi format URL encoding untuk pencarian yang lebih akurat.
5. **Penghapusan Duplikasi Tweet:**
   - Menggunakan `tweet_id` untuk memastikan tidak ada duplikasi tweet dalam hasil scraping.
6. **Format Data yang Diperoleh:**
   - Username
   - Timestamp (diformat menjadi `dd-mm-yyyy hh:mm:ss`)
   - Isi Tweet
   - URL Tweet
7. **Penyimpanan ke CSV:**
   - Hasil scraping disimpan dalam file CSV dengan nama file berdasarkan keyword/hashtag dan tahun pencarian.
8. **Progress Bar:**
   - Menggunakan `tqdm` untuk menunjukkan progress scraping.
  
### Script 2: `scrape_replies.py`
1. **Scrape Replies pada Sebuah Tweet:**
   - Mengambil replies dari sebuah tweet tertentu berdasarkan URL tweet.
2. **Autentikasi dengan Token:**
   - Menggunakan `auth_token` untuk akses yang lebih lengkap terhadap data di platform X.
3. **Penghapusan Duplikasi Replies:**
   - Menggunakan URL reply untuk memastikan tidak ada duplikasi data.
4. **Format Data yang Diperoleh:**
   - Display Name (Nama pengguna yang ditampilkan)
   - Username (Handle pengguna)
   - Timestamp (diformat menjadi `dd-mm-yyyy hh:mm:ss`)
   - Isi Reply
   - URL Reply
5. **Scroll Otomatis untuk Memuat Replies Tambahan:**
   - Melakukan scroll otomatis untuk memuat lebih banyak replies jika jumlah replies yang diminta belum terpenuhi.
6. **Progress Bar:**
   - Menggunakan `alive_progress` untuk menunjukkan animasi progress scraping.
7. **Menyimpanan ke CSV:**
   - Menyimpan data replies dalam file CSV yang ditentukan pengguna.
8. **Handling Timestamp Format:**
   - Konversi otomatis dari format ISO 8601 ke format `dd-mm-yyyy hh:mm:ss`.

## 🛠️ Persyaratan
- **Python** (versi 3.7 atau lebih tinggi)
- **Dependensi Python**:
  - `playwright`
  - `colorama`
  - `tqdm`
  - `alive-progress`
  - `unidecode`
- **Token autentikasi** dari akun X (platform sebelumnya dikenal sebagai Twitter).

### Instalasi Dependensi
Jalankan perintah berikut untuk menginstal semua pustaka yang dibutuhkan:
```bash
pip install playwright colorama tqdm alive-progress unidecode
playwright install
```

## Cara Menggunakan
### Script 1: Scrape Tweet Berdasarkan Keyword atau Hashtag.
1. ```bash
   git clone https://github.com/resaend/twitter-scraping/
   ```
2. ```bash
   cd twitter-scraping
   ```
3. **Masukkan token autentikasi Anda pada variabel auth_token di script**.
4. Jalankan script: `python scrape_tweet.py`
5. Pilih jenis pencarian:
   - Cari berdasarkan hashtag (tanpa simbol #)
   - Cari berdasarkan kata kunci
6. Masukkan jumlah maksimum tweet yang ingin diambil.
7. Masukkan tahun pencarian.
8. Hasil akan disimpan dalam file CSV dengan format: <search_term>_tweets_<year>.csv.

Contoh Output CSV		
			
| username      | timestamp       | tweet_text      |   tweet_url      |
|----------------|----------------|----------------|------------------|
| example_user | 25-12-2024 10:15:45 | Contoh tweet |https://x.com/example_user/status/123456789 |

### Script 2: Scrape Replies pada Sebuah Tweet.
1. ```bash
   git clone https://github.com/resaend/twitter-scraping/
   ```
2. ```bash
   cd twitter-scraping
   ```
3. Masukkan token autentikasi Anda pada variabel `auth_token` di script.
4. Jalankan script
   `python scrape_replies.py`
5. Masukkan URL tweet yang ingin di-scrape.
6. Masukkan jumlah replies maksimum yang ingin diambil.
7. Hasil akan disimpan dalam file CSV dengan nama `replies.csv`.

Contoh Output CSV
| display_name      | username       | timestamp      |   tweet_text      | tweet_url |
|----------------|----------------|----------------|------------------| --------|
| Contoh Nama | example_user |25-12-2024 10:15:45 |Contoh reply | https://x.com/example_user/status/123456789 |

---
## 📂 Struktur Output CSV
- **display_name**: Nama pengguna akun X.
- **username**: Username pengguna akun X.
- **timestamp**: Waktu tweet diterbitkan (format: dd-mm-yyyy hh:mm:ss).
- **tweet_text**: Isi teks tweet atau reply.
- **tweet_url**: URL dari tweet atau reply.

## ⚠️ Catatan
- Pastikan token autentikasi Anda valid. Jika tidak, proses scraping akan gagal.
- Script ini hanya dapat digunakan untuk mengambil data publik.
- Gunakan script ini sesuai dengan kebijakan platform X.
- **For educational purpose only!**
  

[Created with ❤ by Res](https://www.facebook.com/resa.endrawan.56/)
