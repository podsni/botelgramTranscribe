# 📖 Commands Reference - Quick Guide

Quick reference untuk semua commands bot dengan contoh penggunaan.

---

## 🎯 Basic Commands

### `/start`
**Deskripsi:** Info bot dan cara penggunaan dasar  
**Usage:** `/start`  
**Output:** Welcome message dengan fitur-fitur utama bot

### `/help`
**Deskripsi:** Panduan lengkap dengan semua fitur dan commands  
**Usage:** `/help`  
**Output:** Comprehensive help message dengan semua fitur

### `/provider`
**Deskripsi:** Pilih provider transkripsi (Groq/Deepgram/Together)  
**Usage:** `/provider`  
**Output:** Inline keyboard untuk memilih provider dan model

### `/status`
**Deskripsi:** Cek status bot, cache, queue, dan API rotation  
**Usage:** `/status`  
**Output:** 
- API rotation stats (available/FloodWait)
- Queue statistics (workers, tasks)
- Cache statistics (size, hits)
- Bot uptime info

---

## 📚 History & Search Commands

### `/history`
**Deskripsi:** Lihat riwayat transkripsi terakhir (20 file)  
**Usage:** `/history`  
**Output:**
- List 10 transkripsi terbaru
- File name, duration, bahasa, provider
- Preview transcript (80 karakter)
- Timestamp pemrosesan
- Buttons untuk export (JSON/CSV) dan statistics

**Example Output:**
```
📚 Your Transcription History

1. meeting_20240115.mp3
   ⏱️ 15m 30s | 🌐 en | 🔧 groq
   📝 This is the meeting transcript about project discussion...
   🕐 2024-01-15T10:30:00

2. interview_audio.wav
   ⏱️ 8m 45s | 🌐 id | 🔧 deepgram
   📝 Wawancara dengan narasumber tentang teknologi AI...
   🕐 2024-01-15T09:15:00
```

### `/search <keyword>`
**Deskripsi:** Cari dalam semua transcript yang pernah diproses  
**Usage:** `/search <keyword>`  
**Parameters:**
- `<keyword>` - Kata kunci untuk dicari (case-insensitive)

**Examples:**
```
/search meeting
/search presentation
/search "project timeline"
/search AI
```

**Output:**
- Jumlah hasil ditemukan
- Context snippet dengan keyword
- File name dan timestamp
- Maksimal 10 hasil pertama

**Example Output:**
```
🔍 Search Results for "meeting"

Found 3 result(s):

1. meeting_20240115.mp3
   📝 ...important discussion in the meeting about the new project...
   🕐 2024-01-15T10:30:00

2. team_call_recording.mp3
   📝 ...schedule the next team meeting for next Monday...
   🕐 2024-01-14T14:20:00
```

### `/stats`
**Deskripsi:** Lihat statistik penggunaan Anda  
**Usage:** `/stats`  
**Output:**
- Total transkripsi
- Total durasi audio diproses
- Breakdown by provider
- Breakdown by bahasa
- Personal usage insights

**Example Output:**
```
📊 Your Transcription Statistics

Overview:
• Total transcriptions: 45
• Total audio processed: 3h 25m 15s

Providers Used:
• Groq: 30
• Deepgram: 15

Languages Detected:
• English: 25
• Indonesian: 20
```

---

## 🌐 Translation Commands

### `/translate <lang_code>`
**Deskripsi:** Translate transcript terakhir ke bahasa lain  
**Usage:** `/translate <lang_code>`  
**Parameters:**
- `<lang_code>` - Kode bahasa target (2 huruf)

**Supported Languages:**
- `en` - English
- `id` - Indonesian
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- `ar` - Arabic
- `hi` - Hindi
- `th` - Thai
- `vi` - Vietnamese
- Dan 10+ bahasa lainnya (lihat `/languages`)

**Examples:**
```
/translate en       # Translate to English
/translate id       # Translate to Indonesian
/translate es       # Translate to Spanish
/translate ja       # Translate to Japanese
```

**Output:**
- File info (name, size)
- Source language → Target language
- Provider yang digunakan
- Translated text
- Buttons untuk download (TXT/MD)

**Example Output:**
```
✅ Translation Complete

📄 File: meeting_20240115.mp3
🌐 English → Indonesian
🔧 Provider: groq

Translated Text:
Ini adalah transkrip rapat tentang diskusi proyek...

[📥 Download TXT] [📥 Download MD]
```

### `/languages`
**Deskripsi:** Lihat semua bahasa yang didukung untuk translation  
**Usage:** `/languages`  
**Output:** List lengkap 20+ bahasa dengan kode dan nama

