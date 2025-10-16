# 🚀 Setup Guide - New Features

Panduan lengkap untuk setup dan konfigurasi fitur-fitur baru bot.

## 📋 Prerequisites

- Python 3.9+
- Existing bot installation (lihat `README.md` untuk basic setup)
- API keys (Groq/Together AI untuk translation - optional)

---

## 🔧 Installation

### 1. Update Dependencies

Install library baru yang dibutuhkan:

```bash
pip install -r requirements.txt
```

Library baru yang ditambahkan:
- `httpx==0.27.0` - Untuk async HTTP requests (translation service)

### 2. Verify Installation

Check semua import berjalan dengan baik:

```bash
python -c "from app.services import TranscriptionDatabase, TranslationService, ExportService; print('✅ All imports OK')"
```

---

## ⚙️ Configuration

### Environment Variables (Optional)

Tidak ada environment variable baru yang **wajib**. Fitur history & export akan langsung berfungsi.

Untuk fitur translation (optional), tambahkan ke `.env`:

```bash
# Translation Settings (Optional)
# Bot akan fallback ke LibreTranslate jika tidak ada API key

# Groq API (Recommended - Fastest)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Together AI (Alternative)
TOGETHER_API_KEY=your_together_api_key_here

# LibreTranslate (Free fallback - no key needed for public instance)
LIBRETRANSLATE_URL=https://libretranslate.com
LIBRETRANSLATE_API_KEY=  # Optional, untuk self-hosted instance
```

### Database Configuration

Database akan otomatis dibuat saat bot pertama kali dijalankan.

**Default location:** `transcriptions.db` (di root directory)

**Custom location** (optional):
```python
# Di main.py, line ~108
transcription_db = TranscriptionDatabase(db_path="custom/path/transcriptions.db")
```

---

## 🎯 Quick Start

### 1. Start the Bot

```bash
python -m app.main
```

Anda akan melihat log:
```
INFO     Transcription database initialized
INFO     Translation service initialized
INFO     🚀 Bot started with optimizations enabled!
```

### 2. Test Basic Features

Di Telegram:

1. **Upload audio file** → Bot akan transcribe dan simpan ke database
2. **Check history:** `/history` → Lihat transcript yang baru disimpan
3. **Test search:** `/search <keyword>` → Cari kata dalam transcript
4. **View stats:** `/stats` → Lihat statistik penggunaan
5. **Test export:** `/export` → Download transcript dalam berbagai format

### 3. Test Translation (if configured)

```
/translate en
/translate id
/languages
```

Jika tidak ada API key:
- Bot akan menampilkan error message yang informatif
- Translation feature tidak akan tersedia, tapi fitur lain tetap jalan

---

## 📁 File Structure

Fitur baru menambahkan files berikut:

```
botelgramTranscribe/
├── app/
│   ├── services/
│   │   ├── database.py          # ✨ NEW - SQLite database service
│   │   ├── translation.py       # ✨ NEW - Multi-language translation
│   │   └── export.py            # ✨ NEW - Export to TXT/MD/SRT/VTT
│   └── handlers/
│       └── history.py           # ✨ NEW - History, search, translate commands
├── transcriptions.db            # ✨ AUTO-CREATED - SQLite database
├── NEW_FEATURES.md              # Documentation
└── SETUP_NEW_FEATURES.md        # This file
```

---

## 🧪 Testing

### Test Database

```python
from app.services import TranscriptionDatabase, TranscriptionRecord

db = TranscriptionDatabase("test.db")

# Add test record
record = TranscriptionRecord(
    user_id=123456,
    chat_id=123456,
    file_id="test_file_123",
    file_name="test.mp3",
    file_size=1024000,
    transcript="This is a test transcript",
    provider="groq"
)
db.add_transcription(record)

# Get history
history = db.get_history(123456, limit=10)
print(f"✅ Found {len(history)} records")

# Search
results = db.search_transcripts(123456, "test")
print(f"✅ Found {len(results)} search results")
```

### Test Translation

```python
import asyncio
from app.services import TranslationService

async def test_translation():
    service = TranslationService(
        groq_api_key="your_key_here"
    )
    
    result = await service.translate(
        text="Hello, how are you?",
        target_language="id"
    )
    
    print(f"✅ Translated: {result.text}")
    print(f"   Provider: {result.provider}")

asyncio.run(test_translation())
```

### Test Export

```python
from app.services import ExportService

transcript = "This is a test transcript with some content."
metadata = {
    "file_name": "test.mp3",
    "duration": 120.5,
    "detected_language": "en",
    "provider": "groq"
}

# Test TXT export
txt = ExportService.to_txt(transcript, metadata)
print(f"✅ TXT export: {len(txt)} chars")

# Test Markdown export
md = ExportService.to_markdown(transcript, metadata)
print(f"✅ Markdown export: {len(md)} chars")

# Test SRT export
srt = ExportService.to_srt(transcript, duration=120.5)
print(f"✅ SRT export: {len(srt)} chars")
```

---

## 🔍 Verification Checklist

### Database Features ✅

- [ ] Database file created (`transcriptions.db`)
- [ ] Can add transcription records
- [ ] `/history` command works
- [ ] `/search` command works
- [ ] `/stats` command shows statistics
- [ ] History export (JSON/CSV) works

### Translation Features ✅

- [ ] Translation service initialized
- [ ] `/languages` shows supported languages
- [ ] `/translate <lang>` works (if API key configured)
- [ ] Translations saved to database
- [ ] Can export translated text

### Export Features ✅

- [ ] `/export` command works
- [ ] TXT export generates correctly
- [ ] Markdown export has proper formatting
- [ ] SRT export has timings
- [ ] VTT export works
- [ ] Files downloadable via Telegram

