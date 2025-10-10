"""Video processor with ProRes validation and scene detection"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from .ffmpeg_wrapper import FFmpegWrapper


class VideoProcessor:
    """Main video processing class for master video handling"""

    def __init__(self, ffmpeg_wrapper: Optional[FFmpegWrapper] = None):
        """
        Initialize video processor

        Args:
            ffmpeg_wrapper: FFmpeg wrapper instance (creates new if None)
        """
        self.logger = logging.getLogger(__name__)
        self.ffmpeg = ffmpeg_wrapper or FFmpegWrapper()

    def validate_master_video(self, video_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate master video file

        Args:
            video_path: Path to master video

        Returns:
            Tuple of (is_valid, message, info_dict)
        """
        if not os.path.exists(video_path):
            return False, "File does not exist", {}

        try:
            # Get video info
            info = self.ffmpeg.get_video_info(video_path)

            # Check if ProRes
            is_prores = self.ffmpeg.validate_prores(video_path)

            if not is_prores:
                return False, f"Not ProRes: codec is {info.get('codec_long_name', 'unknown')}", info

            # Validate dimensions
            width = info.get('width', 0)
            height = info.get('height', 0)

            if width == 0 or height == 0:
                return False, "Invalid video dimensions", info

            # Validate duration
            duration = info.get('duration', 0)
            if duration == 0:
                return False, "Invalid video duration", info

            # Validate FPS
            fps = info.get('fps', 0)
            if fps == 0 or fps > 120:
                return False, f"Invalid frame rate: {fps}", info

            # Success
            profile = info.get('profile', 'Unknown')
            message = (
                f"Valid ProRes {profile} video\n"
                f"Resolution: {width}x{height}\n"
                f"Duration: {duration:.2f}s\n"
                f"FPS: {fps:.2f}\n"
                f"Size: {info.get('size_bytes', 0) / (1024*1024):.1f} MB"
            )

            self.logger.info(message)
            return True, message, info

        except Exception as e:
            self.logger.error(f"Error validating video: {e}")
            return False, f"Validation error: {str(e)}", {}

    def detect_aspect_ratio(self, width: int, height: int) -> str:
        """
        Detect aspect ratio and return suffix

        Args:
            width: Video width
            height: Video height

        Returns:
            Aspect ratio suffix (e.g., "16x9", "9x16", "1x1")
        """
        if width == 0 or height == 0:
            return "unknown"

        ratio = width / height

        # Common aspect ratios with tolerance
        tolerance = 0.1

        if abs(ratio - 16/9) < tolerance:
            return "16x9"
        elif abs(ratio - 9/16) < tolerance:
            return "9x16"
        elif abs(ratio - 1.0) < tolerance:
            return "1x1"
        elif abs(ratio - 4/3) < tolerance:
            return "4x3"
        elif abs(ratio - 21/9) < tolerance:
            return "21x9"
        elif abs(ratio - 2.35) < tolerance:
            return "235x100"
        else:
            # Return exact ratio
            return f"{width}x{height}"

    def create_output_structure(self, artwork_name: str, project_date: str, output_root: str) -> Dict[str, Path]:
        """
        Create standardized output folder structure

        Args:
            artwork_name: Name of artwork/project
            project_date: Date in YY-MM-DD format
            output_root: Root directory for output

        Returns:
            Dictionary of folder paths
        """
        # Create main project folder
        project_folder = Path(output_root) / f"{project_date}_{artwork_name}"

        # Define subfolder structure
        folders = {
            'root': project_folder,
            'masters': project_folder / "Masters",
            'video_clips': project_folder / "Video-clips",
            'stills_hq': project_folder / "Stills" / "HQ",
            'stills_compressed': project_folder / "Stills" / "Compressed",
            'rd_highres': project_folder / "R&D" / "High-res",
            'rd_compressed': project_folder / "R&D" / "Compressed"
        }

        # Create all folders
        for folder_key, folder_path in folders.items():
            folder_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created folder: {folder_path}")

        return folders

    def optimize_master_video(
        self,
        input_path: str,
        output_path: str,
        use_gpu: bool = True,
        crf: int = 20,
        preset: str = "slow"
    ) -> bool:
        """
        Optimize master ProRes video to H.264

        Args:
            input_path: Source ProRes video
            output_path: Output H.264 video
            use_gpu: Use GPU acceleration if available
            crf: Constant Rate Factor for quality
            preset: Encoding preset

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Optimizing master video: {input_path}")

            # Build encode command
            cmd = self.ffmpeg.build_encode_command(
                input_path=input_path,
                output_path=output_path,
                use_gpu=use_gpu,
                crf=crf,
                preset=preset
            )

            # Run encoding
            result = self.ffmpeg.run_command(cmd, timeout=3600)  # 1 hour timeout

            if result.returncode == 0:
                self.logger.info(f"Successfully optimized to: {output_path}")
                return True
            else:
                self.logger.error("Optimization failed")
                return False

        except Exception as e:
            self.logger.error(f"Error optimizing video: {e}")
            return False

    def extract_frame(
        self,
        video_path: str,
        output_path: str,
        timestamp: float,
        preserve_color: bool = True
    ) -> bool:
        """
        Extract a single frame from video

        Args:
            video_path: Source video
            output_path: Output image path
            timestamp: Time in seconds
            preserve_color: Preserve native color space

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Extracting frame at {timestamp}s to {output_path}")

            cmd = self.ffmpeg.build_extract_frame_command(
                input_path=video_path,
                output_path=output_path,
                timestamp=timestamp,
                preserve_color=preserve_color
            )

            result = self.ffmpeg.run_command(cmd, timeout=60)

            if result.returncode == 0:
                self.logger.info("Frame extraction successful")
                return True
            else:
                self.logger.error("Frame extraction failed")
                return False

        except Exception as e:
            self.logger.error(f"Error extracting frame: {e}")
            return False

    def get_master_copy_path(self, folders: Dict[str, Path], source_path: str) -> Path:
        """
        Get path for master copy in output structure

        Args:
            folders: Output folder structure dict
            source_path: Original source file path

        Returns:
            Path for master copy
        """
        source_filename = Path(source_path).name
        return folders['masters'] / source_filename

    def copy_master_to_output(self, source_path: str, folders: Dict[str, Path]) -> bool:
        """
        Copy original master video to output structure

        Args:
            source_path: Source video path
            folders: Output folder structure

        Returns:
            True if successful
        """
        try:
            import shutil

            dest_path = self.get_master_copy_path(folders, source_path)
            self.logger.info(f"Copying master to: {dest_path}")

            shutil.copy2(source_path, dest_path)

            self.logger.info(f"Master copy complete: {dest_path.stat().st_size / (1024*1024):.1f} MB")
            return True

        except Exception as e:
            self.logger.error(f"Error copying master: {e}")
            return False

    def generate_filename(
        self,
        artwork_name: str,
        file_type: str,
        sequence: int,
        aspect_ratio: Optional[str] = None,
        extension: str = "png"
    ) -> str:
        """
        Generate standardized filename

        Args:
            artwork_name: Artwork/project name
            file_type: Type of file (e.g., "HQ", "compressed", "clip")
            sequence: Sequence number
            aspect_ratio: Aspect ratio suffix (e.g., "16x9")
            extension: File extension

        Returns:
            Formatted filename
        """
        # Format sequence with leading zeros
        seq_str = f"{sequence:02d}"

        # Build filename parts
        parts = [artwork_name, file_type, seq_str]

        # Add aspect ratio if provided
        if aspect_ratio:
            parts.append(aspect_ratio)

        # Join with underscores and add extension
        filename = "_".join(parts) + f".{extension}"

        return filename
