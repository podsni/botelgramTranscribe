# 🧪 Testing Guide - New Features

Panduan lengkap untuk testing dan verifikasi semua fitur baru bot.

---

## 📋 Table of Contents

- [Pre-Testing Setup](#pre-testing-setup)
- [Database Testing](#database-testing)
- [Translation Testing](#translation-testing)
- [Export Testing](#export-testing)
- [Command Testing](#command-testing)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [Error Handling Testing](#error-handling-testing)

---

## 🔧 Pre-Testing Setup

### 1. Environment Setup

```bash
# Clone/update repository
git pull origin main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create or update `.env` file:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Transcription (at least one required)
GROQ_API_KEY=your_groq_key
# or DEEPGRAM_API_KEY=your_deepgram_key
# or TOGETHER_API_KEY=your_together_key

# Translation (optional - for full testing)
GROQ_API_KEY=your_groq_key  # Recommended for translation
```

### 3. Start Bot

```bash
python -m app.main
```

**Expected output:**
```
INFO     Database initialized at transcriptions.db
INFO     Transcription database initialized
INFO     Translation service initialized
INFO     🚀 Bot started with optimizations enabled!
INFO     📊 Features: Caching=True, Queue=5 workers, Streaming=True
```

---

## 💾 Database Testing

### Test 1: Database Creation

**Objective:** Verify database is created automatically

**Steps:**
1. Delete `transcriptions.db` if exists
2. Start bot
3. Check if `transcriptions.db` file is created

**Expected Result:**
```bash
ls -lh transcriptions.db
# Should show file with size ~20KB (empty database with schema)
```

**Verification:**
```bash
sqlite3 transcriptions.db ".tables"
# Expected output: transcriptions  translations
```

### Test 2: Save Transcription

**Objective:** Verify transcriptions are saved to database

**Steps:**
1. Upload a test audio file to bot
2. Wait for transcription to complete
3. Check database

**Verification:**
```bash
sqlite3 transcriptions.db "SELECT COUNT(*) FROM transcriptions;"
# Should return: 1
```

**Or using Python:**
```python
from app.services import TranscriptionDatabase

db = TranscriptionDatabase()
history = db.get_history(your_user_id, limit=10)
print(f"Records found: {len(history)}")
# Should print: Records found: 1
```

### Test 3: Search Functionality

**Objective:** Verify search works correctly

**Steps:**
1. Upload 2-3 audio files with different content
2. Use `/search` command with keyword from one file
3. Verify only relevant results are returned

**Command:**
```
/search [keyword from file 1]
```

**Expected Result:**
- Shows only file 1 in results
- Context snippet contains the keyword
- File name and timestamp displayed

### Test 4: Database Indexes

**Objective:** Verify indexes are created for performance

**Verification:**
```bash
sqlite3 transcriptions.db ".indexes"
```

**Expected Output:**
```
idx_chat_id
idx_file_id
idx_timestamp
idx_transcript_fts
idx_user_id
```

---

## 🌐 Translation Testing

### Test 1: Language List

**Objective:** Verify language list command

**Steps:**
1. Send `/languages` to bot

**Expected Result:**
- List of 20+ languages with codes
- Grouped by region (European, Asian)
- Usage example shown

### Test 2: Basic Translation

**Objective:** Verify translation works

**Prerequisites:**
- At least one API key configured (Groq/Together)
- At least one transcript in database

**Steps:**
1. Upload English audio file
2. Wait for transcription
3. Send `/translate id` (Indonesian)
4. Verify translation received

**Expected Result:**
```
✅ Translation Complete

📄 File: test_audio.mp3
🌐 English → Indonesian
🔧 Provider: groq

Translated Text:
[Indonesian translation here]

[📥 Download TXT] [📥 Download MD]
```

### Test 3: Multiple Translations

**Objective:** Verify multiple translations for same transcript

**Steps:**
1. After transcription, translate to English: `/translate en`
2. Then translate to Spanish: `/translate es`
3. Then translate to Japanese: `/translate ja`

**Expected Result:**
- All translations succeed
- Different languages shown correctly
- All saved to database

**Verification:**
```python
from app.services import TranscriptionDatabase

db = TranscriptionDatabase()
record = db.get_last_transcription(your_user_id)
translations = db.get_translations(record.id)
print(f"Translations: {len(translations)}")
# Should print: Translations: 3
```

### Test 4: Translation Without API Key

**Objective:** Verify fallback to LibreTranslate

**Steps:**
1. Remove all API keys from `.env` (or comment out)
2. Restart bot
3. Try `/translate en`

**Expected Result:**
- Should fallback to LibreTranslate automatically
- Translation still works (might be slower)
- Provider shown as "libretranslate"

### Test 5: Unsupported Language

**Objective:** Verify error handling for invalid language

**Steps:**
1. Send `/translate xyz` (invalid code)

**Expected Result:**
```
❌ Unsupported language code: xyz

Use /languages to see all supported languages.
```

---

## 📥 Export Testing

### Test 1: Export Menu

**Objective:** Verify export command shows format options

**Steps:**
1. Upload and transcribe a file
2. Send `/export`

**Expected Result:**
- Inline keyboard with 4 buttons:
  - 📄 Plain Text (.txt)
  - 📝 Markdown (.md)
  - 🎬 Subtitles (.srt)
  - 📊 WebVTT (.vtt)
- File info displayed

### Test 2: TXT Export

**Objective:** Verify plain text export

**Steps:**
1. Send `/export`
2. Click "Plain Text (.txt)"

**Expected Result:**
- File downloaded successfully
- File name: `[original_name].txt`
- Contains metadata header
- Contains full transcript

**Verification:**
```
Content should look like:
============================================================
TRANSCRIPT METADATA
============================================================
File: test_audio.mp3
Duration: 2m 30s
Language: en
Provider: groq
...
============================================================

[Transcript content here]
```

### Test 3: Markdown Export

**Objective:** Verify Markdown export

**Steps:**
1. Send `/export`
2. Click "Markdown (.md)"

**Expected Result:**
- File downloaded as `.md`
- Proper Markdown formatting
- Headers with emoji (# Title, ## Information, ## Transcript)
- Metadata in bullet list
- Footer with bot attribution

### Test 4: SRT Export

**Objective:** Verify subtitle export

**Steps:**
1. Send `/export`
2. Click "Subtitles (.srt)"

**Expected Result:**
- File downloaded as `.srt`
- Standard SRT format
- Numbered segments
- Timings in format: `HH:MM:SS,mmm --> HH:MM:SS,mmm`
- Text split into ~10 word segments

**Verification:**
```
Content should look like:
1
00:00:00,000 --> 00:00:02,000
This is the first segment of

2
00:00:02,000 --> 00:00:04,000
the transcribed text with proper timing
```

### Test 5: VTT Export

**Objective:** Verify WebVTT export

**Steps:**
1. Send `/export`
2. Click "WebVTT (.vtt)"

**Expected Result:**
- File downloaded as `.vtt`
- Starts with "WEBVTT" header
- Timings in format: `HH:MM:SS.mmm --> HH:MM:SS.mmm` (note: dot instead of comma)

### Test 6: History Export (JSON)

**Objective:** Verify history export as JSON

**Steps:**
1. Upload multiple files (3-5)
2. Send `/history`
3. Click "Export as JSON"

**Expected Result:**
- JSON file downloaded
- Valid JSON format
- Array of transcript objects
- Each object has all metadata fields

**Verification:**
```bash
cat transcription_history_*.json | jq length
# Should show number of transcripts
```

### Test 7: History Export (CSV)

**Objective:** Verify history export as CSV

**Steps:**
1. Send `/history`
2. Click "Export as CSV"

**Expected Result:**
- CSV file downloaded
- Header row with column names
- Data rows for each transcript
- Commas properly escaped in transcript text

**Verification:**
```bash
# Should be readable in Excel/Google Sheets
head transcription_history_*.csv
```

---

## 📖 Command Testing

### Test 1: /start Command

**Steps:**
1. Send `/start`

**Expected Result:**
- Welcome message
- Basic usage instructions
- Mentions all major features (transcription, translation, history)

### Test 2: /help Command

**Steps:**
1. Send `/help`

**Expected Result:**
- Comprehensive help message
- Sections for:
  - Basic Commands
  - History & Search
  - Translation
  - Export
- Feature list with emoji

### Test 3: /history Command

**Steps:**
1. Upload 2-3 files
2. Send `/history`

**Expected Result:**
- List of transcriptions (max 10 shown)
- Each entry shows:
  - Number (1, 2, 3...)
  - File name
  - Duration, language, provider
  - Preview text (80 chars)
  - Timestamp
- Buttons for export and statistics

### Test 4: /search Command

**Test 4.1: Without Parameter**

**Steps:**
1. Send `/search` (no keyword)

**Expected Result:**
- Usage instructions
- Examples shown

**Test 4.2: With Keyword**

**Steps:**
1. Send `/search meeting`

**Expected Result:**
- Search results with keyword highlighted in context
- File name and timestamp for each result
- Max 10 results shown

**Test 4.3: No Results**

**Steps:**
1. Send `/search xyzabc123` (nonsense keyword)

**Expected Result:**
```
🔍 Search Results

No transcripts found containing "xyzabc123"

Try a different keyword or check your history with /history
```

### Test 5: /stats Command

**Steps:**
1. Upload files with different providers/languages
2. Send `/stats`

**Expected Result:**
- Total transcription count
- Total duration processed
- Provider breakdown (Groq: X, Deepgram: Y)
- Language breakdown (English: X, Indonesian: Y)

### Test 6: /translate Command

**Test 6.1: Without Parameter**

**Steps:**
1. Send `/translate` (no language code)

**Expected Result:**
- Usage instructions
- Examples (en, id, es)
- Link to `/languages` command

**Test 6.2: With Language Code**

**Steps:**
1. Send `/translate en`

**Expected Result:**
- Processing message
- Translation result
- Download buttons (TXT, MD)

**Test 6.3: No Transcript Yet**

**Steps:**
1. Fresh user with no transcripts
2. Send `/translate en`

**Expected Result:**
```
📭 No Transcripts Found

You need to transcribe a file first before translating.
Send an audio or video file to start!
```

### Test 7: /status Command

**Steps:**
1. Send `/status`

**Expected Result:**
- API rotation stats
- Queue statistics
- Cache statistics
- Bot status (online & ready)

---

## 🔄 Integration Testing

### End-to-End Test 1: Complete Workflow

**Scenario:** User uploads file, translates, and exports

**Steps:**
1. Upload test audio file (English)
2. Wait for transcription
3. Verify transcript received
4. Send `/translate id`
5. Verify Indonesian translation received
6. Click "Download TXT" button
7. Verify TXT file downloaded
8. Send `/export`
9. Click "Markdown (.md)"
10. Verify MD file downloaded

**Expected Result:**
- All steps complete without errors
- Files downloaded successfully
- Data saved to database

**Verification:**
```python
from app.services import TranscriptionDatabase

db = TranscriptionDatabase()
record = db.get_last_transcription(your_user_id)
assert record is not None
assert record.transcript != ""

translations = db.get_translations(record.id)
assert len(translations) >= 1
```

### End-to-End Test 2: Search and Re-export

**Scenario:** User searches old transcript and exports it

**Steps:**
1. Upload 3 files with different content
2. Wait 1-2 minutes
3. Send `/search [keyword from file 2]`
4. Verify file 2 found
5. Send `/history`
6. Verify all 3 files in history
7. Send `/export`
8. Export file 2 as SRT

**Expected Result:**
- Search finds correct file
- History shows all files
- Export works for most recent file

### End-to-End Test 3: Multi-language Content

**Scenario:** Create multi-language versions

**Steps:**
1. Upload English audio
2. Get transcription
3. `/translate id` → Indonesian
4. `/translate es` → Spanish
5. `/translate ja` → Japanese
6. `/history`
7. Verify transcript shown with all translations

**Expected Result:**
- All 3 translations complete
- Database has 1 transcript + 3 translations
- Can export each version

---

## ⚡ Performance Testing

### Test 1: Large File Handling

**Steps:**
1. Upload file >100MB
2. Monitor processing time
3. Check database write speed

**Expected Result:**
- File processes successfully
- Streaming optimization active (check logs)
- Database save completes quickly (<1s)

### Test 2: Concurrent Requests

**Steps:**
1. Open bot in 3 different accounts
2. Upload files simultaneously
3. Monitor queue stats with `/status`

**Expected Result:**
- Queue shows active workers (1-5)
- All files process eventually
- No crashes or errors

### Test 3: Database Query Speed

**Verification:**
```python
import time
from app.services import TranscriptionDatabase

db = TranscriptionDatabase()

# Insert 100 test records
for i in range(100):
    record = TranscriptionRecord(
        user_id=12345,
        chat_id=12345,
        file_id=f"test_{i}",
        file_name=f"test_{i}.mp3",
        transcript=f"Test transcript {i} " * 50,
        provider="groq"
    )
    db.add_transcription(record)

# Test search speed
start = time.time()
results = db.search_transcripts(12345, "transcript", limit=20)
duration = time.time() - start

print(f"Search took {duration:.3f}s")
# Should be < 0.1s even with 100 records
```

### Test 4: Export Speed

**Steps:**
1. Create transcript with 10,000 words
2. Export as TXT, MD, SRT, VTT
3. Measure time for each

**Expected Result:**
- TXT: <1s
- MD: <2s
- SRT: <3s (timing calculation)
- VTT: <3s

---

## 🐛 Error Handling Testing

### Test 1: Database Unavailable

**Steps:**
1. Start bot
2. Delete `transcriptions.db` while bot running
3. Try `/history`

**Expected Result:**
- Graceful error message
- Bot doesn't crash
- Database recreated on next save

### Test 2: Translation API Failure

**Steps:**
1. Set invalid API key in `.env`
2. Restart bot
3. Try `/translate en`

**Expected Result:**
- Error message shown
- Suggests checking configuration
- Bot still functional for other commands

### Test 3: Empty Transcript

**Steps:**
1. Upload silent audio file
2. Wait for processing

**Expected Result:**
- Either: "Transkrip kosong" message
- Or: Minimal transcript returned
- No crash

### Test 4: Invalid File Format

**Steps:**
1. Upload text file (.txt)
2. Wait for bot response

**Expected Result:**
- Bot ignores non-media files
- No error message (silent ignore)
- No processing attempted

### Test 5: Network Interruption

**Steps:**
1. Start large file upload
2. Disconnect internet briefly
3. Reconnect

**Expected Result:**
- Telethon handles reconnection
- Download resumes or retries
- User notified if fails after retries

### Test 6: Database Lock

**Steps:**
1. Open database in SQLite CLI
2. Start long-running query
3. Try `/history` in bot

**Expected Result:**
- Bot waits or retries
- Eventually times out with error
- User-friendly message shown

---

## ✅ Testing Checklist

### Database Tests
- [ ] Database file created automatically
- [ ] Transcriptions saved correctly
- [ ] Search returns accurate results
- [ ] History pagination works
- [ ] Statistics calculated correctly
- [ ] Indexes improve query speed
- [ ] Translations linked to transcriptions

### Translation Tests
- [ ] `/languages` shows all languages
- [ ] Translation works with Groq
- [ ] Translation works with Together
- [ ] Fallback to LibreTranslate works
- [ ] Invalid language codes handled
- [ ] Multiple translations per transcript
- [ ] Translation saved to database

### Export Tests
- [ ] TXT export has proper formatting
- [ ] Markdown export renders correctly
- [ ] SRT has valid timings
- [ ] VTT format correct
- [ ] JSON export valid
- [ ] CSV export readable in Excel
- [ ] File names appropriate

### Command Tests
- [ ] `/start` shows welcome
- [ ] `/help` comprehensive
- [ ] `/history` lists transcripts
- [ ] `/search` finds keywords
- [ ] `/stats` shows analytics
- [ ] `/translate` works
- [ ] `/export` generates files
- [ ] `/languages` lists all
- [ ] `/status` shows system info

### Integration Tests
- [ ] Full workflow works end-to-end
- [ ] Multiple users don't interfere
- [ ] Data persists across restarts
- [ ] Cache + database work together
- [ ] Queue + database work together

### Performance Tests
- [ ] Large files process efficiently
- [ ] Concurrent users handled
- [ ] Database queries fast (<0.1s)
- [ ] Export generation fast (<3s)
- [ ] No memory leaks in long sessions

### Error Handling Tests
- [ ] Database errors handled gracefully
- [ ] API failures don't crash bot
- [ ] Invalid input handled
- [ ] Network issues recovered
- [ ] User-friendly error messages

---

## 📊 Test Results Template

Use this template to document test results:

```markdown
## Test Run: [Date]

**Tester:** [Name]
**Environment:** [Production/Staging/Local]
**Bot Version:** 2.1.0

### Summary
- Total Tests: [X]
- Passed: [Y]
- Failed: [Z]
- Skipped: [W]

### Failed Tests
1. **Test Name:** [Test that failed]
   - **Issue:** [Description]
   - **Expected:** [Expected result]
   - **Actual:** [Actual result]
   - **Logs:** [Relevant log excerpt]

### Notes
[Any additional observations]

### Recommendation
[ ] Ready for production
[ ] Needs fixes before deployment
[ ] Requires further testing
```

---

## 🔍 Debugging Tips

### Enable Debug Logging

```python
# In main.py, change logging level:
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

### Check Database Content

```bash
# View recent transcriptions
sqlite3 transcriptions.db "
SELECT id, user_id, file_name, 
       substr(transcript, 1, 50) as preview,
       timestamp 
FROM transcriptions 
ORDER BY timestamp DESC 
LIMIT 5;
"
```

### Monitor Bot Logs

```bash
# Real-time log monitoring
tail -f bot.log | grep -i "error\|warning\|database\|translation"
```

### Test in Isolation

```python
# Test single component
from app.services import TranslationService

async def test():
    service = TranslationService(groq_api_key="your_key")
    result = await service.translate("Hello", "id")
    print(result.text)

import asyncio
asyncio.run(test())
```

---

## 📞 Reporting Issues

If you find bugs during testing:

1. **Document the issue:**
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs
   - Environment details

2. **Check existing issues:**
   - Review `CHANGELOG.md` for known issues
   - Search GitHub issues

3. **Create detailed bug report:**
   - Use template above
   - Include all relevant information
   - Tag with severity (critical/high/medium/low)

---

**Happy Testing! 🧪✨**

*Last Updated: January 2024*