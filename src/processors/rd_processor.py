"""R&D folder recursive processing for mixed media assets"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image


class RDProcessor:
    """Process R&D folder with mixed stills and videos recursively"""

    # Supported file extensions
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp'}
    VIDEO_EXTENSIONS = {'.mov', '.mp4', '.avi', '.mkv', '.mts', '.m2ts', '.prores'}

    def __init__(self, ffmpeg_wrapper, image_processor):
        """
        Initialize R&D processor

        Args:
            ffmpeg_wrapper: FFmpeg wrapper instance
            image_processor: Image processor instance
        """
        self.logger = logging.getLogger(__name__)
        self.ffmpeg = ffmpeg_wrapper
        self.image_proc = image_processor

    def scan_rd_folder(self, rd_input_path: str) -> Tuple[List[Path], List[Path]]:
        """
        Recursively scan R&D folder for media files

        Args:
            rd_input_path: Path to R&D input folder

        Returns:
            Tuple of (image_files, video_files)
        """
        rd_path = Path(rd_input_path)

        if not rd_path.exists():
            self.logger.warning(f"R&D input path does not exist: {rd_input_path}")
            return [], []

        image_files = []
        video_files = []

        # Recursively find all media files
        for item in rd_path.rglob('*'):
            if item.is_file():
                ext = item.suffix.lower()
                if ext in self.IMAGE_EXTENSIONS:
                    image_files.append(item)
                elif ext in self.VIDEO_EXTENSIONS:
                    video_files.append(item)

        self.logger.info(f"Found {len(image_files)} images and {len(video_files)} videos in R&D folder")
        return image_files, video_files

    def process_rd_images(
        self,
        image_files: List[Path],
        highres_dir: Path,
        compressed_dir: Path,
        artwork_name: str,
        quality: int = 90,
        max_width: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_workers: int = 4
    ) -> Tuple[int, int]:
        """
        Process R&D images to HQ and compressed versions

        Args:
            image_files: List of image file paths
            highres_dir: High-res output directory
            compressed_dir: Compressed output directory
            artwork_name: Artwork name for filenames
            quality: JPEG quality for compressed
            max_width: Max width for compressed (None = source)
            metadata: Metadata to embed
            max_workers: Parallel workers

        Returns:
            Tuple of (hq_count, compressed_count)
        """
        if not image_files:
            return 0, 0

        highres_dir.mkdir(parents=True, exist_ok=True)
        compressed_dir.mkdir(parents=True, exist_ok=True)

        hq_created = 0
        compressed_created = 0

        def process_image(idx: int, img_path: Path) -> Tuple[bool, bool]:
            """Process single image to HQ PNG and compressed JPEG"""
            try:
                sequence = idx + 1

                # Detect aspect ratio
                with Image.open(img_path) as img:
                    width, height = img.size
                    aspect = self._detect_aspect_ratio(width, height)

                # HQ PNG filename
                hq_filename = f"{artwork_name}_RD_HQ_{sequence:02d}_{aspect}.png"
                hq_path = highres_dir / hq_filename

                # Compressed JPEG filename
                comp_filename = f"{artwork_name}_RD_compressed_{sequence:02d}_{aspect}.jpg"
                comp_path = compressed_dir / comp_filename

                # Copy/convert to HQ PNG
                hq_success = self._create_hq_png(img_path, hq_path, metadata)

                # Create compressed JPEG
                comp_success = self.image_proc.compress_png_to_jpeg(
                    input_path=str(img_path),
                    output_path=str(comp_path),
                    quality=quality,
                    max_width=max_width,
                    progressive=True,
                    optimize=True,
                    metadata=metadata
                )

                return hq_success, comp_success

            except Exception as e:
                self.logger.error(f"Error processing R&D image {img_path.name}: {e}")
                return False, False

        # Process images in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_image, idx, img_path): (idx, img_path)
                for idx, img_path in enumerate(image_files)
            }

            for future in as_completed(futures):
                idx, img_path = futures[future]
                try:
                    hq_success, comp_success = future.result()
                    if hq_success:
                        hq_created += 1
                    if comp_success:
                        compressed_created += 1
                    self.logger.debug(f"Processed R&D image {idx + 1}/{len(image_files)}: {img_path.name}")
                except Exception as e:
                    self.logger.error(f"Error processing R&D image {img_path.name}: {e}")

        self.logger.info(f"R&D Images: {hq_created} HQ, {compressed_created} compressed")
        return hq_created, compressed_created

    def process_rd_videos(
        self,
        video_files: List[Path],
        clips_dir: Path,
        artwork_name: str,
        use_gpu: bool = True,
        crf_hq: int = 17,
        crf_compressed: int = 23,
        preset: str = "slow",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, int]:
        """
        Process R&D videos to HQ and compressed versions in Clips subfolder

        Args:
            video_files: List of video file paths
            clips_dir: Clips output directory (R&D/Clips)
            artwork_name: Artwork name for filenames
            use_gpu: Use GPU encoding
            crf_hq: CRF for high-quality version
            crf_compressed: CRF for compressed version
            preset: Encoding preset
            metadata: Metadata to embed

        Returns:
            Tuple of (hq_count, compressed_count)
        """
        if not video_files:
            return 0, 0

        # Create Clips subfolder with HQ and Compressed subdirectories
        clips_hq_dir = clips_dir / "HQ"
        clips_compressed_dir = clips_dir / "Compressed"

        clips_hq_dir.mkdir(parents=True, exist_ok=True)
        clips_compressed_dir.mkdir(parents=True, exist_ok=True)

        hq_created = 0
        compressed_created = 0

        for idx, vid_path in enumerate(video_files):
            try:
                sequence = idx + 1

                # Get video info for aspect ratio
                info = self.ffmpeg.get_video_info(str(vid_path))
                width = info.get('width', 0)
                height = info.get('height', 0)
                aspect = self._detect_aspect_ratio(width, height)

                # HQ H.264 filename (in Clips/HQ)
                hq_filename = f"{artwork_name}_RD_HQ_{sequence:02d}_{aspect}.mp4"
                hq_path = clips_hq_dir / hq_filename

                # Compressed H.264 filename (in Clips/Compressed)
                comp_filename = f"{artwork_name}_RD_compressed_{sequence:02d}_{aspect}.mp4"
                comp_path = clips_compressed_dir / comp_filename

                # Encode HQ version
                hq_success = self._encode_video(
                    str(vid_path), str(hq_path),
                    use_gpu=use_gpu, crf=crf_hq, preset=preset
                )
                if hq_success:
                    hq_created += 1

                # Encode compressed version
                comp_success = self._encode_video(
                    str(vid_path), str(comp_path),
                    use_gpu=use_gpu, crf=crf_compressed, preset="faster"
                )
                if comp_success:
                    compressed_created += 1

                self.logger.info(f"Processed R&D video {idx + 1}/{len(video_files)}: {vid_path.name}")

            except Exception as e:
                self.logger.error(f"Error processing R&D video {vid_path.name}: {e}")

        self.logger.info(f"R&D Videos: {hq_created} HQ, {compressed_created} compressed")
        return hq_created, compressed_created

    def _create_hq_png(self, input_path: Path, output_path: Path, metadata: Optional[Dict[str, Any]]) -> bool:
        """
        Create HQ PNG from input image

        Args:
            input_path: Input image path
            output_path: Output PNG path
            metadata: Metadata to embed

        Returns:
            True if successful
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed (preserve quality)
                if img.mode in ('RGBA', 'LA'):
                    # Preserve alpha channel for PNG
                    img.save(output_path, 'PNG', optimize=False)
                elif img.mode == 'P':
                    img = img.convert('RGB')
                    img.save(output_path, 'PNG', optimize=False)
                else:
                    img.save(output_path, 'PNG', optimize=False)

            # Add metadata
            if metadata:
                self.image_proc.save_png_with_metadata(str(output_path), metadata)

            output_size = output_path.stat().st_size
            self.logger.debug(f"HQ PNG created: {output_size / (1024*1024):.1f} MB")
            return True

        except Exception as e:
            self.logger.error(f"Error creating HQ PNG: {e}")
            return False

    def _encode_video(
        self,
        input_path: str,
        output_path: str,
        use_gpu: bool,
        crf: int,
        preset: str
    ) -> bool:
        """
        Encode video with specified quality

        Args:
            input_path: Input video path
            output_path: Output video path
            use_gpu: Use GPU encoding
            crf: Quality setting
            preset: Encoding preset

        Returns:
            True if successful
        """
        try:
            cmd = self.ffmpeg.build_encode_command(
                input_path=input_path,
                output_path=output_path,
                use_gpu=use_gpu,
                crf=crf,
                preset=preset
            )

            result = self.ffmpeg.run_command(cmd, timeout=3600)

            if result.returncode == 0:
                output_size = Path(output_path).stat().st_size
                self.logger.debug(f"Video encoded: {output_size / (1024*1024):.1f} MB")
                return True
            else:
                self.logger.error(f"Video encoding failed: {output_path}")
                return False

        except Exception as e:
            self.logger.error(f"Error encoding video: {e}")
            return False

    def _detect_aspect_ratio(self, width: int, height: int) -> str:
        """
        Detect aspect ratio and return suffix

        Args:
            width: Image/video width
            height: Image/video height

        Returns:
            Aspect ratio suffix (e.g., "16x9", "9x16", "1x1")
        """
        if width == 0 or height == 0:
            return "unknown"

        ratio = width / height
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
            return f"{width}x{height}"

    def process_rd_folder(
        self,
        rd_input_path: str,
        rd_root_dir: str,
        artwork_name: str,
        image_quality: int = 90,
        image_max_width: Optional[int] = None,
        video_crf_hq: int = 17,
        video_crf_compressed: int = 23,
        use_gpu: bool = True,
        preset: str = "slow",
        metadata: Optional[Dict[str, Any]] = None,
        max_workers: int = 4
    ) -> Dict[str, int]:
        """
        Complete R&D folder processing pipeline

        Args:
            rd_input_path: R&D input folder path
            rd_root_dir: R&D root output directory
            artwork_name: Artwork name for filenames
            image_quality: JPEG quality for compressed images
            image_max_width: Max width for compressed images
            video_crf_hq: CRF for HQ videos
            video_crf_compressed: CRF for compressed videos
            use_gpu: Use GPU encoding for videos
            preset: Video encoding preset
            metadata: Metadata to embed
            max_workers: Parallel workers for images

        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Processing R&D folder: {rd_input_path}")

        # Scan for media files
        image_files, video_files = self.scan_rd_folder(rd_input_path)

        stats = {
            'images_found': len(image_files),
            'videos_found': len(video_files),
            'images_hq': 0,
            'images_compressed': 0,
            'videos_hq': 0,
            'videos_compressed': 0
        }

        rd_root = Path(rd_root_dir)

        # Process images (in High-res and Compressed folders)
        if image_files:
            img_hq, img_comp = self.process_rd_images(
                image_files=image_files,
                highres_dir=rd_root / "High-res",
                compressed_dir=rd_root / "Compressed",
                artwork_name=artwork_name,
                quality=image_quality,
                max_width=image_max_width,
                metadata=metadata,
                max_workers=max_workers
            )
            stats['images_hq'] = img_hq
            stats['images_compressed'] = img_comp

        # Process videos (in Clips/HQ and Clips/Compressed folders)
        if video_files:
            vid_hq, vid_comp = self.process_rd_videos(
                video_files=video_files,
                clips_dir=rd_root / "Clips",
                artwork_name=artwork_name,
                use_gpu=use_gpu,
                crf_hq=video_crf_hq,
                crf_compressed=video_crf_compressed,
                preset=preset,
                metadata=metadata
            )
            stats['videos_hq'] = vid_hq
            stats['videos_compressed'] = vid_comp

        self.logger.info(
            f"R&D Processing Complete: "
            f"{stats['images_hq']} HQ images, {stats['images_compressed']} compressed images, "
            f"{stats['videos_hq']} HQ videos, {stats['videos_compressed']} compressed videos"
        )

        return stats
