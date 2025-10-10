## Quick Start Guide - Video Archive Tool

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.11+ already installed
- FFmpeg binaries (download separately)

### Setup (First Time)

1. **Virtual Environment** (Already Created ✓)
   ```bash
   # Already done - venv folder exists
   ```

2. **Dependencies** (Already Installed ✓)
   ```bash
   # Already installed via pip
   ```

3. **Get FFmpeg** (Required)
   - Download from: https://ffmpeg.org/download.html
   - Extract `ffmpeg.exe` and `ffprobe.exe`
   - Place in: `App/ffmpeg/` folder (create if needed)
   - Or add to system PATH

### Running the Application

**Option 1: Development Launcher (Easiest)**
```bash
run_dev.bat
```

**Option 2: Manual**
```bash
venv\Scripts\activate
python src/main.py
```

### First Use

1. **Launch** the application using `run_dev.bat`

2. **Project Setup:**
   - Artwork Name: Enter your project name
   - Date: Use YY-MM-DD format (defaults to today)

3. **Input Files:**
   - Master Video: Select a ProRes video file
   - R&D Folder: (Optional) Select folder with reference materials
   - Output Root: Choose where to create project folder

4. **Settings:**
   - Preset: Choose compression quality (default: Webflow Standard)
   - Encoder: x264 (quality) or NVENC (speed, requires NVIDIA GPU)

5. **Advanced** (Optional):
   - Scene threshold: Sensitivity for scene detection
   - Min scene length: Minimum frames per scene

6. **Process:**
   - Click "PROCESS" button
   - Wait for completion message
   - Output folder opens automatically

### Expected Output Structure

```
YY-MM-DD_ArtworkName/
├── Masters/
│   └── original.mov                # Your original ProRes file
├── Video-clips/
│   └── (Phase 2)
├── Stills/
│   ├── HQ/
│   │   └── ArtworkName_test_frame.png  # Test frame extraction
│   └── Compressed/
│       └── (Phase 2)
└── R&D/
    ├── High-res/
    └── Compressed/
```

### Logs & Database

- **Logs**: `logs/video_archive_YYYYMMDD_HHMMSS.log`
- **Database**: `config/state.db` (session tracking)
- **Config**: `config/settings.json` (user preferences)

### Troubleshooting

**"FFmpeg not found"**
- Download FFmpeg and place in `App/ffmpeg/`
- Or install to system PATH

**"Module not found"**
- Activate virtual environment: `venv\Scripts\activate`
- Check dependencies: `pip list`

**"Not ProRes" error**
- Ensure file is genuine ProRes 422/4444
- Check file isn't corrupted
- Try with different ProRes file

**GUI doesn't appear**
- Check Python includes tkinter (should be default)
- Check logs folder for error details

### What Works in Phase 1

✅ FFmpeg integration with GPU detection
✅ ProRes validation
✅ Output folder structure creation
✅ Master file copying
✅ Test frame extraction
✅ Database session tracking
✅ Configuration management
✅ Logging system

### Coming in Phase 2

- Scene detection with PySceneDetect
- Scene selection UI
- Batch still extraction (PNG + JPEG)
- Video clip generation
- Metadata embedding

### Support

- **Documentation**: See `PHASE1_COMPLETE.md` for detailed status
- **Technical Specs**: See `docs/TECHNICAL_SPECIFICATION.md`
- **Issues**: Check logs folder for detailed error information

---

*Ready to process your first project!*
