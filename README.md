# Social Media Content Prep

Professional media formatting tool for Instagram and social platforms. Transform images and videos into 1080x1350 format with template-based layouts and intelligent compression.

## Quick Start

```bash
# Clone repository
git clone https://github.com/yamb0x/social-media-content-prep.git
cd social-media-content-prep

# Install dependencies
pip install -r requirements.txt

# Launch application
python src/main_social.py
```

**Windows**: Double-click `run_social.bat`

## Features

- Template-based layouts for 1080x1350 Instagram format
- Smart center-crop algorithm maintains aspect ratios
- Batch processing with file reordering
- GPU-accelerated encoding (NVENC) with CPU fallback
- Project-based naming with sequential numbering
- Parallel image processing for speed
- Professional compression presets

## Templates

All outputs are 1080x1350 pixels with configurable content positioning:

**Full Canvas** - Content fills entire canvas
**Square Small (1:1)** - Centered 786x786 square
**Square Large (1:1)** - Centered 1008x1008 square
**Landscape (16:9)** - Centered 1008x567 widescreen
**Dual Landscape (2x 16:9)** - Two stacked 1008x567 areas

Template coordinates are editable via `config/template_coordinates.json` for pixel-perfect alignment.

## Workflow

1. Enter project name
2. Load folder containing images/videos
3. Reorder files using up/down buttons
4. Assign templates (or use auto-template)
5. Select compression preset
6. Choose output folder and process

Output naming: `{sequence}-{projectname}_{template}_{variant}.{ext}`

Example: `1-brandlaunch_16-9_01.mp4`

## Presets

**Instagram High Quality** - 8Mbps video, 92% JPEG
**Instagram Medium** - 5Mbps video, 85% JPEG
**Instagram Fast** - 3.5Mbps video, 80% JPEG
**Social Media Ultra HQ** - 12Mbps video, PNG images
**Instagram High (GPU)** - NVENC hardware acceleration

## System Requirements

- Python 3.8+
- FFmpeg 4.4+ (included or in PATH)
- Windows 10/11, macOS 10.15+, or Linux
- Optional: NVIDIA GPU with NVENC for hardware acceleration

## Template Customization

Edit `config/template_coordinates.json` to adjust content positioning:

```json
{
  "templates": {
    "16-9": {
      "coordinates": {
        "x": 36,
        "y": 389,
        "width": 1008,
        "height": 567
      }
    }
  }
}
```

Restart application to apply changes.

## Project Structure

```
social-media-content-prep/
├── src/
│   ├── core/              # Template manager, media scanner, FFmpeg wrapper
│   ├── gui/               # Main window interface
│   ├── models/            # Media file data model
│   ├── processors/        # Template compositor, batch processor
│   └── utils/             # Configuration, logging
├── config/
│   ├── template_coordinates.json
│   └── default_presets.json
├── tamplates/             # Template background images
└── run_social.bat         # Windows launcher
```

## Configuration

Settings are stored in `config/default_presets.json` and `config/template_coordinates.json`.

Key configurations:
- Video codecs (h264, h264_nvenc)
- Image quality and formats
- Template positioning coordinates
- Encoding presets

## Troubleshooting

**FFmpeg not found**: Install FFmpeg from ffmpeg.org or place in App/ffmpeg/

**NVENC not available**: Requires NVIDIA GPU with updated drivers, will fallback to CPU encoding

**Template alignment issues**: Adjust coordinates in template_coordinates.json using image editor measurements

**Processing failures**: Check process_log.txt in output folder for detailed error information

## License

© 2024 Yambo Studio. All rights reserved.

## Credits

Built with FFmpeg, Pillow, and OpenCV.
