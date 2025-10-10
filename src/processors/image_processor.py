"""Image processing for stills extraction and compression"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image
import piexif


class ImageProcessor:
    """Process and optimize images with metadata embedding"""

    def __init__(self):
        """Initialize image processor"""
        self.logger = logging.getLogger(__name__)

    def compress_png_to_jpeg(
        self,
        input_path: str,
        output_path: str,
        quality: int = 90,
        max_width: Optional[int] = None,
        progressive: bool = True,
        optimize: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Convert PNG to optimized JPEG

        Args:
            input_path: Input PNG file
            output_path: Output JPEG file
            quality: JPEG quality (1-100)
            max_width: Maximum width (maintains aspect ratio)
            progressive: Use progressive JPEG
            optimize: Optimize file size
            metadata: EXIF metadata to embed

        Returns:
            True if successful
        """
        try:
            self.logger.debug(f"Converting {input_path} to JPEG (quality={quality})")

            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (PNG can have alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if needed
                if max_width and img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    self.logger.debug(f"Resized to {max_width}x{new_height}")

                # Prepare EXIF data if provided
                exif_bytes = None
                if metadata:
                    exif_bytes = self._create_exif(metadata)

                # Save as JPEG
                save_kwargs = {
                    'quality': quality,
                    'optimize': optimize,
                    'progressive': progressive
                }

                if exif_bytes:
                    save_kwargs['exif'] = exif_bytes

                img.save(output_path, 'JPEG', **save_kwargs)

            output_size = Path(output_path).stat().st_size
            self.logger.debug(f"JPEG created: {output_size / 1024:.1f} KB")
            return True

        except Exception as e:
            self.logger.error(f"Error converting to JPEG: {e}")
            return False

    def save_png_with_metadata(
        self,
        image_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save PNG with embedded metadata

        Args:
            image_path: Path to PNG file
            metadata: Metadata to embed

        Returns:
            True if successful
        """
        try:
            if not metadata:
                return True

            # PNG metadata is stored in PNG text chunks, not EXIF
            # For now, we'll add basic metadata support
            # Full EXIF embedding requires piexif with PNG support

            self.logger.debug(f"Adding metadata to PNG: {image_path}")

            with Image.open(image_path) as img:
                # Create PNG info
                info = {}
                if 'Copyright' in metadata:
                    info['Copyright'] = metadata['Copyright']
                if 'Creator' in metadata:
                    info['Author'] = metadata['Creator']
                if 'Description' in metadata:
                    info['Description'] = metadata['Description']

                # Re-save with metadata
                img.save(image_path, 'PNG', pnginfo=self._create_png_info(info))

            self.logger.debug("PNG metadata added")
            return True

        except Exception as e:
            self.logger.error(f"Error adding PNG metadata: {e}")
            return False

    def _create_exif(self, metadata: Dict[str, Any]) -> bytes:
        """
        Create EXIF data from metadata dict

        Args:
            metadata: Metadata dictionary

        Returns:
            EXIF bytes
        """
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        # Add copyright
        if 'Copyright' in metadata:
            exif_dict["0th"][piexif.ImageIFD.Copyright] = metadata['Copyright'].encode('utf-8')

        # Add artist/creator
        if 'Creator' in metadata:
            exif_dict["0th"][piexif.ImageIFD.Artist] = metadata['Creator'].encode('utf-8')

        # Add description
        if 'Description' in metadata:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = metadata['Description'].encode('utf-8')

        # Add software
        if 'Software' in metadata:
            exif_dict["0th"][piexif.ImageIFD.Software] = metadata['Software'].encode('utf-8')

        # Add custom fields in UserComment
        if 'Custom' in metadata:
            import json
            custom_json = json.dumps(metadata['Custom'])
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = custom_json.encode('utf-8')

        return piexif.dump(exif_dict)

    def _create_png_info(self, info_dict: Dict[str, str]):
        """
        Create PNG info from dictionary

        Args:
            info_dict: Info dictionary

        Returns:
            PngInfo object
        """
        from PIL.PngImagePlugin import PngInfo

        png_info = PngInfo()
        for key, value in info_dict.items():
            png_info.add_text(key, value)

        return png_info

    def batch_extract_stills(
        self,
        video_path: str,
        timestamps: list,
        output_dir: str,
        artwork_name: str,
        file_type: str,
        ffmpeg_wrapper,
        aspect_ratio: str,
        max_workers: int = 4,
        metadata: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Extract multiple stills in parallel

        Args:
            video_path: Source video
            timestamps: List of timestamps to extract
            output_dir: Output directory
            artwork_name: Artwork name for filenames
            file_type: File type suffix (e.g., "HQ", "compressed")
            ffmpeg_wrapper: FFmpeg wrapper instance
            aspect_ratio: Aspect ratio suffix
            max_workers: Maximum parallel workers
            metadata: Metadata to embed

        Returns:
            List of created file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        def extract_frame(idx, timestamp):
            """Extract single frame"""
            sequence = idx + 1
            filename = f"{artwork_name}_{file_type}_{sequence:02d}_{aspect_ratio}.png"
            frame_path = output_path / filename

            if ffmpeg_wrapper.run_command(
                ffmpeg_wrapper.build_extract_frame_command(
                    input_path=video_path,
                    output_path=str(frame_path),
                    timestamp=timestamp,
                    preserve_color=True
                ),
                timeout=60
            ).returncode == 0:
                # Add metadata to PNG
                if metadata:
                    self.save_png_with_metadata(str(frame_path), metadata)

                return str(frame_path)
            return None

        # Extract frames in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(extract_frame, idx, ts): (idx, ts)
                for idx, ts in enumerate(timestamps)
            }

            for future in as_completed(futures):
                idx, ts = futures[future]
                try:
                    result = future.result()
                    if result:
                        created_files.append(result)
                        self.logger.debug(f"Extracted frame {idx + 1}/{len(timestamps)}")
                except Exception as e:
                    self.logger.error(f"Error extracting frame at {ts}s: {e}")

        self.logger.info(f"Extracted {len(created_files)}/{len(timestamps)} stills")
        return created_files

    def batch_compress_to_jpeg(
        self,
        png_files: list,
        output_dir: str,
        quality: int = 90,
        max_width: Optional[int] = None,
        max_workers: int = 4,
        metadata: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Compress multiple PNGs to JPEG in parallel

        Args:
            png_files: List of PNG file paths
            output_dir: Output directory
            quality: JPEG quality
            max_width: Maximum width
            max_workers: Maximum parallel workers
            metadata: Metadata to embed

        Returns:
            List of created JPEG paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        def compress_file(png_path):
            """Compress single PNG"""
            png_file = Path(png_path)
            jpeg_filename = png_file.stem + '.jpg'
            jpeg_path = output_path / jpeg_filename

            if self.compress_png_to_jpeg(
                input_path=png_path,
                output_path=str(jpeg_path),
                quality=quality,
                max_width=max_width,
                metadata=metadata
            ):
                return str(jpeg_path)
            return None

        # Compress in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(compress_file, png): png for png in png_files}

            for future in as_completed(futures):
                png = futures[future]
                try:
                    result = future.result()
                    if result:
                        created_files.append(result)
                        self.logger.debug(f"Compressed: {Path(png).name}")
                except Exception as e:
                    self.logger.error(f"Error compressing {png}: {e}")

        self.logger.info(f"Compressed {len(created_files)}/{len(png_files)} images")
        return created_files

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get image information

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image info
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'size_bytes': Path(image_path).stat().st_size
                }
        except Exception as e:
            self.logger.error(f"Error getting image info: {e}")
            return {}
