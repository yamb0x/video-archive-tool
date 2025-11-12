"""
Media Scanner - Scans folders for images and videos
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path
from PIL import Image
import cv2


class MediaScanner:
    """Scans directories for supported image and video files"""

    # Supported file formats
    SUPPORTED_IMAGES = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    SUPPORTED_VIDEOS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.webm'}

    def __init__(self):
        """Initialize media scanner"""
        pass

    def scan_folder(self, folder_path: str) -> List[dict]:
        """
        Scan folder for supported media files

        Args:
            folder_path: Path to folder to scan

        Returns:
            List of file info dictionaries with metadata
        """
        if not os.path.exists(folder_path):
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not os.path.isdir(folder_path):
            raise ValueError(f"Not a directory: {folder_path}")

        media_files = []

        # Get all files in directory (non-recursive)
        for entry in os.scandir(folder_path):
            if not entry.is_file():
                continue

            file_ext = Path(entry.name).suffix.lower()

            if file_ext in self.SUPPORTED_IMAGES:
                file_info = self._get_image_info(entry.path)
                if file_info:
                    media_files.append(file_info)

            elif file_ext in self.SUPPORTED_VIDEOS:
                file_info = self._get_video_info(entry.path)
                if file_info:
                    media_files.append(file_info)

        # Sort by filename for consistent ordering
        media_files.sort(key=lambda x: x['filename'].lower())

        return media_files

    def _get_image_info(self, file_path: str) -> Optional[dict]:
        """
        Get metadata for image file

        Args:
            file_path: Path to image file

        Returns:
            Dictionary with file info or None if unreadable
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                return {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'type': 'image',
                    'width': width,
                    'height': height,
                    'aspect_ratio': width / height,
                    'size_bytes': os.path.getsize(file_path),
                    'format': img.format
                }
        except Exception as e:
            print(f"Warning: Could not read image {file_path}: {e}")
            return None

    def _get_video_info(self, file_path: str) -> Optional[dict]:
        """
        Get metadata for video file

        Args:
            file_path: Path to video file

        Returns:
            Dictionary with file info or None if unreadable
        """
        try:
            cap = cv2.VideoCapture(file_path)

            if not cap.isOpened():
                print(f"Warning: Could not open video {file_path}")
                return None

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()

            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'type': 'video',
                'width': width,
                'height': height,
                'aspect_ratio': width / height if height > 0 else 0,
                'size_bytes': os.path.getsize(file_path),
                'fps': fps,
                'duration_seconds': duration,
                'frame_count': frame_count
            }
        except Exception as e:
            print(f"Warning: Could not read video {file_path}: {e}")
            return None

    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if file is a supported media type

        Args:
            file_path: Path to file

        Returns:
            True if supported image or video
        """
        ext = Path(file_path).suffix.lower()
        return ext in (self.SUPPORTED_IMAGES | self.SUPPORTED_VIDEOS)

    def get_file_type(self, file_path: str) -> Optional[str]:
        """
        Get file type (image or video)

        Args:
            file_path: Path to file

        Returns:
            'image', 'video', or None if unsupported
        """
        ext = Path(file_path).suffix.lower()

        if ext in self.SUPPORTED_IMAGES:
            return 'image'
        elif ext in self.SUPPORTED_VIDEOS:
            return 'video'
        else:
            return None

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format

        Args:
            size_bytes: File size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format video duration in human-readable format

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "1:23")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
