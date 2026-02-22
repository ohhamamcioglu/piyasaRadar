#!/bin/bash
# PiyasaRadar - Günlük Tarama Script'i
# Her sabah 08:00'de çalıştırılır (BIST + ABD piyasaları kapalıyken)

cd /home/ohhamamcioglu/Desktop/bistTümBilanco

LOG_FILE="scan_log_$(date +%Y-%m-%d).txt"

echo "========================================" >> "$LOG_FILE"
echo "Tarama Başladı: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. BIST Taraması
echo "[1/3] BIST Taraması başlıyor..." >> "$LOG_FILE"
./venv/bin/python bist_scanner.py >> "$LOG_FILE" 2>&1
echo "BIST Taraması tamamlandı: $(date)" >> "$LOG_FILE"

# 2. ABD (Midas) Taraması
echo "[2/3] ABD Taraması başlıyor..." >> "$LOG_FILE"
./venv/bin/python us_scanner.py >> "$LOG_FILE" 2>&1
echo "ABD Taraması tamamlandı: $(date)" >> "$LOG_FILE"

# 3. Portföy Yönetimi ve Dengeleme Raporu
echo "[3/4] Portföy Raporları oluşturuluyor..." >> "$LOG_FILE"
./venv/bin/python portfolio_manager.py >> "$LOG_FILE" 2>&1

# 4. History Dosyalarını Güncelle (NaN temizliği dahil)
echo "[4/4] History güncelleniyor..." >> "$LOG_FILE"
./venv/bin/python force_update_history.py >> "$LOG_FILE" 2>&1

echo "========================================" >> "$LOG_FILE"
echo "Tüm taramalar tamamlandı: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
