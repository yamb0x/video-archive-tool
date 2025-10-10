# Performance & Reliability

## GPU Utilization
- `ffmpeg -hwaccel cuda` for decode/scaling.
- Auto-fallback to CPU.
- Future: optional OpenCV CUDA for frame ops.

## Atomic Workflow
- Temp writes → rename after completion.
- Reruns: overwrite/version dialog.
- Deterministic outputs for same config.

## Failure Policy
- Smart skip & log (non-critical).
- Halt on master failure.
- Full log + summary in UI and `process_log.txt`.

## Logging
- ffmpeg commands + stderr output.
- GPU detection + timing.
- Per-asset success/fail list.
- Log saved in root + displayed in verbose pane.

