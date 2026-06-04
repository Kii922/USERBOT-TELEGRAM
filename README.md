<div align="center">

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="120">

# 🚀 Projek UBot

### Telegram Userbot Promo System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![Pyrogram](https://img.shields.io/badge/Pyrogram-MTProto-blue?style=for-the-badge&logo=telegram)

</div>

## 🤖 Telegram Userbot Promo System

Userbot Telegram untuk mengirim pesan promosi ke banyak grup sekaligus.  
Dibangun menggunakan **Pyrogram (MTProto)** dengan sistem otomatisasi tinggi.

---

## 🧑‍💻 Contributors

![Dev](https://img.shields.io/badge/Developed%20by-kii922%20•%20devinai%20•%20chatgpt-7c3aed?style=for-the-badge)

---

## ⚡ Fitur Utama

![Features](https://img.shields.io/badge/features-full%20automation-orange?style=for-the-badge)

- 📢 Kirim pesan ke banyak grup sekaligus
- 🖼️ Support media (foto, video, dokumen)
- 🔍 Scan grup otomatis
- 🧠 Manage grup target (add/remove/on/off)
- 🛡️ Anti-spam delay system
- 🔁 Retry otomatis (FloodWait handling)
- 🧵 Support Topics / Forum group
- 📊 Logging database lengkap

---

## 📦 Prasyarat

- Akun Telegram aktif
- API ID & API HASH dari https://my.telegram.org
- Docker (recommended) atau Python 3.10+

---

## 🔑 Dapatkan API Credentials

1. Buka https://my.telegram.org  
2. Login dengan nomor Telegram  
3. Pilih **API Development Tools**  
4. Buat aplikasi baru  
5. Simpan:
   - API_ID
   - API_HASH

---

## 🐳 Instalasi Docker (Recommended)

### 1. Install Docker
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
```

---

### 2. Clone Project
```bash
git clone <repo-url>
cd projek_ubot
cp .env.example .env
nano .env
```

---

### 3. Login pertama kali
```bash
./start.sh docker login
```

---

### 4. Jalankan bot
```bash
./start.sh docker
```

---

## 💻 Instalasi Lokal

```bash
git clone <repo-url>
cd projek_ubot
cp .env.example .env
nano .env
```

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

---

## 📌 Perintah Utama

### 📁 Manage Grup
```
/groups scan
/groups list
/groups add
/groups remove <id>
/groups on <id>
/groups off <id>
```

### 🧵 Topics Support
```
/settopic
/groups topic <id> <topic_id>
/groups topics <id>
```

### 📤 Kirim Pesan
```
/send Pesan kamu di sini
/sendpreview <pesan>
```

---

## 📂 Struktur Project

```
projek_ubot/
├── bot.py
├── config.py
├── database.py
├── sender.py
├── handlers/
├── data/
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── requirements.txt
└── README.md
```

---

## 🔐 Tips Keamanan

- Jangan spam berlebihan  
- Gunakan delay aman  
- Jangan share file `.session`  
- Gunakan akun lama (bukan akun baru)  

---

## 👨‍💻 Contributors

| Developer | Role |
|------------|--------|
| @kii922 | Lead Developer |
| @devinai | AI Engineer |
| @chatgpt | Documentation & Development Assistant |


