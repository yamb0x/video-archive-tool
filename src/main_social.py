"""
Social Media Prep Tool - Main Entry Point
Yambo Studio - Social Media Asset Preparation
"""

import sys
import logging
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from utils.config_manager import ConfigManager
from core.ffmpeg_wrapper import FFmpegWrapper
from core.template_manager import TemplateManager
from processors.template_compositor import TemplateCompositor
from processors.batch_processor import BatchProcessor
from gui.main_window_social import MainWindow


class SocialMediaPrepApp:
    """Main application controller for Social Media Prep Tool"""

    def __init__(self):
        """Initialize application"""
        # Setup logging
        self.logger = setup_logging(log_level="INFO")
        self.logger.info("=" * 80)
        self.logger.info("Social Media Prep Tool - Starting...")
        self.logger.info("=" * 80)

        # Load configuration
        self.config = ConfigManager()

        # Initialize FFmpeg
        try:
            self.ffmpeg = FFmpegWrapper()
            self.logger.info(f"FFmpeg initialized: {self.ffmpeg.get_encoder_type()} encoder")
        except Exception as e:
            self.logger.error(f"Failed to initialize FFmpeg: {e}")
            self.ffmpeg = None

        # Initialize template manager
        templates_dir = self._get_templates_dir()
        self.template_manager = TemplateManager(templates_dir)
        self.logger.info(f"Templates directory: {templates_dir}")

        # Initialize processors
        self.compositor = TemplateCompositor(self.template_manager, self.ffmpeg)
        self.batch_processor = BatchProcessor(self.compositor)

        # Initialize GUI
        self.gui = None

    def _get_templates_dir(self) -> str:
        """Get templates directory path"""
        # Check if templates directory exists relative to main script
        app_root = Path(__file__).parent.parent
        templates_dir = app_root / "tamplates"

        if templates_dir.exists():
            return str(templates_dir)

        # Fallback to creating templates directory
        templates_dir.mkdir(exist_ok=True)
        self.logger.warning(f"Templates directory not found, created: {templates_dir}")

        return str(templates_dir)

    def process_files(self, params: dict):
        """
        Process media files

        Args:
            params: Dictionary with processing parameters
                - project_name: str
                - media_files: List[MediaFile]
                - output_dir: str
                - preset: dict
                - use_gpu: bool
        """
        try:
            self.logger.info("Starting batch processing...")
            self.logger.info(f"Project: {params['project_name']}")
            self.logger.info(f"Output: {params['output_dir']}")

            # Update GPU usage in preset if needed
            preset = params['preset'].copy()
            if params['use_gpu'] and self.ffmpeg and self.ffmpeg.nvenc_available:
                # Ensure GPU codec is used
                if 'settings' in preset and 'video' in preset['settings']:
                    preset['settings']['video']['codec'] = 'h264_nvenc'
            else:
                # Force CPU encoding
                if 'settings' in preset and 'video' in preset['settings']:
                    preset['settings']['video']['codec'] = 'h264'

            # Progress callback
            def progress_callback(current, total, filename, status):
                if self.gui:
                    self.gui.update_progress(current, total, filename, status)

            # Process files
            result = self.batch_processor.process_all(
                media_files=params['media_files'],
                project_name=params['project_name'],
                preset=preset,
                output_dir=params['output_dir'],
                progress_callback=progress_callback,
                parallel_images=True,
                max_workers=4
            )

            # Show results
            if result['success']:
                self.logger.info("=" * 80)
                self.logger.info("PROCESSING COMPLETE")
                self.logger.info("=" * 80)
                self.logger.info(f"Processed: {result['processed']} files")
                self.logger.info(f"Failed: {result['failed']} files")
                self.logger.info(f"Output directory: {result['output_directory']}")

                if self.gui:
                    from tkinter import messagebox
                    messagebox.showinfo(
                        "Processing Complete",
                        f"Successfully processed {result['processed']} files!\n\n"
                        f"Output: {result['output_directory']}"
                    )
            else:
                self.logger.error("Processing failed or was cancelled")

                if self.gui:
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Processing Failed",
                        f"Processing failed.\n\n"
                        f"Processed: {result['processed']}\n"
                        f"Failed: {result['failed']}\n\n"
                        f"Check process_log.txt for details."
                    )

        except Exception as e:
            self.logger.error(f"Error during processing: {e}", exc_info=True)

            if self.gui:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Processing error: {str(e)}")

        finally:
            # Reset progress
            if self.gui:
                self.gui.progress_var.set(0)
                self.gui.status_var.set("Ready")

    def run(self):
        """Run application"""
        try:
            # Create and run GUI
            self.gui = MainWindow(
                config_manager=self.config,
                template_manager=self.template_manager,
                process_callback=self.process_files
            )

            self.logger.info("Launching GUI...")
            self.gui.run()

        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            raise

        finally:
            self.logger.info("Social Media Prep Tool - Shutting down")


def main():
    """Main entry point"""
    try:
        app = SocialMediaPrepApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
