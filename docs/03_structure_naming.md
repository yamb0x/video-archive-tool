# Folder Structure & Naming

## Root Directory
`YY-MM-DD_ArtworkName/`

Always create:
1. `Masters/` – Original ProRes + optimized `ArtworkName_master_web.mp4`
2. `Video-clips/` – detected segments: `ArtworkName_01-16x9.mp4`, etc.
3. `Stills/` –  
   - `ArtworkName_HQ_01-16x9.png`  
   - `ArtworkName_compressed_01-16x9.jpg`
4. `R&D/` – recursively processed into:  
   - `R&D/high-res/`  
   - `R&D/compressed/`

## Naming Rules
- Sequential numbering: `01, 02, 03…`
- Numeric aspect ratio suffixes: `-16x9`, `-9x16`, `-1x1`
- Prefixes for HQ vs compressed
- Metadata embedded (EXIF/XMP):
  - `ArtworkName`
  - `ExportDate`
  - `SourceVideo`
- Native color preserved (no sRGB conversion)

