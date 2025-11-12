"""
Template Manager - Handles template layouts and content positioning for social media prep
"""

import os
import json
from typing import Tuple, Dict, List, Optional
from pathlib import Path
from PIL import Image


class TemplateManager:
    """Manages template layouts and calculates content positioning for 1080x1350 social media format"""

    def __init__(self, templates_dir: str, config_path: str = "config/template_coordinates.json"):
        """
        Initialize template manager

        Args:
            templates_dir: Path to directory containing template background images
            config_path: Path to template coordinates configuration file
        """
        self.templates_dir = templates_dir
        self.config_path = config_path
        self.TEMPLATES = {}

        # Load templates from config file
        self._load_template_config()
        self._validate_templates()

    def _load_template_config(self):
        """Load template coordinates from JSON configuration file"""
        try:
            # Try to load from config file
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Convert JSON config to internal format
                self.TEMPLATES = self._convert_config_to_templates(config)
                print(f"Loaded template coordinates from: {self.config_path}")
            else:
                # Fallback to hardcoded defaults
                print(f"Warning: Config file not found: {self.config_path}")
                print("Using hardcoded template coordinates")
                self.TEMPLATES = self._get_default_templates()
        except Exception as e:
            print(f"Error loading template config: {e}")
            print("Using hardcoded template coordinates")
            self.TEMPLATES = self._get_default_templates()

    def _convert_config_to_templates(self, config: dict) -> dict:
        """
        Convert JSON config format to internal TEMPLATES format

        Args:
            config: Loaded JSON configuration

        Returns:
            Dictionary in TEMPLATES format
        """
        templates = {}
        canvas_size = (
            config['canvas_size']['width'],
            config['canvas_size']['height']
        )

        for template_id, template_data in config['templates'].items():
            # Check if dual template
            if template_data.get('dual_template', False):
                # Dual template (2x-16-9)
                top = template_data['coordinates']['top']
                bottom = template_data['coordinates']['bottom']

                templates[template_id] = {
                    "name": template_data['name'],
                    "canvas_size": canvas_size,
                    "content_areas": [
                        (top['x'], top['y'], top['width'], top['height']),
                        (bottom['x'], bottom['y'], bottom['width'], bottom['height'])
                    ],
                    "background_file": template_data['background_file'],
                    "aspect_ratio": template_data.get('aspect_ratio')
                }
            else:
                # Single template
                coords = template_data['coordinates']

                templates[template_id] = {
                    "name": template_data['name'],
                    "canvas_size": canvas_size,
                    "content_area": (coords['x'], coords['y'], coords['width'], coords['height']),
                    "background_file": template_data['background_file'],
                    "aspect_ratio": template_data.get('aspect_ratio')
                }

        return templates

    def _get_default_templates(self) -> dict:
        """Get hardcoded default templates as fallback"""
        return {
            "full": {
                "name": "Full Canvas",
                "canvas_size": (1080, 1350),
                "content_area": (0, 0, 1080, 1350),
                "background_file": "full.png",
                "aspect_ratio": None
            },
            "1-1-small": {
                "name": "Square Small (1:1)",
                "canvas_size": (1080, 1350),
                "content_area": (147, 269, 786, 786),
                "background_file": "1-1-small.png",
                "aspect_ratio": 1.0
            },
            "1-1-large": {
                "name": "Square Large (1:1)",
                "canvas_size": (1080, 1350),
                "content_area": (36, 158, 1008, 1008),
                "background_file": "1-1-large.png",
                "aspect_ratio": 1.0
            },
            "16-9": {
                "name": "Landscape (16:9)",
                "canvas_size": (1080, 1350),
                "content_area": (36, 357, 1008, 567),
                "background_file": "16-9.png",
                "aspect_ratio": 16/9
            },
            "2x-16-9": {
                "name": "Dual Landscape (2x 16:9)",
                "canvas_size": (1080, 1350),
                "content_areas": [
                    (36, 82, 1008, 567),
                    (36, 701, 1008, 567)
                ],
                "background_file": "2x 16-9.png",
                "aspect_ratio": 16/9
            }
        }

    def _validate_templates(self):
        """Verify all template background files exist"""
        for template_id, spec in self.TEMPLATES.items():
            if template_id == "2x-16-9":
                continue  # Skip dual template for now

            bg_path = os.path.join(self.templates_dir, spec["background_file"])
            if not os.path.exists(bg_path):
                print(f"Warning: Template background not found: {bg_path}")

    def get_template_names(self) -> List[str]:
        """Get list of available template IDs"""
        return list(self.TEMPLATES.keys())

    def get_template_display_names(self) -> Dict[str, str]:
        """Get mapping of template IDs to display names"""
        return {tid: spec["name"] for tid, spec in self.TEMPLATES.items()}

    def auto_assign_template(self, image_width: int, image_height: int) -> str:
        """
        Automatically assign best template based on source aspect ratio

        Args:
            image_width: Source image/video width
            image_height: Source image/video height

        Returns:
            Template ID that best fits the source content
        """
        source_aspect = image_width / image_height

        # Square-ish (0.95 to 1.05 aspect ratio)
        if 0.95 <= source_aspect <= 1.05:
            return "1-1-small"

        # Landscape (aspect >= 1.6)
        elif source_aspect >= 1.6:
            return "16-9"

        # Portrait or unusual - use full canvas
        else:
            return "full"

    def calculate_center_crop(
        self,
        source_width: int,
        source_height: int,
        template_id: str
    ) -> Tuple[int, int, int, int]:
        """
        Calculate center-crop box from source to fit template content area

        Args:
            source_width: Source media width
            source_height: Source media height
            template_id: Target template ID

        Returns:
            Crop box (x, y, width, height) in source coordinates
        """
        if template_id not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")

        spec = self.TEMPLATES[template_id]
        content_area = spec["content_area"]
        target_width = content_area[2]
        target_height = content_area[3]

        # Calculate target aspect ratio
        target_aspect = target_width / target_height
        source_aspect = source_width / source_height

        if source_aspect > target_aspect:
            # Source is wider - crop width
            crop_height = source_height
            crop_width = int(crop_height * target_aspect)
            crop_x = (source_width - crop_width) // 2
            crop_y = 0
        else:
            # Source is taller - crop height
            crop_width = source_width
            crop_height = int(crop_width / target_aspect)
            crop_x = 0
            crop_y = (source_height - crop_height) // 2

        return (crop_x, crop_y, crop_width, crop_height)

    def get_template_background(self, template_id: str) -> Image.Image:
        """
        Load template background image

        Args:
            template_id: Template ID

        Returns:
            PIL Image of template background
        """
        if template_id not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")

        spec = self.TEMPLATES[template_id]
        bg_path = os.path.join(self.templates_dir, spec["background_file"])

        if not os.path.exists(bg_path):
            # Create white background if template file missing
            return Image.new('RGB', spec["canvas_size"], color='white')

        return Image.open(bg_path).convert('RGB')

    def get_content_area(self, template_id: str) -> Tuple[int, int, int, int]:
        """
        Get content area position and size for template

        Args:
            template_id: Template ID

        Returns:
            Content area (x, y, width, height)
            For dual templates (2x-16-9), returns first area
        """
        if template_id not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")

        template_spec = self.TEMPLATES[template_id]

        # Check if dual template
        if 'content_areas' in template_spec:
            # Return first area for dual templates
            return template_spec['content_areas'][0]

        return template_spec["content_area"]

    def get_ffmpeg_crop_filter(
        self,
        source_width: int,
        source_height: int,
        template_id: str
    ) -> str:
        """
        Generate FFmpeg crop filter string for video processing

        Args:
            source_width: Source video width
            source_height: Source video height
            template_id: Target template ID

        Returns:
            FFmpeg filter string for cropping and scaling
        """
        crop_box = self.calculate_center_crop(source_width, source_height, template_id)
        content_area = self.get_content_area(template_id)

        crop_x, crop_y, crop_w, crop_h = crop_box
        target_w, target_h = content_area[2], content_area[3]

        # FFmpeg filter: crop then scale
        return f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={target_w}:{target_h}"

    def get_ffmpeg_overlay_filter(
        self,
        source_width: int,
        source_height: int,
        template_id: str
    ) -> str:
        """
        Generate FFmpeg overlay filter for compositing video on template

        Args:
            source_width: Source video width
            source_height: Source video height
            template_id: Target template ID

        Returns:
            Complete FFmpeg filter_complex string
        """
        content_area = self.get_content_area(template_id)
        overlay_x, overlay_y = content_area[0], content_area[1]

        crop_filter = self.get_ffmpeg_crop_filter(source_width, source_height, template_id)

        # Filter complex: [1:v] = input video, [0:v] = template background
        return f"[1:v]{crop_filter}[fg];[0:v][fg]overlay={overlay_x}:{overlay_y}"