**Example Output:**
```
🌐 Supported Languages

European:
• en - English
• es - Spanish
• fr - French
• de - German
...

Asian:
• id - Indonesian
• ja - Japanese
• ko - Korean
• zh - Chinese
...

Usage:
/translate <code> - Translate last transcript
```

---

## 📥 Export Commands

### `/export`
**Deskripsi:** Export transcript terakhir dalam berbagai format  
**Usage:** `/export`  
**Output:** Inline keyboard dengan pilihan format:
- 📄 Plain Text (.txt)
- 📝 Markdown (.md)
- 🎬 Subtitles (.srt)
- 📊 WebVTT (.vtt)

**Export Formats:**

#### 1. Plain Text (.txt)
- Clean text tanpa timestamp
- Metadata header (file, duration, language)
- Perfect untuk dokumentasi

#### 2. Markdown (.md)
- Professional formatting
- Metadata section dengan emoji
- Section headers
- Perfect untuk GitHub/Notion

#### 3. Subtitles (.srt)
- Standard subtitle format
- Auto-generated timings
- Compatible dengan video editors
- Ready untuk YouTube/Vimeo

#### 4. WebVTT (.vtt)
- Modern web subtitle format
- HTML5 video compatible
- Better styling support

**After Selection:**
Bot akan generate dan kirim file sesuai format pilihan Anda.

---

## 🔄 Workflow Examples

### Workflow 1: Basic Transcription
```
1. Upload audio file → Bot transcribes automatically
2. Receive transcript in Telegram
3. Get TXT and SRT files
```

### Workflow 2: Transcribe + Translate
```
1. Upload audio file → Bot transcribes
2. /translate en → Get English translation
3. Download translated text (TXT/MD)
```

### Workflow 3: Find Old Transcript
```
1. /search "project meeting" → Find relevant transcripts
2. /history → View full list
3. /export → Download specific transcript
```

### Workflow 4: Multi-language Content
```
1. Upload Indonesian audio → Get ID transcript
2. /translate en → Get English version
3. /translate es → Get Spanish version
4. /export → Download all versions
```

### Workflow 5: Review & Analysis
```
1. /history → View recent transcriptions
2. /stats → Check usage statistics
3. /search "keyword" → Find specific topics
4. Export as CSV → Analyze in Excel
```

---

## 💡 Pro Tips

### Search Tips
- **Use specific keywords** untuk hasil lebih akurat
- **Search is case-insensitive** - "Meeting" = "meeting"
- **Context provided** - Lihat 40 karakter sebelum/sesudah keyword
- **Use quotes** untuk phrase search (jika applicable)

### Translation Tips
- **Best quality:** Groq (fastest & accurate)
- **For European languages:** LibreTranslate works well
- **Audio quality matters** - Better audio = better translation
- **Translate immediately** jika butuh multiple languages

### Export Tips
- **TXT format** - Best untuk reading & documentation
- **Markdown format** - Best untuk sharing (GitHub/Notion)
- **SRT format** - Best untuk video subtitles
- **VTT format** - Best untuk web players

### History Management
- **Use /search** sebelum /history untuk cari spesifik
- **Export to CSV** untuk backup atau analysis di Excel
- **Check /stats** untuk track usage patterns

---

## 🔧 Command Combinations

### Combination 1: Complete Documentation
```bash
1. Upload meeting.mp3
2. /export → Download as Markdown
3. /translate en → Get English version
4. /export → Download English MD
```

### Combination 2: Video Subtitles
```bash
1. Upload video.mp4 (audio extracted)
2. /export → Download SRT
3. /translate id → Get Indonesian transcript
4. /export → Download Indonesian SRT
```

### Combination 3: Research & Archive
```bash
1. /history → Export as JSON (backup)
2. /stats → Check statistics
3. /search "research" → Find relevant transcripts
4. /export → Download specific ones
```

---

## 🆘 Quick Help

**Can't find command?**
- Type `/help` untuk full guide
- Check documentation di `NEW_FEATURES.md`

**Command not working?**
- Check bot `/status` untuk availability
- Make sure you've transcribed at least 1 file
- Verify API keys for translation features

**Need specific format?**
- Use `/export` untuk multiple format options
- All formats include metadata

**Want to find old file?**
- Use `/search <keyword>` untuk cari spesifik
- Use `/history` untuk browse chronologically

---

## 📞 Support

Jika ada pertanyaan atau masalah:

1. Check `/help` command
2. Review `NEW_FEATURES.md` documentation
3. Check `SETUP_NEW_FEATURES.md` untuk setup guide
4. Contact bot owner untuk technical issues

---

**Last Updated:** January 2024  
**Bot Version:** 2.1.0

*Happy Transcribing! 🎵✨*