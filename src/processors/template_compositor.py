"""
Template Compositor - Composites images and videos onto template backgrounds
"""

import os
from typing import Optional, Tuple
from PIL import Image, ImageOps
import logging

from core.template_manager import TemplateManager
from models.media_file import MediaFile


class TemplateCompositor:
    """Handles compositing media files onto template backgrounds"""

    def __init__(self, template_manager: TemplateManager, ffmpeg_wrapper=None):
        """
        Initialize compositor

        Args:
            template_manager: TemplateManager instance
            ffmpeg_wrapper: Optional FFmpegWrapper for video processing
        """
        self.template_manager = template_manager
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.logger = logging.getLogger(__name__)

    def process_file(
        self,
        media_file: MediaFile,
        project_name: str,
        output_dir: str,
        preset: dict,
        progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Process a media file (image or video) onto template

        Args:
            media_file: MediaFile instance
            project_name: Project name for output filename
            output_dir: Output directory path
            preset: Preset settings dictionary
            progress_callback: Optional callback(current, total, status)

        Returns:
            Tuple of (success: bool, output_path or error_message)
        """
        try:
            # Generate output filename
            output_filename = media_file.generate_output_filename(project_name)
            output_path = os.path.join(output_dir, output_filename)

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Process based on file type
            if media_file.type == 'image':
                success = self._process_image(media_file, output_path, preset)
            else:  # video
                success = self._process_video(media_file, output_path, preset, progress_callback)

            if success:
                media_file.mark_processed(output_path)
                return True, output_path
            else:
                error_msg = "Processing failed"
                media_file.mark_error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Error processing {media_file.filename}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            media_file.mark_error(error_msg)
            return False, error_msg

    def _process_image(
        self,
        media_file: MediaFile,
        output_path: str,
        preset: dict,
        second_media_file: MediaFile = None
    ) -> bool:
        """
        Process image file onto template background
        For 2x-16-9 template, can merge two images

        Args:
            media_file: MediaFile instance
            output_path: Output file path
            preset: Preset settings
            second_media_file: Optional second MediaFile for 2x-16-9 template

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Processing image: {media_file.filename} -> {os.path.basename(output_path)}")

            # Get image settings from preset
            image_settings = preset.get('settings', {}).get('image', {})
            quality = image_settings.get('quality', 90)
            output_format = image_settings.get('format', 'JPEG').upper()
            progressive = image_settings.get('progressive', True)
            optimize = image_settings.get('optimize', True)

            # Load template background
            template_bg = self.template_manager.get_template_background(media_file.template)

            # Check if this is a dual template (2x-16-9)
            template_spec = self.template_manager.TEMPLATES[media_file.template]
            is_dual = 'content_areas' in template_spec

            if is_dual and second_media_file:
                # Process dual image template
                content_areas = template_spec['content_areas']

                # Process first image (top)
                source_img1 = Image.open(media_file.path)
                if source_img1.mode not in ('RGB', 'RGBA'):
                    source_img1 = source_img1.convert('RGB')

                target_x1, target_y1, target_w1, target_h1 = content_areas[0]
                processed1 = self._process_single_image_for_area(
                    source_img1, target_w1, target_h1, output_format
                )

                # Process second image (bottom)
                source_img2 = Image.open(second_media_file.path)
                if source_img2.mode not in ('RGB', 'RGBA'):
                    source_img2 = source_img2.convert('RGB')

                target_x2, target_y2, target_w2, target_h2 = content_areas[1]
                processed2 = self._process_single_image_for_area(
                    source_img2, target_w2, target_h2, output_format
                )

                # Composite both onto template
                if template_bg.mode == 'RGBA':
                    template_bg = template_bg.convert('RGB')

                template_bg.paste(processed1, (target_x1, target_y1))
                template_bg.paste(processed2, (target_x2, target_y2))

            else:
                # Single image template
                source_img = Image.open(media_file.path)

                # Convert to RGB if necessary
                if source_img.mode not in ('RGB', 'RGBA'):
                    source_img = source_img.convert('RGB')

                # Calculate center crop
                crop_box = self.template_manager.calculate_center_crop(
                    source_img.width,
                    source_img.height,
                    media_file.template
                )

                # Crop from center
                crop_x, crop_y, crop_w, crop_h = crop_box
                cropped = source_img.crop((
                    crop_x,
                    crop_y,
                    crop_x + crop_w,
                    crop_y + crop_h
                ))

                # Get target content area
                content_area = self.template_manager.get_content_area(media_file.template)
                target_x, target_y, target_w, target_h = content_area

                # Resize to fit content area
                resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

                # Convert to RGB if needed (for JPEG)
                if resized.mode == 'RGBA' and output_format == 'JPEG':
                    # Create white background for transparency
                    rgb_img = Image.new('RGB', resized.size, (255, 255, 255))
                    rgb_img.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
                    resized = rgb_img

                # Composite onto template
                if template_bg.mode == 'RGBA' and resized.mode == 'RGB':
                    template_bg = template_bg.convert('RGB')
                elif template_bg.mode == 'RGB' and resized.mode == 'RGBA':
                    resized = resized.convert('RGB')

                template_bg.paste(resized, (target_x, target_y))

            # Save with appropriate settings
            save_kwargs = {}

            if output_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = optimize
                save_kwargs['progressive'] = progressive
                # Ensure RGB mode for JPEG
                if template_bg.mode != 'RGB':
                    template_bg = template_bg.convert('RGB')
            elif output_format == 'PNG':
                save_kwargs['optimize'] = optimize
                save_kwargs['compress_level'] = 6

            template_bg.save(output_path, format=output_format, **save_kwargs)

            self.logger.info(f"Successfully saved: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error processing image {media_file.filename}: {str(e)}", exc_info=True)
            return False

    def _process_single_image_for_area(self, source_img: Image.Image, target_w: int, target_h: int, output_format: str) -> Image.Image:
        """
        Process a single image to fit a specific area with center crop

        Args:
            source_img: Source PIL Image
            target_w: Target width
            target_h: Target height
            output_format: Output format (JPEG or PNG)

        Returns:
            Processed PIL Image
        """
        # Calculate center crop for target dimensions
        target_aspect = target_w / target_h
        source_aspect = source_img.width / source_img.height

        if source_aspect > target_aspect:
            # Source is wider - crop width
            crop_h = source_img.height
            crop_w = int(crop_h * target_aspect)
            crop_x = (source_img.width - crop_w) // 2
            crop_y = 0
        else:
            # Source is taller - crop height
            crop_w = source_img.width
            crop_h = int(crop_w / target_aspect)
            crop_x = 0
            crop_y = (source_img.height - crop_h) // 2

        # Crop and resize
        cropped = source_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Convert to RGB if needed
        if resized.mode == 'RGBA' and output_format == 'JPEG':
            rgb_img = Image.new('RGB', resized.size, (255, 255, 255))
            rgb_img.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
            resized = rgb_img
        elif resized.mode not in ('RGB', 'RGBA'):
            resized = resized.convert('RGB')

        return resized

    def _process_video(
        self,
        media_file: MediaFile,
        output_path: str,
        preset: dict,
        progress_callback=None
    ) -> bool:
        """
        Process video file onto template background using FFmpeg

        Args:
            media_file: MediaFile instance
            output_path: Output file path
            preset: Preset settings
            progress_callback: Optional progress callback

        Returns:
            True if successful
        """
        if not self.ffmpeg_wrapper:
            self.logger.error("FFmpeg wrapper not available for video processing")
            return False

        try:
            self.logger.info(f"Processing video: {media_file.filename} -> {os.path.basename(output_path)}")

            # Get video settings from preset
            video_settings = preset.get('settings', {}).get('video', {})

            # Get template background path
            template_spec = self.template_manager.TEMPLATES[media_file.template]
            template_bg_path = os.path.join(
                self.template_manager.templates_dir,
                template_spec['background_file']
            )

            # Build FFmpeg overlay command
            overlay_filter = self.template_manager.get_ffmpeg_overlay_filter(
                media_file.width,
                media_file.height,
                media_file.template
            )

            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(
                template_bg_path,
                media_file.path,
                output_path,
                overlay_filter,
                video_settings
            )

            # Execute FFmpeg
            self.logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

            success, error = self.ffmpeg_wrapper.run_command(
                cmd,
                progress_callback=progress_callback
            )

            if success:
                self.logger.info(f"Successfully processed video: {output_path}")
                return True
            else:
                self.logger.error(f"FFmpeg failed: {error}")
                return False

        except Exception as e:
            self.logger.error(f"Error processing video {media_file.filename}: {str(e)}", exc_info=True)
            return False

    def _build_ffmpeg_command(
        self,
        template_path: str,
        video_path: str,
        output_path: str,
        overlay_filter: str,
        video_settings: dict
    ) -> list:
        """
        Build FFmpeg command for video compositing

        Args:
            template_path: Path to template background image
            video_path: Path to source video
            output_path: Path to output video
            overlay_filter: FFmpeg overlay filter string
            video_settings: Video encoding settings

        Returns:
            FFmpeg command as list
        """
        cmd = [self.ffmpeg_wrapper.ffmpeg_path, '-y']

        # Input: template background (loop it for video duration)
        cmd.extend(['-loop', '1', '-i', template_path])

        # Input: source video
        cmd.extend(['-i', video_path])

        # Filter complex for overlay
        cmd.extend(['-filter_complex', overlay_filter])

        # Video codec and settings
        codec = video_settings.get('codec', 'h264')

        if codec == 'h264_nvenc':
            # GPU encoding
            cmd.extend(['-c:v', 'h264_nvenc'])
            cmd.extend(['-preset', video_settings.get('preset', 'p7')])
            cmd.extend(['-b:v', video_settings.get('bitrate', '8000k')])
            if 'max_bitrate' in video_settings:
                cmd.extend(['-maxrate', video_settings['max_bitrate']])
            if 'bufsize' in video_settings:
                cmd.extend(['-bufsize', video_settings['bufsize']])
        else:
            # CPU encoding
            cmd.extend(['-c:v', 'libx264'])
            cmd.extend(['-preset', video_settings.get('preset', 'medium')])
            cmd.extend(['-b:v', video_settings.get('bitrate', '5000k')])
            if 'max_bitrate' in video_settings:
                cmd.extend(['-maxrate', video_settings['max_bitrate']])
            if 'bufsize' in video_settings:
                cmd.extend(['-bufsize', video_settings['bufsize']])

        # Profile and level
        if 'profile' in video_settings:
            cmd.extend(['-profile:v', video_settings['profile']])
        if 'level' in video_settings:
            cmd.extend(['-level', video_settings['level']])

        # Pixel format
        cmd.extend(['-pix_fmt', video_settings.get('pixel_format', 'yuv420p')])

        # FPS
        fps = video_settings.get('fps', 30)
        if fps:
            cmd.extend(['-r', str(fps)])

        # Audio settings
        audio_settings = video_settings.get('audio', {})
        if audio_settings:
            cmd.extend(['-c:a', audio_settings.get('codec', 'aac')])
            cmd.extend(['-b:a', audio_settings.get('bitrate', '192k')])
            cmd.extend(['-ar', str(audio_settings.get('sample_rate', 48000))])
        else:
            cmd.extend(['-an'])  # No audio

        # Use shortest stream (template or video)
        cmd.extend(['-shortest'])

        # Output file
        cmd.append(output_path)

        return cmd

    def create_preview(
        self,
        media_file: MediaFile,
        max_size: Tuple[int, int] = (400, 500)
    ) -> Optional[Image.Image]:
        """
        Create a preview image showing template overlay

        Args:
            media_file: MediaFile instance
            max_size: Maximum preview size (width, height)

        Returns:
            PIL Image preview or None if failed
        """
        try:
            if media_file.type == 'video':
                # For videos, extract first frame
                # This would need OpenCV or similar
                # For now, return None
                return None

            # Load template background
            template_bg = self.template_manager.get_template_background(media_file.template)

            # Load source image
            source_img = Image.open(media_file.path)

            # Calculate center crop
            crop_box = self.template_manager.calculate_center_crop(
                source_img.width,
                source_img.height,
                media_file.template
            )

            # Crop from center
            crop_x, crop_y, crop_w, crop_h = crop_box
            cropped = source_img.crop((
                crop_x,
                crop_y,
                crop_x + crop_w,
                crop_y + crop_h
            ))

            # Get target content area
            content_area = self.template_manager.get_content_area(media_file.template)
            target_x, target_y, target_w, target_h = content_area

            # Resize to fit content area
            resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Composite onto template
            if template_bg.mode != resized.mode:
                if 'A' in resized.mode:
                    resized = resized.convert('RGB')
                if 'A' in template_bg.mode:
                    template_bg = template_bg.convert('RGB')

            template_bg.paste(resized, (target_x, target_y))

            # Scale down for preview
            template_bg.thumbnail(max_size, Image.Resampling.LANCZOS)

            return template_bg

        except Exception as e:
            self.logger.error(f"Error creating preview: {str(e)}", exc_info=True)
            return None
