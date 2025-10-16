# 🚀 Quick Start Guide - Version 2.1

**Transhades Telegram Transcription Bot - Get Started in 5 Minutes**

---

## 📦 Installation (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Edit `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
GROQ_API_KEY=your_groq_key
```

### Step 3: Start Bot
```bash
python -m app.main
```

**Expected output:**
```
✅ Database initialized
✅ Translation service initialized  
🚀 Bot started with optimizations enabled!
```

---

## 🎯 Basic Usage (4 Commands)

### 1️⃣ Upload & Transcribe
```
📎 Upload audio/video file → Bot transcribes automatically
```

### 2️⃣ View History
```
/history
```
Shows last 20 transcriptions with previews

### 3️⃣ Search Transcripts
```
/search meeting
/search presentation
```
Find keywords in all transcripts

### 4️⃣ Translate & Export
```
/translate en          # Translate to English
/export               # Download as TXT/MD/SRT/VTT
```

---

## 🌟 New Features (v2.1)

### 🌐 Multi-Language Translation
**20+ languages supported:**
- `/translate en` → English
- `/translate id` → Indonesian  
- `/translate es` → Spanish
- `/translate ja` → Japanese
- `/languages` → See all

### 📚 Search & History
**Never lose a transcript:**
- `/history` → View all transcriptions
- `/search keyword` → Find specific content
- `/stats` → Usage statistics

### 📥 Multiple Export Formats
**Download in any format:**
- 📄 **TXT** - Plain text with metadata
- 📝 **MD** - Markdown for docs
- 🎬 **SRT** - Video subtitles
- 📊 **VTT** - Web subtitles

### 💾 Persistent Storage
**SQLite database:**
- All transcripts saved automatically
- Fast search (1000+ records)
- Export history as JSON/CSV

---

## 💡 Quick Examples

### Example 1: Basic Transcription
```
1. Upload: audio_file.mp3
2. Wait: Bot processes automatically
3. Receive: Transcript + TXT + SRT files
```

### Example 2: Multi-Language Content
```
1. Upload: english_audio.mp3
2. Command: /translate id
3. Command: /translate es  
4. Result: 3 versions (EN, ID, ES)
```

### Example 3: Find Old Transcript
```
1. Command: /search "project meeting"
2. Result: All meetings listed
3. Command: /export
4. Download: As Markdown
```

---

## 📖 All Commands

### Basic
- `/start` - Welcome & info
- `/help` - Full guide
- `/status` - Bot status

### History & Search
- `/history` - Last 20 transcripts
- `/search <word>` - Find keyword
- `/stats` - Your statistics

### Translation
- `/translate <lang>` - Translate
- `/languages` - Show languages

### Export
- `/export` - Download files

---

## ⚡ Performance Features

✅ **Smart Cache** - Instant for duplicates  
✅ **Queue System** - 5 concurrent users  
✅ **Auto-Retry** - Fails? Retries 2x  
✅ **Compression** - Auto-optimize files  
✅ **Large Files** - Support up to 2GB  

---

## 🎓 Pro Tips

### Tip 1: Use Search Effectively
```
/search "important"     # Find all important items
/search meeting         # Find all meetings
```

### Tip 2: Multi-Language Workflow
```
1. Upload audio
2. /translate en (English version)
3. /translate id (Indonesian version)  
4. /export (download both)
```

### Tip 3: Video Subtitles
```
1. Upload video file
2. /export → Choose SRT
3. Add subtitles to video editor
```

### Tip 4: Regular Backup
```
/history → Export as JSON
Save file regularly for backup
```

---

## 🔧 Troubleshooting

### "No transcripts found"
**Solution:** Upload at least 1 audio file first

### "Translation not available"
**Solution:** Add GROQ_API_KEY to .env (or uses free LibreTranslate)

### "Database error"
**Solution:** Check `transcriptions.db` exists and is writable

### Bot not responding
**Solution:** Check `/status` for queue and API status

---

## 📞 Need Help?

**In-Bot Help:**
```
/help           # Comprehensive guide
/status         # System status
```

**Documentation:**
- `NEW_FEATURES.md` - Complete feature guide
- `COMMANDS_REFERENCE.md` - All commands
- `SETUP_NEW_FEATURES.md` - Setup details

**Logs:**
```bash
python -m app.main 2>&1 | tee bot.log
```

---

## 🎯 Common Workflows

### Workflow 1: Meeting Documentation
```
1. Record meeting → Upload to bot
2. Receive transcript automatically
3. /translate en (if needed)
4. /export → Markdown
5. Share with team
```

### Workflow 2: Video Subtitles
```
1. Upload video
2. /export → SRT format
3. Import to video editor
4. /translate id → Indonesian subtitles
5. Export again as SRT
```

### Workflow 3: Content Archive
```
1. Upload all audio files
2. /history (review all)
3. /search by topics
4. /stats (check usage)
5. Export as CSV for records
```

---

## ✅ Quick Checklist

### First Time Setup
- [ ] Install dependencies
- [ ] Configure .env file
- [ ] Start bot
- [ ] Test with 1 audio file
- [ ] Check database created

### Daily Usage
- [ ] Upload audio files
- [ ] Use /history regularly
- [ ] Search when needed
- [ ] Translate as required
- [ ] Export important files

### Weekly Maintenance
- [ ] Check /stats
- [ ] Backup database
- [ ] Review history
- [ ] Clean old files (optional)

---

## 🎉 You're Ready!

Bot is now ready to use with **all advanced features**:

✅ Multi-language translation (20+ languages)  
✅ Full-text search & history  
✅ Multiple export formats  
✅ Persistent database storage  
✅ Statistics & analytics  

**Start transcribing now!** 🎵✨

---

## 📊 Feature Matrix

| Feature | Status | Command |
|---------|--------|---------|
| Transcription | ✅ | Upload file |
| History | ✅ | `/history` |
| Search | ✅ | `/search` |
| Translation | ✅ | `/translate` |
| Export TXT | ✅ | `/export` |
| Export MD | ✅ | `/export` |
| Export SRT | ✅ | `/export` |
| Export VTT | ✅ | `/export` |
| Statistics | ✅ | `/stats` |
| Cache | ✅ | Automatic |
| Queue | ✅ | Automatic |

---

## 🚀 Next Steps

1. **Try basic transcription** - Upload 1 audio file
2. **Explore history** - Use `/history` and `/search`
3. **Test translation** - Try `/translate en`
4. **Export files** - Download in different formats
5. **Check stats** - View your usage with `/stats`

---

**Version:** 2.1.0  
**Last Updated:** January 2024  
**Documentation:** See `NEW_FEATURES.md` for details

*Happy Transcribing! 🎵✨*