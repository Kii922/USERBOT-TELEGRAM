# Projek UBot

Userbot Telegram untuk mengirim pesan promosi ke beberapa grup sekaligus. Dibangun dengan **Pyrogram** (MTProto).

## Fitur

- **Kirim pesan ke banyak grup** — Satu perintah, terkirim ke semua grup target
- **Kirim media** — Support foto, video, dokumen (reply + `/send`)
- **Scan grup otomatis** — Deteksi semua grup yang kamu ikuti
- **Manage grup target** — Tambah, hapus, aktifkan/nonaktifkan grup
- **Anti-spam** — Delay otomatis antar pengiriman (configurable)
- **Retry otomatis** — Jika kena FloodWait, bot tunggu lalu coba lagi
- **Support Topics/Forum** — Kirim ke topic tertentu di grup forum
- **Logging** — Semua pengiriman dicatat di database

## Prasyarat

- Akun Telegram
- API ID & API Hash (dari https://my.telegram.org)
- **Pilih salah satu:**
  - Docker & Docker Compose (direkomendasikan)
  - Python 3.10+

## Dapatkan API Credentials

1. Buka https://my.telegram.org dan login dengan nomor telepon
2. Klik **"API development tools"**
3. Buat aplikasi baru (isi nama & deskripsi bebas)
4. Catat **API ID** (angka) dan **API Hash** (string panjang)

---

## Instalasi dengan Docker (Direkomendasikan)


### 1. Install Docker (jika belum)

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
```

> **Penting:** Setelah `usermod`, logout dan login kembali supaya group `docker` aktif.

### 2. Clone / Download & Setup

```bash
git clone <repo-url>
cd projek_ubot
cp .env.example .env
nano .env   # isi API_ID dan API_HASH
```

### 3. Login Pertama Kali (Wajib 1x)

Login harus dilakukan secara interaktif karena Pyrogram butuh input nomor telepon & OTP:

```bash
./start.sh docker login
```

Atau manual:

```bash
docker compose run --rm promo-bot
```

- Masukkan **nomor telepon** (format: +62812xxxx)
- Masukkan **kode OTP** yang dikirim Telegram
- Jika punya 2FA, masukkan password
- Setelah login berhasil, tekan `Ctrl+C`
- Session disimpan di folder `data/` — tidak perlu login ulang

### 4. Jalankan Bot (Background)

```bash
./start.sh docker
# atau manual:
docker compose up -d --build
```

### Perintah Docker Lainnya

```bash
./start.sh docker logs   # Lihat log bot
./start.sh docker stop   # Hentikan bot
docker compose restart   # Restart bot
```

---

## Instalasi Lokal (Tanpa Docker)

### 1. Clone & Setup

```bash
git clone <repo-url>
cd projek_ubot
cp .env.example .env
nano .env   # isi API_ID dan API_HASH
```

### 2. Jalankan dengan Script

```bash
chmod +x start.sh
./start.sh
```

Script ini otomatis: buat virtual environment, install dependencies, dan jalankan bot.

### Atau Manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

**Login pertama kali:**
- Bot akan meminta **nomor telepon** Telegram kamu
- Masukkan **kode OTP** yang dikirim Telegram
- Jika punya 2FA, masukkan password-nya
- Session disimpan di folder `data/` — tidak perlu login ulang

## Cara Penggunaan

Kirim perintah di **Saved Messages** (chat dengan diri sendiri) untuk privasi.

### Manage Grup Target

```
/groups scan              — Scan & tambahkan semua grup yang kamu ikuti
/groups list              — Lihat daftar grup target
/groups add               — Tambah grup (kirim di dalam grup/topic)
/groups add -1001234567   — Tambah grup via chat ID
/groups add -1001234567 99 — Tambah grup + set topic #99
/groups remove -1001234567 — Hapus grup dari target
/groups on -1001234567    — Aktifkan grup
/groups off -1001234567   — Nonaktifkan grup
```

### Topics (Grup Forum)

Untuk grup yang menggunakan Topics:

```
/settopic                          — Set topic (kirim di dalam topic)
/groups topics -1001234567         — Lihat daftar topic di grup
/groups topic -1001234567 99       — Set topic target via ID
/groups topic -1001234567 0        — Reset ke General
/groups add -1001234567 99         — Tambah grup + set topic sekaligus
```

**Cara paling mudah:**
1. Buka grup forum → masuk ke **topic yang diinginkan**
2. Ketik `/groups add` atau `/settopic`
3. Selesai! Pesan promosi akan masuk ke topic itu

### Kirim Pesan Promosi

```
/send Pesan promosi kamu di sini!
```

Untuk kirim dengan media (foto/video):
1. Reply ke foto/video yang ingin dikirim
2. Ketik `/send` atau `/send Caption baru untuk media`

### Perintah Lainnya

```
/sendpreview <pesan>  — Preview pesan sebelum kirim
/status               — Lihat status bot & jumlah grup
/help                 — Tampilkan panduan
```

## Contoh Alur Penggunaan

```
Kamu: /groups scan
Bot:  Scan selesai! Ditemukan: 15 grup. Ditambahkan: 15 grup baru.

Kamu: /groups list
Bot:  1. [ON] Grup Jual Beli Bandung (ID: -100123...)
      2. [ON] Marketplace Indonesia (ID: -100456...)
      ...

Kamu: /send 🔥 PROMO HARI INI! Diskon 50% semua produk! Order WA: 08123456789

Bot:  Mengirim ke 15 grup...
      Selesai! 14/15 pesan terkirim.
      Berhasil:
        + Grup Jual Beli Bandung
        + Marketplace Indonesia
        ...
      Gagal:
        - Grup Tertutup: Tidak punya izin menulis
```

## Konfigurasi

| Variable | Default | Keterangan |
|----------|---------|------------|
| `API_ID` | — | API ID dari my.telegram.org (wajib) |
| `API_HASH` | — | API Hash dari my.telegram.org (wajib) |
| `TIMEZONE` | `Asia/Jakarta` | Timezone untuk logging |
| `MIN_DELAY` | `3` | Delay minimum antar pesan (detik) |
| `MAX_DELAY` | `7` | Delay maksimum antar pesan (detik) |
| `DB_PATH` | `promo_bot.db` | Path file database SQLite |

## Struktur Proyek

```
projek_ubot/
├── bot.py              # Entry point utama
├── config.py           # Konfigurasi & environment
├── database.py         # Database SQLite (grup & log)
├── sender.py           # Logika kirim pesan ke banyak grup
├── handlers/
│   ├── __init__.py     # Register semua handlers
│   ├── groups.py       # Command /groups (manage grup target)
│   ├── send.py         # Command /send (kirim promosi)
│   └── help.py         # Command /help, /start, /status
├── data/               # Data persistent (session, database)
│   ├── promo_userbot.session
│   └── promo_bot.db
├── Dockerfile          # Docker image
├── docker-compose.yml  # Docker Compose config
├── start.sh            # Script helper
├── requirements.txt    # Dependencies
├── .env.example        # Template konfigurasi
├── .gitignore          # File yang diabaikan git
└── README.md           # Dokumentasi
```

## Tips Keamanan & Anti-Ban

- **Jangan spam**: Mulai dari 5-10 grup, naikkan bertahap
- **Variasi pesan**: Ubah sedikit teks setiap kirim
- **Batasi frekuensi**: Max 2-3x promo per hari per grup
- **Delay cukup**: Gunakan MIN_DELAY=5, MAX_DELAY=10 untuk aman
- **Akun mature**: Gunakan akun yang sudah lama, bukan akun baru
- **Jangan share session**: File `.session` adalah akses ke akun kamu

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `API_ID dan API_HASH belum diatur` | Isi file `.env` dengan benar |
| `FloodWait` | Bot otomatis handle, tapi naikkan delay jika sering terjadi |
| `ChatWriteForbidden` | Kamu tidak punya izin menulis di grup tersebut |
| `ChannelPrivate` | Kamu sudah bukan member grup tersebut |
| `SessionPasswordNeeded` | Masukkan password 2FA saat login |

## Roadmap

- [x] Fase 1: Kirim pesan ke beberapa grup
- [x] Fase 1.5: Support Topics/Forum
