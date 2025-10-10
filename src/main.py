"""
Video Archive Tool - Main Entry Point
Yambo Studio
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from utils.config_manager import ConfigManager
from core.ffmpeg_wrapper import FFmpegWrapper
from core.video_processor import VideoProcessor
from database.state_manager import StateManager
from gui.main_window import MainWindow


class VideoArchiveApp:
    """Main application controller"""

    def __init__(self):
        """Initialize application"""
        # Setup logging
        self.logger = setup_logging(log_level="INFO")
        self.logger.info("Initializing Video Archive Tool...")

        # Load configuration
        self.config = ConfigManager()

        # Initialize components
        self.ffmpeg = None
        self.processor = None
        self.state_manager = None
        self.gui = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialize application components"""
        try:
            # Initialize FFmpeg wrapper
            self.logger.info("Initializing FFmpeg wrapper...")
            self.ffmpeg = FFmpegWrapper()

            # Initialize video processor
            self.logger.info("Initializing video processor...")
            self.processor = VideoProcessor(self.ffmpeg)

            # Initialize state manager
            self.logger.info("Initializing state manager...")
            self.state_manager = StateManager()

            # Check for resumable session
            self._check_resume()

            # Initialize GUI
            self.logger.info("Initializing GUI...")
            self.gui = MainWindow(
                config_manager=self.config,
                processor_callback=self.process_video
            )

            self.logger.info("Application initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            raise

    def _check_resume(self):
        """Check for resumable sessions"""
        try:
            resumable = self.state_manager.get_resumable_session()
            if resumable:
                self.logger.info(f"Found resumable session: {resumable['session_id']}")
                # TODO: Implement resume dialog in Phase 4
        except Exception as e:
            self.logger.warning(f"Error checking for resumable sessions: {e}")

    def process_video(self, params: dict):
        """
        Process video with given parameters

        Args:
            params: Processing parameters from GUI
        """
        try:
            self.logger.info("="*60)
            self.logger.info("STARTING VIDEO PROCESSING")
            self.logger.info("="*60)

            artwork_name = params['artwork_name']
            project_date = params['project_date']
            master_path = params['master_path']
            output_root = params['output_root']

            self.logger.info(f"Artwork: {artwork_name}")
            self.logger.info(f"Date: {project_date}")
            self.logger.info(f"Master: {master_path}")
            self.logger.info(f"Output: {output_root}")

            # Phase 1: Validate master video
            self.logger.info("\n--- PHASE 1: Validation ---")
            is_valid, message, info = self.processor.validate_master_video(master_path)

            if not is_valid:
                self.logger.error(f"Validation failed: {message}")
                self._show_error("Validation Error", message)
                return

            self.logger.info(f"✓ {message}")

            # Phase 1: Create output structure
            self.logger.info("\n--- PHASE 1: Creating Output Structure ---")
            folders = self.processor.create_output_structure(
                artwork_name=artwork_name,
                project_date=project_date,
                output_root=output_root
            )

            self.logger.info(f"✓ Created output structure at: {folders['root']}")

            # Phase 1: Create database session
            self.logger.info("\n--- PHASE 1: Creating Session ---")
            session_id = self.state_manager.create_session(
                artwork_name=artwork_name,
                project_date=project_date,
                master_path=master_path,
                output_path=str(folders['root']),
                preset_id=params['preset'],
                total_operations=5,  # Basic operations for Phase 1
                rd_folder_path=params.get('rd_path'),
                encoder_type=params['encoder'],
                scene_threshold=params['scene_threshold'],
                min_scene_length=params['min_scene_length']
            )

            self.logger.info(f"✓ Session created: {session_id}")

            # Update status to processing
            self.state_manager.update_status('processing')

            # Phase 1 Test: Copy master to output
            self.logger.info("\n--- PHASE 1 TEST: Copying Master ---")
            if self.processor.copy_master_to_output(master_path, folders):
                self.logger.info("✓ Master copied successfully")
                self.state_manager.update_progress("copy_master", {"status": "completed"})
            else:
                raise RuntimeError("Failed to copy master")

            # Phase 1 Test: Extract test frame
            self.logger.info("\n--- PHASE 1 TEST: Extracting Test Frame ---")
            test_frame_path = folders['stills_hq'] / f"{artwork_name}_test_frame.png"

            # Get video duration and extract midpoint frame
            duration = info.get('duration', 0)
            midpoint = duration / 2

            if self.processor.extract_frame(master_path, str(test_frame_path), midpoint):
                self.logger.info(f"✓ Test frame extracted: {test_frame_path}")
                self.state_manager.update_progress("extract_test_frame", {"status": "completed"})
            else:
                self.logger.warning("Test frame extraction failed (non-critical)")

            # Mark session as completed
            self.state_manager.update_status('completed')

            self.logger.info("\n" + "="*60)
            self.logger.info("PHASE 1 PROCESSING COMPLETE")
            self.logger.info("="*60)
            self.logger.info(f"Output location: {folders['root']}")

            # Show completion message
            self._show_success(
                "Processing Complete",
                f"Phase 1 test completed successfully!\n\nOutput: {folders['root']}\n\n"
                f"Created:\n"
                f"- Output folder structure\n"
                f"- Master copy\n"
                f"- Test frame extraction\n"
                f"- Database session tracking"
            )

            # Auto-open output folder if enabled
            if params.get('auto_open_output', True):
                import os
                import subprocess
                import platform

                if platform.system() == 'Windows':
                    os.startfile(folders['root'])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', folders['root']])
                else:  # Linux
                    subprocess.run(['xdg-open', folders['root']])

        except Exception as e:
            self.logger.error(f"Processing error: {e}", exc_info=True)
            self.state_manager.update_status('failed', str(e))
            self._show_error("Processing Error", f"An error occurred:\n\n{str(e)}")

        finally:
            # Re-enable process button
            if self.gui:
                self.gui.process_btn.config(state='normal')
                self.gui.status_var.set("Ready")

    def _show_error(self, title: str, message: str):
        """Show error dialog"""
        if self.gui:
            from tkinter import messagebox
            messagebox.showerror(title, message)

    def _show_success(self, title: str, message: str):
        """Show success dialog"""
        if self.gui:
            from tkinter import messagebox
            messagebox.showinfo(title, message)

    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting GUI...")
            self.gui.run()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up resources...")

        if self.state_manager:
            self.state_manager.close()

        self.logger.info("Application shutdown complete")


def main():
    """Main entry point"""
    try:
        app = VideoArchiveApp()
        app.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
