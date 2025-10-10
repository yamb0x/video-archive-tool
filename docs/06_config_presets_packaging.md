# Config, Presets & Packaging

## Config
Editable `config.yaml` in app folder, mirrored in GUI.
Stores:
- Cut threshold
- Default encoder
- CRFs per preset
- Downscale flags
- Naming behavior
- R&D recursion
- Overwrite policy default

## Presets
### Webflow Standard
HQ PNG full res  
Web JPG q=90 full res  
Clips: H.264 full res (or FullHD option), CRF 20

### Retina/Web Showcase
JPG q=90, max width 2560px  
Clips: 1440p, CRF 19

### Ultra-Light Web (Thumbnails)
JPG q=82, max width 1600px

## Distribution
**Portable folder structure**
App/
├── App.exe
├── ffmpeg/
├── configs/config.yaml
├── Run.bat
└── logs/

No installation required.  
Source version optional (`venv` + `requirements.txt`).