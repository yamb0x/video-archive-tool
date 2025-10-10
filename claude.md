# CLAUDE PROJECT RULES — ASSET PREP TOOL

## Core Principles
- 🧠 Always **read specification docs** in `docs/` folder before starting any new coding session.
- 🧩 The app is **Tkinter GUI-based**, not CLI — never switch to CLI-only.
- ⚙️ Use **ffmpeg** for all media operations (no external wrappers).
- ⚡ Default encoder: **x264**, optional **NVENC** toggle.
- 🧱 Folder structure and naming must always match spec in `docs/03_structure_naming.md`.
- 🧾 Every run must produce:
  - a `process_log.txt` file in the root
  - all four subfolders (even if empty)

## Coding Standards
- Write modular Python (split GUI, processing, config, and utils).
- Never break portability — app must run from `run_phase2.bat`.
- Respect `config.yaml` syncing both ways (GUI ↔ file).
- Keep GUI hybrid-style: clean layout, collapsible advanced panels, small amount of Yambo vibe.

## Behavior Rules
- On failure: **smart skip & log**, stop only if master file fails.
- Always use **GPU acceleration** where possible (`-hwaccel cuda`).
- Never convert colorspace — maintain native color.
- Always embed EXIF/XMP metadata.

## Versioning
- Follow sequential version naming: `YY-MM-DD_ArtworkName/`.
- If existing project detected → show overwrite/version dialog.

## Output Consistency
- Every still/clip must be numbered `01, 02, 03...` sequentially.
- Aspect ratio suffix: numeric only (`-16x9`, `-9x16`, etc.).
- Preserve preset quality values exactly as in the specs.

---

☑️ **Mission:** build a reliable, artist-friendly desktop automation that preps assets perfectly for Webflow and archiving — fast, elegant, deterministic.
