"""Video clip generation from scenes"""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional
import tempfile


class VideoClipGenerator:
    """Generate video clips from scenes"""

    def __init__(self, ffmpeg_wrapper):
        """
        Initialize clip generator

        Args:
            ffmpeg_wrapper: FFmpeg wrapper instance
        """
        self.logger = logging.getLogger(__name__)
        self.ffmpeg = ffmpeg_wrapper

    def extract_scene_clip(
        self,
        input_video: str,
        output_path: str,
        start_time: float,
        duration: float,
        use_gpu: bool = True,
        crf: int = 20,
        preset: str = "slow"
    ) -> bool:
        """
        Extract a single scene as video clip

        Args:
            input_video: Source video path
            output_path: Output clip path
            start_time: Start time in seconds
            duration: Duration in seconds
            use_gpu: Use GPU encoding if available
            crf: Constant Rate Factor for quality
            preset: Encoding preset

        Returns:
            True if successful
        """
        try:
            self.logger.info(
                f"Extracting clip: {start_time:.2f}s - {start_time + duration:.2f}s "
                f"({duration:.2f}s)"
            )

            cmd = [self.ffmpeg.ffmpeg_path]

            # Hardware acceleration
            if use_gpu and self.ffmpeg.cuda_available:
                cmd.extend(["-hwaccel", "cuda"])

            # Seek to start
            cmd.extend(["-ss", str(start_time)])

            # Input
            cmd.extend(["-i", input_video])

            # Duration
            cmd.extend(["-t", str(duration)])

            # Video encoding
            if use_gpu and self.ffmpeg.nvenc_available:
                cmd.extend([
                    "-c:v", "h264_nvenc",
                    "-preset", "p7",
                    "-rc", "vbr",
                    "-cq", str(crf),
                    "-b:v", "0",
                    "-profile:v", "high"
                ])
            else:
                cmd.extend([
                    "-c:v", "libx264",
                    "-crf", str(crf),
                    "-preset", preset,
                    "-profile:v", "high"
                ])

            # Audio
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "320k",
                "-ar", "48000"
            ])

            # Pixel format
            cmd.extend(["-pix_fmt", "yuv420p"])

            # Output
            cmd.extend(["-y", output_path])

            # Run command
            result = self.ffmpeg.run_command(cmd, timeout=600)

            if result.returncode == 0:
                output_size = Path(output_path).stat().st_size
                self.logger.info(
                    f"Clip created: {output_path} ({output_size / (1024*1024):.1f} MB)"
                )
                return True
            else:
                self.logger.error("Clip extraction failed")
                return False

        except Exception as e:
            self.logger.error(f"Error extracting clip: {e}")
            return False

    def concatenate_scenes(
        self,
        input_video: str,
        output_path: str,
        scenes: List,  # List of Scene objects
        use_gpu: bool = True,
        crf: int = 20,
        preset: str = "slow"
    ) -> bool:
        """
        Concatenate multiple scenes into single clip

        Args:
            input_video: Source video path
            output_path: Output clip path
            scenes: List of Scene objects to concatenate
            use_gpu: Use GPU encoding
            crf: Quality setting
            preset: Encoding preset

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Concatenating {len(scenes)} scenes")

            if len(scenes) == 1:
                # Single scene, just extract
                scene = scenes[0]
                return self.extract_scene_clip(
                    input_video, output_path,
                    scene.start_time, scene.duration,
                    use_gpu, crf, preset
                )

            # Create temp directory for segments
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract each scene as intermediate file
                segment_files = []
                for idx, scene in enumerate(scenes):
                    segment_file = temp_path / f"segment_{idx:03d}.mp4"

                    if not self.extract_scene_clip(
                        input_video, str(segment_file),
                        scene.start_time, scene.duration,
                        use_gpu, crf, preset
                    ):
                        self.logger.error(f"Failed to extract segment {idx}")
                        return False

                    segment_files.append(segment_file)

                # Create concat list file
                concat_list = temp_path / "concat_list.txt"
                with open(concat_list, 'w') as f:
                    for segment in segment_files:
                        # Use forward slashes for FFmpeg compatibility
                        f.write(f"file '{segment.as_posix()}'\n")

                # Concatenate using FFmpeg concat demuxer
                cmd = [
                    self.ffmpeg.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_list),
                    "-c", "copy",  # Copy without re-encoding for seamless concat
                    "-y",
                    output_path
                ]

                result = self.ffmpeg.run_command(cmd, timeout=600)

                if result.returncode == 0:
                    output_size = Path(output_path).stat().st_size
                    total_duration = sum(s.duration for s in scenes)
                    self.logger.info(
                        f"Concatenated clip created: {output_path}\n"
                        f"Duration: {total_duration:.2f}s, "
                        f"Size: {output_size / (1024*1024):.1f} MB"
                    )
                    return True
                else:
                    self.logger.error("Concatenation failed")
                    return False

        except Exception as e:
            self.logger.error(f"Error concatenating scenes: {e}")
            return False

    def generate_clips_from_scenes(
        self,
        input_video: str,
        output_dir: str,
        artwork_name: str,
        scenes: List,
        use_gpu: bool = True,
        crf: int = 20,
        preset: str = "slow"
    ) -> List[str]:
        """
        Generate individual clips for all scenes

        Args:
            input_video: Source video
            output_dir: Output directory
            artwork_name: Artwork name for filenames
            scenes: List of Scene objects
            use_gpu: Use GPU encoding
            crf: Quality setting
            preset: Encoding preset

        Returns:
            List of created clip paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_clips = []

        for scene in scenes:
            # Generate filename
            filename = f"{artwork_name}_clip_{scene.scene_number:02d}.mp4"
            clip_path = output_path / filename

            if self.extract_scene_clip(
                input_video, str(clip_path),
                scene.start_time, scene.duration,
                use_gpu, crf, preset
            ):
                created_clips.append(str(clip_path))
            else:
                self.logger.warning(f"Failed to create clip for scene {scene.scene_number}")

        self.logger.info(f"Created {len(created_clips)}/{len(scenes)} clips")
        return created_clips
