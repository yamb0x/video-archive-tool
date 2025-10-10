# Video Archive Tool
*Yambo Studio - Professional Video Processing & Archive Automation*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Phase 2](https://img.shields.io/badge/phase-2%20%E2%80%93%20Scene%20Detection-green.svg)](docs/)

## Overview
A desktop automation tool for preparing video assets for Webflow upload and intelligent project archiving. Optimized for creative studios working with ProRes master videos.

**Current Status**: Phase 2 - Full scene detection, still extraction, and video clip generation

## Features
- **ProRes Master Processing**: Validate and optimize ProRes 422/4444 videos
- **Automatic Scene Detection**: Detect cuts with adjustable sensitivity
- **Smart Asset Generation**:
  - High-quality PNG stills for archiving
  - Web-optimized JPEG stills for Webflow
  - H.264 video clips with scene grouping
- **R&D Folder Processing**: Batch process reference materials
- **GPU Acceleration**: NVIDIA CUDA support with automatic CPU fallback
- **Resume Capability**: Continue interrupted processing sessions
- **Metadata Embedding**: Copyright and processing information

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yamb0x/video-archive-tool.git
cd video-archive-tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run Phase 2 application
run_phase2.bat  # Windows
# python src/main_phase2.py  # Direct Python
```

### System Requirements
- **Python**: 3.11 or higher
- **OS**: Windows 10/11 (64-bit) | macOS 10.15+ | Linux
- **FFmpeg**: 4.4+ (automatically detected or manual installation)
- **GPU**: NVIDIA RTX series (optional, for NVENC acceleration)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2x the size of your largest video file

### Required Dependencies
- OpenCV (4.8.1+)
- PySceneDetect (0.6.2+)
- Pillow (10.1.0+)
- tkinter (included with Python)

## Usage

### Basic Workflow
1. **Launch**: Run `run_phase2.bat` or `python src/main_phase2.py`
2. **Set Project**: Enter artwork name and date (format: YY-MM-DD)
3. **Select Master**: Choose your video file (ProRes recommended)
4. **Configure Settings**:
   - Choose encoder (x264 or NVENC)
   - Adjust scene detection threshold
   - Set minimum scene length
5. **Process**: Click "Process Video"
6. **Scene Selection**:
   - Review auto-detected scenes with thumbnails
   - Select individual scenes for clips
   - Group multiple scenes into combined clips
   - Deselect scenes you don't want as clips
7. **Wait for Processing**:
   - Video clips generated from selected scenes
   - PNG stills extracted from ALL detected scenes
   - JPEG stills compressed for web
8. **Complete**: Review outputs in organized folder structure

### Output Structure
```
YY-MM-DD_ArtworkName/
├── Masters/              # Original + optimized master video
│   ├── [ArtworkName]_master_[ext]      # Original master copy
│   └── [ArtworkName]_master.mp4        # Optimized MP4 master
├── Video-clips/          # Scene-based video clips
│   ├── [ArtworkName]_clip_01.mp4       # Individual scene clips
│   ├── [ArtworkName]_clip_02.mp4
│   └── [ArtworkName]_group_01.mp4      # Grouped scene clips
└── Stills/
    ├── HQ/              # High-quality PNG stills (ALL scenes)
    │   ├── [ArtworkName]_01.png
    │   ├── [ArtworkName]_02.png
    │   └── ...
    └── Compressed/      # Web-optimized JPEG (ALL scenes)
        ├── [ArtworkName]_01.jpg
        ├── [ArtworkName]_02.jpg
        └── ...
```

**Note**: Stills are extracted from ALL detected scenes, while video clips are only created from selected scenes.

### Compression Presets

#### Webflow Standard
- **Best for**: General Webflow projects
- **Quality**: High (CRF 20)
- **Resolution**: Source

#### Retina/Web Showcase
- **Best for**: High-end portfolios
- **Quality**: Very High (CRF 19)
- **Resolution**: Up to 1440p

#### Ultra-Light Web
- **Best for**: Fast loading pages
- **Quality**: Good (CRF 23)
- **Resolution**: Up to 1080p

## Advanced Features

### Scene Detection
- **Adaptive Detection**: Uses PySceneDetect with content-aware algorithms
- **Adjustable Threshold**: 0.0-1.0 sensitivity control (default: 0.3)
- **Minimum Scene Length**: Prevent micro-scenes (default: 1.0s)
- **Interactive Selection**: Visual thumbnail-based scene picker
- **Scene Grouping**: Combine multiple scenes into single clips
- **Smart Extraction**: Midpoint frame extraction for representative stills

### GPU Acceleration
- **Automatic Detection**: NVIDIA GPU auto-detection on startup
- **NVENC Encoding**: Hardware-accelerated H.264 encoding
- **CPU Fallback**: Seamless x264 software encoding
- **Encoder Toggle**: Switch between GPU/CPU per project
- **Performance**: 3-5x faster encoding with NVENC

### Metadata Embedding
- **Copyright**: Embedded in all outputs
- **XMP/EXIF**: PNG and JPEG metadata
- **Project Info**: Artwork name, date, source file
- **Processing Data**: Encoder, settings, timestamps

### Session Management
- **SQLite Database**: Persistent state tracking
- **Progress Monitoring**: Real-time operation tracking
- **Session History**: View past processing sessions
- **Resume Capability**: (Planned for Phase 4)

## Development

### Running from Source
```bash
# Development mode (Phase 2)
python src/main_phase2.py

# Or use the batch file
run_phase2.bat

# Run Phase 1 (basic testing)
python src/main.py

# Run tests
pytest tests/
```

### Development Roadmap

#### ✅ Phase 1: Core Foundation (Completed)
- Master video validation
- Output folder structure
- Basic FFmpeg integration
- Configuration management

#### ✅ Phase 2: Scene Detection & Processing (Completed)
- Automatic scene detection with PySceneDetect
- Interactive scene selection GUI
- High-quality PNG still extraction (ALL scenes)
- Web-optimized JPEG compression (ALL scenes)
- H.264 video clip generation (selected scenes)
- Scene grouping and concatenation
- Metadata embedding (XMP/EXIF)

#### 🔄 Phase 3: R&D Folder Processing (In Progress)
- Batch image processing
- Smart image categorization
- Multi-resolution output
- Metadata preservation

#### 📋 Phase 4: Advanced Features (Planned)
- Session resume capability
- Preset management UI
- Batch project processing
- Progress reporting improvements

#### 🚀 Phase 5: Distribution (Planned)
- PyInstaller executable bundling
- Installer creation
- Auto-update mechanism
- Error reporting system

### Project Structure
```
video-archive-tool/
├── src/              # Source code
│   ├── core/        # Core processing
│   ├── gui/         # User interface
│   ├── processors/  # Video/image processors
│   └── database/    # State management
├── config/          # Configuration files
├── tests/           # Test suite
└── docs/            # Documentation
```

## Configuration

### Settings Location
`App/config/settings.json`

### Key Settings
- `scene_threshold`: Detection sensitivity (1-100)
- `encoder_preference`: "x264" or "nvenc"
- `copyright_text`: Embedded metadata
- `parallel_workers`: Processing threads

## Troubleshooting

### Common Issues

#### "FFmpeg not found"
- Ensure `App/ffmpeg/` contains ffmpeg.exe
- Download from [FFmpeg.org](https://ffmpeg.org)

#### "GPU acceleration unavailable"
- Check NVIDIA driver is updated
- Verify CUDA support
- Tool will automatically use CPU

#### "ProRes file not valid"
- Ensure file is genuine ProRes
- Check file isn't corrupted
- Try different ProRes variant

## Support
- **Documentation**: See `/docs` folder
- **Issues**: Report bugs on GitHub
- **Contact**: support@yambo.studio

## License
© 2024 Yambo Studio. All rights reserved.

## Credits
- **FFmpeg**: Video processing engine
- **PySceneDetect**: Scene detection
- **OpenCV**: Image processing
- **NVIDIA CUDA**: GPU acceleration

---

*Version 2.0.0 - Phase 2 (Scene Detection) - October 2025*
*Built with ❤️ by Yambo Studio*