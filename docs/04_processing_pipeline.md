# Processing Pipeline

## Master Ingest
- Validate codec/FPS/dimensions/colorspace.
- Copy original to `Masters/`.
- Encode optimized MP4:
  - Default: x264 CRF 20, High profile, AAC 320 kbps
  - NVENC option for speed.

## Cut Detection
- PySceneDetect (content mode) or ffmpeg scene detection.
- Threshold slider (configurable).
- Generate midpoint thumbnails (ffmpeg, native color).
- Display cut list with thumbnails; user can deselect or merge.

## Export Steps
**Stills**
- Extract midpoint PNG (HQ).
- Derive JPG (Webflow optimized).

**Video Clips**
- Encode from master ProRes.
- CRF and scale per preset.
- Optional downscale (1080p/1440p).

**R&D**
- Recursive image → JPG q=90 or 82.
- Video → H.264 per chosen encoder.
- Maintain high-res/compressed split.

