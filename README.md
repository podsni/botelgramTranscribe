# Transhades Telegram Transcription Bot

Bot Telegram ini mentranskripsi audio, voice note, dan video menggunakan Groq Whisper API. Anda dapat mengirim langsung atau me-forward file ke bot dan menerima teks hasil transkripsi.

## Persiapan

1. Salin `.env.example` menjadi `.env` dan sesuaikan nilai token bila diperlukan.
   ```bash
   cp .env.example .env
   ```
2. Install dependensi Python (gunakan Python 3.9+).
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Menjalankan Bot

Aktifkan virtual environment sebelum menjalankan aplikasi:

```bash
source .venv/bin/activate
```

Jalankan bot dengan module package Python:

```bash
python -m app.main
```

Bot akan mulai menggunakan long polling. Kirim atau forward file audio (mp3, m4a, ogg) atau video (mp4) ke bot Anda. Hasil transkripsi akan dikirim balik sebagai pesan teks.

## Catatan

- Token Groq dan Telegram diambil dari variabel lingkungan `GROQ_API_KEY` dan `TELEGRAM_BOT_TOKEN`.
- Bot akan mengunduh file media secara sementara ke direktori sistem dan memastikan pembersihan setelah selesai.
- Struktur modular berada di folder `app/` yang memisahkan konfigurasi, handler Telegram, dan integrasi Groq untuk memudahkan pemeliharaan.
- Bot akan otomatis mengirim hasil sebagai pesan (maks 4000 karakter) serta lampiran `transcript.txt` dan, bila tersedia, `transcript.srt` tanpa timestamp tambahan di teks utama.
- Telegram tidak mengizinkan bot mengunduh file lebih besar dari ~20MB; jika batas ini tercapai, Anda perlu mengompresi atau memotong file secara manual sebelum mengirim ulang.
- Bot akan mengonversi media berukuran ≥15MB ke format mp3 menggunakan `ffmpeg` secara otomatis setelah unduhan selesai. Pastikan `ffmpeg` tersedia di lingkungan server.
