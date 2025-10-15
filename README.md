# Transhades Telegram Transcription Bot

Bot Telegram ini mentranskripsi audio, voice note, dan video menggunakan layanan Groq Whisper atau Deepgram (pilih sesuai kebutuhan). Anda dapat mengirim langsung atau me-forward file ke bot dan menerima teks hasil transkripsi.

## Persiapan

1. Salin `.env.example` menjadi `.env` dan isi kredensial berikut:
   ```bash
   cp .env.example .env
   ```
   - `TELEGRAM_BOT_TOKEN`: token bot dari BotFather.
   - `TELEGRAM_API_ID` dan `TELEGRAM_API_HASH`: kredensial MTProto dari [my.telegram.org](https://my.telegram.org).
   - `TRANSCRIPTION_PROVIDER`: `groq` (default) atau `deepgram`.
   - `GROQ_API_KEY`: kunci Groq Whisper (wajib jika provider `groq`).
   - `DEEPGRAM_API_KEY`: kunci Deepgram (wajib jika provider `deepgram`).
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

- Token Groq/Deepgram dan Telegram diambil dari variabel lingkungan (`GROQ_API_KEY` atau `DEEPGRAM_API_KEY`, serta `TELEGRAM_BOT_TOKEN`).
- Bot akan mengunduh file media secara sementara ke direktori sistem dan memastikan pembersihan setelah selesai.
- Struktur modular berada di folder `app/` yang memisahkan konfigurasi, handler Telegram, dan integrasi Groq untuk memudahkan pemeliharaan.
- Bot akan otomatis mengirim hasil sebagai pesan (maks 4000 karakter) serta lampiran `transcript.txt` dan, bila tersedia, `transcript.srt` tanpa timestamp tambahan di teks utama.
- Berkat integrasi Telethon (MTProto), bot dapat mengunduh file hingga 2GB. Jika ukuran melebihi 2GB, Anda perlu mengompresi atau memotong file secara manual sebelum mengirim ulang.
- Bot akan mengonversi media berukuran ≥15MB ke format mp3 menggunakan `ffmpeg` secara otomatis setelah unduhan selesai. Pastikan `ffmpeg` tersedia di lingkungan server.
- Bot berbasis Aiogram 3 dan Telethon sehingga seluruh alur bersifat asinkron serta efisien untuk unduhan buffer-stream besar.
- Untuk media ≥50MB, terminal akan menampilkan progress bar unduhan lengkap dengan logging Rich agar status proses mudah dipantau.
- Salinan media yang diunduh akan disimpan di `~/Downloads/transhades/` sehingga Anda dapat melakukan konversi atau kompresi lanjutan secara manual.
