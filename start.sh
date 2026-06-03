#!/bin/bash
# ============================================
# Projek Userbot — Start Script
# ============================================
# Script ini membantu setup & jalankan bot

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Telegram Promo Bot ===${NC}\n"

# Cek apakah .env sudah ada
if [ ! -f .env ]; then
    echo -e "${YELLOW}File .env belum ada. Membuat dari template...${NC}"
    cp .env.example .env
    echo ""
    echo -e "${RED}PENTING: Edit file .env dan isi API_ID & API_HASH!${NC}"
    echo "1. Buka https://my.telegram.org"
    echo "2. Login → API development tools → Buat aplikasi"
    echo "3. Catat API_ID dan API_HASH"
    echo ""
    echo "Edit .env dengan perintah:"
    echo -e "  ${GREEN}nano .env${NC}"
    echo ""
    echo "Setelah edit .env, jalankan script ini lagi."
    exit 1
fi

# Buat folder data jika belum ada
mkdir -p data

# Cek mode (docker atau lokal)
if [ "$1" = "docker" ]; then
    echo -e "${GREEN}Mode: Docker${NC}\n"

    # Cek Docker terinstall
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker belum terinstall!${NC}"
        echo "Install Docker di Linux Mint:"
        echo "  sudo apt update"
        echo "  sudo apt install docker.io docker-compose-v2"
        echo "  sudo usermod -aG docker \$USER"
        echo "  (logout & login kembali)"
        exit 1
    fi

    if [ "$2" = "login" ]; then
        # Login pertama kali (interactive mode)
        echo -e "${YELLOW}Login mode — masukkan nomor telepon & OTP saat diminta${NC}\n"
        docker compose run --rm promo-bot
    elif [ "$2" = "stop" ]; then
        echo "Menghentikan bot..."
        docker compose down
        echo -e "${GREEN}Bot dihentikan.${NC}"
    elif [ "$2" = "logs" ]; then
        docker compose logs -f promo-bot
    else
        # Jalankan di background
        echo "Menjalankan bot di background..."
        docker compose up -d --build
        echo -e "${GREEN}Bot berjalan!${NC}"
        echo "Lihat log: ./start.sh docker logs"
        echo "Stop: ./start.sh docker stop"
    fi

elif [ "$1" = "local" ] || [ -z "$1" ]; then
    echo -e "${GREEN}Mode: Lokal${NC}\n"

    # Cek Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 belum terinstall!${NC}"
        echo "Install: sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi

    # Buat virtual environment jika belum ada
    if [ ! -d "venv" ]; then
        echo "Membuat virtual environment..."
        python3 -m venv venv
    fi

    # Aktifkan venv
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt -q

    # Jalankan bot
    echo -e "\n${GREEN}Menjalankan bot...${NC}"
    echo "Tekan Ctrl+C untuk berhenti."
    echo ""
    python bot.py

else
    echo "Penggunaan:"
    echo "  ./start.sh              — Jalankan lokal (tanpa Docker)"
    echo "  ./start.sh local        — Jalankan lokal (tanpa Docker)"
    echo "  ./start.sh docker login — Login pertama kali (Docker)"
    echo "  ./start.sh docker       — Jalankan dengan Docker (background)"
    echo "  ./start.sh docker logs  — Lihat log Docker"
    echo "  ./start.sh docker stop  — Hentikan Docker"
fi
