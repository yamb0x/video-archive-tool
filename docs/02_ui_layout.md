# UI & Interaction Model

## Structure
Hybrid single-window layout with collapsible Advanced panels.

### Top Section
- **Artwork Name** (text field)
- **Date** (defaults to today)
- **Master ProRes picker**
- **R&D folder picker**
- **Output folder picker**
- **Preset dropdown**
  - Webflow Standard
  - Retina/Web Showcase
  - Ultra-Light Web (Thumbnails)
- **Encoder toggle:** x264 (default) / NVENC
- **Aspect ratio:** auto-detect with manual override dropdown

### Advanced Panels
**Cut Detection:** slider for threshold (saved to config) + “Analyze” button → results populate a timeline list with thumbnails.  
**Naming:** shows preview (`ArtworkName_HQ_01-16x9.png`).  
**Compression:** CRF display per preset + optional 1080p/1440p switches.  
**System:** GPU status, ffmpeg path, config location.

### Bottom Section
- **Run** button
- Determinate progress bar
- Collapsible verbose log panel
- Completion modal: summary (counts, sizes), open folder, and auto-saved `process_log.txt`.

