# CLAUDE PROJECT RULES - SOCIAL MEDIA CONTENT PREP

## Core Principles
- Read BUG_FIXES.md before modifying template positioning
- This is a Tkinter GUI-based social media prep tool
- Use FFmpeg for all video operations with NVENC/CPU fallback
- Default encoder: x264, optional NVENC toggle
- Template coordinates configurable via config/template_coordinates.json
- All outputs must be 1080x1350 pixels (Instagram portrait format)

## Coding Standards
- Modular Python architecture: core, processors, GUI, models, utils
- App runs from run_social.bat for portability
- Template coordinates loaded from JSON config file
- Keep GUI clean and functional

## Template System
- Templates define content positioning on 1080x1350 canvas
- Center-crop algorithm maintains aspect ratios without stretching
- Single templates: full, 1-1-small, 1-1-large, 16-9
- Dual template: 2x-16-9 (merges two images)
- Coordinates user-adjustable via config/template_coordinates.json
- Template backgrounds in tamplates/ folder

## Processing Behavior
- Images: Parallel processing using ThreadPoolExecutor
- Videos: Sequential processing with progress callbacks
- Smart skip and log on failure, continue processing
- GPU acceleration (NVENC) where available
- Preserve native colorspace
- Embed metadata where supported

## Output Consistency
- Naming: {sequence}-{projectname}_{template}_{variant}.{ext}
- Sequential numbering: 01, 02, 03...
- Template suffix: 16-9, 1-1-small, etc.
- Single output folder
- Process log for every batch

## Auto-Template Pattern
- Pattern: full, 16-9, 16-9, full, 16-9, 16-9... (repeating)
- User can override individual templates

## Mission
Build a reliable desktop tool for Instagram content preparation with template-based layouts, intelligent cropping, and batch processing efficiency.
