"""
MediaFile - Data model for media files with ordering and template assignment
"""

import os
from typing import Optional, Dict, Any


class MediaFile:
    """Represents a media file with sequencing, template assignment, and metadata"""

    def __init__(
        self,
        path: str,
        sequence: int,
        file_info: Dict[str, Any],
        template_manager=None
    ):
        """
        Initialize media file

        Args:
            path: Full path to media file
            sequence: Sequence number for ordering (1-based)
            file_info: Dictionary with file metadata (from MediaScanner)
            template_manager: Optional TemplateManager for auto-assignment
        """
        self.path = path
        self.sequence = sequence
        self.filename = file_info['filename']
        self.type = file_info['type']  # 'image' or 'video'
        self.width = file_info['width']
        self.height = file_info['height']
        self.aspect_ratio = file_info['aspect_ratio']
        self.size_bytes = file_info['size_bytes']
        self.format = file_info.get('format', '')

        # Video-specific properties
        self.fps = file_info.get('fps', 0)
        self.duration_seconds = file_info.get('duration_seconds', 0)
        self.frame_count = file_info.get('frame_count', 0)

        # Template assignment
        self.template = self._auto_assign_template(template_manager)

        # Processing state
        self.enabled = True
        self.processed = False
        self.output_path = None
        self.error_message = None

    def _auto_assign_template(self, template_manager) -> str:
        """
        Automatically assign template based on aspect ratio

        Args:
            template_manager: TemplateManager instance

        Returns:
            Template ID
        """
        if template_manager:
            return template_manager.auto_assign_template(self.width, self.height)

        # Fallback if no template manager
        aspect = self.aspect_ratio

        if 0.95 <= aspect <= 1.05:  # Square
            return "1-1-small"
        elif aspect >= 1.6:  # Landscape
            return "16-9"
        else:  # Portrait or unusual
            return "full"

    def generate_output_filename(self, project_name: str, variant: str = "01") -> str:
        """
        Generate output filename in format: {seq}-{project}_{template}_{variant}.{ext}

        Args:
            project_name: Sanitized project name
            variant: Variant number (default "01")

        Returns:
            Output filename
        """
        # Sanitize project name
        safe_project = self._sanitize_name(project_name)

        # Get file extension
        _, ext = os.path.splitext(self.filename)
        ext = ext.lower()

        # Convert template name to filename-safe format
        template_safe = self.template.replace(" ", "-")

        return f"{self.sequence}-{safe_project}_{template_safe}_{variant}{ext}"

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize project name for filename

        Args:
            name: Project name

        Returns:
            Safe filename string
        """
        # Convert to lowercase, replace spaces with underscores
        safe = name.lower().strip()
        safe = safe.replace(' ', '_')

        # Remove special characters, keep alphanumeric, underscore, hyphen
        safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-'))

        # Ensure not empty
        if not safe:
            safe = "project"

        return safe

    def get_display_info(self) -> str:
        """
        Get human-readable info string for display

        Returns:
            Info string (e.g., "1920x1080 • 2.5 MB • 16:9")
        """
        size_str = self._format_size(self.size_bytes)
        aspect_str = f"{self.aspect_ratio:.2f}:1"

        if self.type == 'video':
            duration_str = self._format_duration(self.duration_seconds)
            return f"{self.width}x{self.height} • {size_str} • {duration_str}"
        else:
            return f"{self.width}x{self.height} • {size_str}"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format video duration"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def set_template(self, template_id: str):
        """
        Manually set template

        Args:
            template_id: Template ID
        """
        self.template = template_id

    def mark_processed(self, output_path: str):
        """
        Mark file as successfully processed

        Args:
            output_path: Path to output file
        """
        self.processed = True
        self.output_path = output_path
        self.error_message = None

    def mark_error(self, error_message: str):
        """
        Mark file as failed with error

        Args:
            error_message: Error description
        """
        self.processed = False
        self.error_message = error_message

    def __repr__(self) -> str:
        """String representation"""
        return f"MediaFile(seq={self.sequence}, file={self.filename}, template={self.template})"
