"""
Batch Processor - Orchestrates batch processing of multiple media files
"""

import os
import logging
from typing import List, Callable, Optional, Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.media_file import MediaFile
from processors.template_compositor import TemplateCompositor


class BatchProcessor:
    """Orchestrates batch processing of media files with progress tracking"""

    def __init__(self, template_compositor: TemplateCompositor):
        """
        Initialize batch processor

        Args:
            template_compositor: TemplateCompositor instance
        """
        self.compositor = template_compositor
        self.logger = logging.getLogger(__name__)
        self.cancelled = False

    def process_all(
        self,
        media_files: List[MediaFile],
        project_name: str,
        preset: dict,
        output_dir: str,
        progress_callback: Optional[Callable] = None,
        parallel_images: bool = True,
        max_workers: int = 4
    ) -> Dict[str, any]:
        """
        Process all media files in batch

        Args:
            media_files: List of MediaFile instances
            project_name: Project name for output filenames
            preset: Preset settings dictionary
            output_dir: Output directory path
            progress_callback: Optional callback(current, total, filename, status)
            parallel_images: Process images in parallel (videos always sequential)
            max_workers: Maximum parallel workers for image processing

        Returns:
            Dictionary with processing results and statistics
        """
        self.cancelled = False

        # Filter enabled files
        files_to_process = [f for f in media_files if f.enabled]

        if not files_to_process:
            return {
                'success': False,
                'error': 'No files selected for processing',
                'processed': 0,
                'failed': 0,
                'skipped': 0
            }

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Separate images and videos
        images = [f for f in files_to_process if f.type == 'image']
        videos = [f for f in files_to_process if f.type == 'video']

        total_files = len(files_to_process)
        processed_count = 0
        failed_count = 0
        skipped_count = 0

        results = {
            'processed_files': [],
            'failed_files': [],
            'skipped_files': []
        }

        self.logger.info(f"Starting batch processing: {total_files} files ({len(images)} images, {len(videos)} videos)")

        # Process images (can be parallel)
        if images:
            if parallel_images and max_workers > 1:
                # Parallel image processing
                processed, failed, skipped = self._process_images_parallel(
                    images,
                    project_name,
                    preset,
                    output_dir,
                    progress_callback,
                    processed_count,
                    total_files,
                    max_workers
                )
            else:
                # Sequential image processing
                processed, failed, skipped = self._process_images_sequential(
                    images,
                    project_name,
                    preset,
                    output_dir,
                    progress_callback,
                    processed_count,
                    total_files
                )

            processed_count += processed
            failed_count += failed
            skipped_count += skipped

        # Process videos (always sequential due to resource intensity)
        if videos and not self.cancelled:
            processed, failed, skipped = self._process_videos_sequential(
                videos,
                project_name,
                preset,
                output_dir,
                progress_callback,
                processed_count,
                total_files
            )

            processed_count += processed
            failed_count += failed
            skipped_count += skipped

        # Generate processing summary
        summary = {
            'success': not self.cancelled and failed_count == 0,
            'processed': processed_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'total': total_files,
            'cancelled': self.cancelled,
            'output_directory': output_dir,
            'project_name': project_name
        }

        # Write processing log
        self._write_processing_log(output_dir, media_files, summary)

        self.logger.info(f"Batch processing complete: {processed_count} processed, {failed_count} failed, {skipped_count} skipped")

        return summary

    def _process_images_parallel(
        self,
        images: List[MediaFile],
        project_name: str,
        preset: dict,
        output_dir: str,
        progress_callback: Optional[Callable],
        start_index: int,
        total_files: int,
        max_workers: int
    ) -> tuple:
        """Process images in parallel using ThreadPoolExecutor"""
        processed = 0
        failed = 0
        skipped = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all image processing tasks
            future_to_image = {
                executor.submit(
                    self.compositor.process_file,
                    img,
                    project_name,
                    output_dir,
                    preset
                ): img for img in images
            }

            # Process completed tasks
            for future in as_completed(future_to_image):
                if self.cancelled:
                    skipped = len(images) - processed - failed
                    break

                image = future_to_image[future]

                try:
                    success, result = future.result()

                    if success:
                        processed += 1
                        self.logger.info(f"Processed: {image.filename}")
                    else:
                        failed += 1
                        self.logger.error(f"Failed: {image.filename} - {result}")

                except Exception as e:
                    failed += 1
                    self.logger.error(f"Exception processing {image.filename}: {str(e)}")

                # Update progress
                if progress_callback:
                    current = start_index + processed + failed
                    progress_callback(current, total_files, image.filename, "Processing images...")

        return processed, failed, skipped

    def _process_images_sequential(
        self,
        images: List[MediaFile],
        project_name: str,
        preset: dict,
        output_dir: str,
        progress_callback: Optional[Callable],
        start_index: int,
        total_files: int
    ) -> tuple:
        """Process images sequentially"""
        processed = 0
        failed = 0
        skipped = 0

        for idx, image in enumerate(images):
            if self.cancelled:
                skipped = len(images) - idx
                break

            try:
                success, result = self.compositor.process_file(
                    image,
                    project_name,
                    output_dir,
                    preset
                )

                if success:
                    processed += 1
                    self.logger.info(f"Processed: {image.filename}")
                else:
                    failed += 1
                    self.logger.error(f"Failed: {image.filename} - {result}")

            except Exception as e:
                failed += 1
                self.logger.error(f"Exception processing {image.filename}: {str(e)}")

            # Update progress
            if progress_callback:
                current = start_index + idx + 1
                progress_callback(current, total_files, image.filename, "Processing images...")

        return processed, failed, skipped

    def _process_videos_sequential(
        self,
        videos: List[MediaFile],
        project_name: str,
        preset: dict,
        output_dir: str,
        progress_callback: Optional[Callable],
        start_index: int,
        total_files: int
    ) -> tuple:
        """Process videos sequentially (resource intensive)"""
        processed = 0
        failed = 0
        skipped = 0

        for idx, video in enumerate(videos):
            if self.cancelled:
                skipped = len(videos) - idx
                break

            try:
                # Create video-specific progress callback
                def video_progress(percent):
                    if progress_callback:
                        current = start_index + idx + 1
                        status = f"Encoding video ({percent}%)"
                        progress_callback(current, total_files, video.filename, status)

                success, result = self.compositor.process_file(
                    video,
                    project_name,
                    output_dir,
                    preset,
                    progress_callback=video_progress
                )

                if success:
                    processed += 1
                    self.logger.info(f"Processed: {video.filename}")
                else:
                    failed += 1
                    self.logger.error(f"Failed: {video.filename} - {result}")

            except Exception as e:
                failed += 1
                self.logger.error(f"Exception processing {video.filename}: {str(e)}")

            # Update progress
            if progress_callback:
                current = start_index + idx + 1
                progress_callback(current, total_files, video.filename, "Processing videos...")

        return processed, failed, skipped

    def _write_processing_log(
        self,
        output_dir: str,
        media_files: List[MediaFile],
        summary: dict
    ):
        """
        Write processing log to output directory

        Args:
            output_dir: Output directory path
            media_files: List of all MediaFile instances
            summary: Processing summary dictionary
        """
        try:
            log_path = os.path.join(output_dir, 'process_log.txt')

            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SOCIAL MEDIA PREP TOOL - PROCESSING LOG\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Project Name: {summary['project_name']}\n")
                f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Output Directory: {output_dir}\n\n")

                f.write("-" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Files: {summary['total']}\n")
                f.write(f"Processed: {summary['processed']}\n")
                f.write(f"Failed: {summary['failed']}\n")
                f.write(f"Skipped: {summary['skipped']}\n")
                f.write(f"Status: {'CANCELLED' if summary['cancelled'] else 'COMPLETE'}\n\n")

                f.write("-" * 80 + "\n")
                f.write("FILE DETAILS\n")
                f.write("-" * 80 + "\n\n")

                for media_file in media_files:
                    if not media_file.enabled:
                        continue

                    f.write(f"File: {media_file.filename}\n")
                    f.write(f"  Sequence: {media_file.sequence}\n")
                    f.write(f"  Template: {media_file.template}\n")
                    f.write(f"  Type: {media_file.type}\n")
                    f.write(f"  Dimensions: {media_file.width}x{media_file.height}\n")

                    if media_file.processed:
                        f.write(f"  Status: SUCCESS\n")
                        f.write(f"  Output: {os.path.basename(media_file.output_path)}\n")
                    elif media_file.error_message:
                        f.write(f"  Status: FAILED\n")
                        f.write(f"  Error: {media_file.error_message}\n")
                    else:
                        f.write(f"  Status: SKIPPED\n")

                    f.write("\n")

                f.write("=" * 80 + "\n")

            self.logger.info(f"Processing log written to: {log_path}")

        except Exception as e:
            self.logger.error(f"Failed to write processing log: {str(e)}")

    def cancel(self):
        """Cancel ongoing batch processing"""
        self.cancelled = True
        self.logger.warning("Batch processing cancellation requested")
