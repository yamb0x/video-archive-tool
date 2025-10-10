"""Generate test video file for development"""

import subprocess
import sys
from pathlib import Path


def create_test_video(output_path: str = "test_assets/test_video.mov", duration: int = 30):
    """
    Create a test video file using FFmpeg

    Args:
        output_path: Output video path
        duration: Duration in seconds
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Create test video with color changes (simulates scene changes)
    # This creates a video with different colored segments
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"color=c=red:s=1920x1080:d={duration//3}",
        "-f", "lavfi",
        "-i", f"color=c=green:s=1920x1080:d={duration//3}",
        "-f", "lavfi",
        "-i", f"color=c=blue:s=1920x1080:d={duration//3}",
        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex",
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]",
        "-map", "[outv]",
        "-map", "3:a",
        "-c:v", "prores_ks",
        "-profile:v", "3",  # ProRes 422 HQ
        "-c:a", "pcm_s16le",
        "-t", str(duration),
        "-y",
        str(output)
    ]

    print(f"Creating test video: {output}")
    print(f"Duration: {duration}s")
    print(f"Resolution: 1920x1080")
    print(f"Codec: ProRes 422 HQ")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"\n[OK] Test video created successfully: {output}")
        print(f"File size: {output.stat().st_size / (1024*1024):.1f} MB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error creating test video:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("\n[ERROR] FFmpeg not found!")
        print("Please install FFmpeg or add it to PATH")
        return False


if __name__ == "__main__":
    success = create_test_video()
    sys.exit(0 if success else 1)