---

## 🐛 Troubleshooting

### Database Issues

**Error: "Database locked"**
```bash
# Solution: Close all connections to database
rm transcriptions.db
# Restart bot - database will be recreated
```

**Error: "Table already exists"**
```bash
# Solution: Database schema mismatch
# Backup old database, then:
mv transcriptions.db transcriptions_backup.db
# Restart bot
```

### Translation Issues

**Error: "Translation service not available"**
```bash
# Check if API keys are set:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GROQ_API_KEY:', bool(os.getenv('GROQ_API_KEY')))"
```

**LibreTranslate fallback not working**
```bash
# Test LibreTranslate connection:
curl https://libretranslate.com/translate -d "q=hello&source=en&target=es"
```

### Export Issues

**Error: "Export failed"**
- Check database connection
- Verify record ID exists
- Check file write permissions

**SRT timing issues**
- Duration metadata might be missing
- Bot will estimate timings automatically

---

## 📊 Database Management

### Backup Database

```bash
# Simple backup
cp transcriptions.db transcriptions_backup_$(date +%Y%m%d).db

# Or use SQLite dump
sqlite3 transcriptions.db .dump > backup.sql
```

### Restore Database

```bash
# From backup file
cp transcriptions_backup_20240115.db transcriptions.db

# From SQL dump
sqlite3 transcriptions.db < backup.sql
```

### Database Maintenance

```python
from app.services import TranscriptionDatabase

db = TranscriptionDatabase()

# Clean old records (older than 30 days)
deleted = db.cleanup_old_records(days=30)
print(f"Deleted {deleted} old records")
```

### View Database Content

```bash
# Using SQLite CLI
sqlite3 transcriptions.db

# View tables
.tables

# View transcriptions
SELECT id, user_id, file_name, detected_language, timestamp 
FROM transcriptions 
ORDER BY timestamp DESC 
LIMIT 10;

# View statistics
SELECT provider, COUNT(*) as count 
FROM transcriptions 
GROUP BY provider;
```

---

## 🔐 Security Notes

### Database Security

- Database file (`transcriptions.db`) contains user data
- **Tidak** share database file publicly
- Add to `.gitignore`:
  ```
  transcriptions.db
  transcriptions_*.db
  *.db-journal
  ```

### API Keys

- **Jangan** commit API keys ke Git
- Use `.env` file (already in `.gitignore`)
- Rotate keys secara berkala

---

## 📈 Performance Tuning

### Database Optimization

```python
# Increase cache size for better performance
import sqlite3
conn = sqlite3.connect('transcriptions.db')
conn.execute('PRAGMA cache_size = 10000')
conn.execute('PRAGMA temp_store = MEMORY')
```

### Translation Performance

- Groq: Fastest (recommended)
- Together AI: Good balance
- LibreTranslate: Slower but free

### Export Performance

- Large transcripts (>100KB) might take a few seconds
- Bot sends files asynchronously
- No impact on other users

---

## 🎓 Advanced Usage

### Custom Database Path

```python
# main.py
transcription_db = TranscriptionDatabase(
    db_path="/path/to/custom/transcriptions.db"
)
```

### Custom Translation Provider

```python
# main.py
translation_service = TranslationService(
    groq_api_key=settings.groq_api_key,
    together_api_key=settings.together_api_key,
    libretranslate_url="https://your-instance.com",
    libretranslate_api_key="your-key"
)
```

### Programmatic Export

```python
from app.services import ExportService

# Export with table of contents
md = ExportService.to_markdown(
    transcript=your_transcript,
    metadata=your_metadata,
    include_toc=True  # Adds table of contents
)

# Custom SRT timing
srt = ExportService.to_srt(
    transcript=your_transcript,
    duration=300.5,
    words_per_segment=15  # Adjust subtitle density
)
```

---

## 📞 Support & Help

### Log Files

Check logs untuk debugging:
```bash
# Bot logs (console output)
python -m app.main 2>&1 | tee bot.log

# SQLite errors
tail -f bot.log | grep -i "database\|sqlite"

# Translation errors
tail -f bot.log | grep -i "translation"
```

### Common Log Messages

✅ **Success:**
```
INFO     Transcription database initialized
INFO     Translation service initialized
INFO     💾 Saved transcription to database (ID: 123)
INFO     💾 Cached transcript for hash abc123
```

⚠️ **Warnings:**
```
WARNING  Failed to check cache by file_id
WARNING  Translation failed: <error>
```

❌ **Errors:**
```
ERROR    Failed to save to database: <error>
ERROR    Export failed: <error>
```

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Database backup strategy in place
- [ ] `.env` file configured with all keys
- [ ] Database path is writable
- [ ] Sufficient disk space (estimate 1MB per 100 transcripts)
- [ ] Translation API keys valid and have quota
- [ ] Bot has been tested with all commands
- [ ] Error handling tested
- [ ] Logs monitored

---

## 🎉 You're All Set!

Bot sekarang memiliki fitur-fitur berikut:

✅ **History Management** - Track semua transkripsi
✅ **Full-Text Search** - Cari dalam transcript dengan cepat
✅ **Multi-Language Translation** - 20+ bahasa didukung
✅ **Multiple Export Formats** - TXT, MD, SRT, VTT
✅ **SQLite Database** - Persistent storage
✅ **Statistics** - Usage analytics per user

### Next Steps

1. Test semua fitur dengan real data
2. Monitor database growth
3. Setup regular backups
4. Share dengan users!

---

**Need Help?**
- Check `NEW_FEATURES.md` untuk detailed documentation
- Review `README.md` untuk basic bot setup
- Check GitHub issues untuk known problems

---

*Happy Transcribing with New Features! 🎵✨*