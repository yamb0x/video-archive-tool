"""
Video Archive Tool - Main Entry Point (Phase 2)
Yambo Studio - With Scene Detection and Full Processing
"""

import sys
import logging
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from utils.config_manager import ConfigManager
from core.ffmpeg_wrapper import FFmpegWrapper
from core.video_processor import VideoProcessor
from database.state_manager import StateManager
from gui.main_window import MainWindow
from gui.scene_selection_window import SceneSelectionWindow
from processors import SceneDetector, ImageProcessor, VideoClipGenerator


class VideoArchiveApp:
    """Main application controller with Phase 2 features"""

    def __init__(self):
        """Initialize application"""
        # Setup logging
        self.logger = setup_logging(log_level="INFO")
        self.logger.info("Initializing Video Archive Tool (Phase 2)...")

        # Load configuration
        self.config = ConfigManager()

        # Initialize components
        self.ffmpeg = None
        self.processor = None
        self.state_manager = None
        self.scene_detector = None
        self.image_processor = None
        self.clip_generator = None
        self.gui = None

        # Processing state
        self.current_params = None
        self.current_folders = None
        self.current_info = None
        self.all_detected_scenes = None  # Store ALL scenes for stills extraction

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

            # Initialize Phase 2 processors
            self.logger.info("Initializing Phase 2 processors...")
            self.scene_detector = SceneDetector(self.ffmpeg)
            self.image_processor = ImageProcessor()
            self.clip_generator = VideoClipGenerator(self.ffmpeg)

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
        Process video with Phase 2 workflow

        Args:
            params: Processing parameters from GUI
        """
        try:
            self.logger.info("="*60)
            self.logger.info("STARTING VIDEO PROCESSING (PHASE 2)")
            self.logger.info("="*60)

            self.current_params = params

            artwork_name = params['artwork_name']
            project_date = params['project_date']
            master_path = params['master_path']
            output_root = params['output_root']

            self.logger.info(f"Artwork: {artwork_name}")
            self.logger.info(f"Date: {project_date}")
            self.logger.info(f"Master: {master_path}")
            self.logger.info(f"Output: {output_root}")

            # === PHASE 1: Validation & Setup ===
            self.logger.info("\n--- PHASE 1: Validation & Setup ---")
            is_valid, message, info = self.processor.validate_master_video(master_path)

            if not is_valid:
                self.logger.error(f"Validation failed: {message}")
                self._show_error("Validation Error", message)
                return

            self.current_info = info
            self.logger.info(f"[OK] {message}")

            # Create output structure
            folders = self.processor.create_output_structure(
                artwork_name=artwork_name,
                project_date=project_date,
                output_root=output_root
            )
            self.current_folders = folders

            self.logger.info(f"[OK] Output structure: {folders['root']}")

            # Create database session
            session_id = self.state_manager.create_session(
                artwork_name=artwork_name,
                project_date=project_date,
                master_path=master_path,
                output_path=str(folders['root']),
                preset_id=params['preset'],
                total_operations=9,  # Phase 2 operations (copy, optimize, scenes, thumbnails, select, stills, jpeg, clips, finalize)
                rd_folder_path=params.get('rd_path'),
                encoder_type=params['encoder'],
                scene_threshold=params['scene_threshold'],
                min_scene_length=params['min_scene_length']
            )

            self.logger.info(f"[OK] Session: {session_id}")
            self.state_manager.update_status('processing')

            # Copy master
            self.logger.info("\n[1/9] Copying master...")
            if self.processor.copy_master_to_output(master_path, folders):
                self.state_manager.update_progress("copy_master")
                self.logger.info("[OK] Master copied")
            else:
                raise RuntimeError("Failed to copy master")

            # Create optimized master MP4
            self.logger.info("\n[2/9] Creating optimized master MP4...")
            optimized_master = folders['masters'] / f"{artwork_name}_master.mp4"
            use_gpu = params['encoder'] == 'nvenc'

            if self.processor.optimize_master_video(
                input_path=master_path,
                output_path=str(optimized_master),
                use_gpu=use_gpu,
                crf=18,  # Higher quality for master
                preset='slow'
            ):
                self.state_manager.update_progress("optimize_master")
                master_size = optimized_master.stat().st_size / (1024*1024)
                self.logger.info(f"[OK] Optimized master created: {master_size:.1f} MB")
            else:
                self.logger.warning("Optimized master creation failed, continuing...")

            # === PHASE 2: Scene Detection ===
            self.logger.info("\n--- PHASE 2: Scene Detection ---")
            self.logger.info("[3/9] Detecting scenes...")

            scenes = self.scene_detector.detect_scenes(
                video_path=master_path,
                threshold=params['scene_threshold'],
                min_scene_len=params['min_scene_length']
            )

            if not scenes:
                self.logger.warning("No scenes detected, using single scene")
                # Create single scene for entire video
                from processors import Scene
                scenes = [Scene(
                    scene_number=1,
                    start_frame=0,
                    end_frame=int(info['fps'] * info['duration']),
                    start_time=0.0,
                    end_time=info['duration'],
                    duration=info['duration']
                )]

            self.logger.info(f"[OK] Detected {len(scenes)} scenes")

            # Generate thumbnails
            self.logger.info("[4/9] Generating thumbnails...")
            thumbnail_dir = folders['root'] / "temp_thumbnails"
            scenes = self.scene_detector.generate_thumbnails(
                video_path=master_path,
                scenes=scenes,
                output_dir=str(thumbnail_dir),
                artwork_name=artwork_name
            )

            self.state_manager.update_progress("scene_detection", {
                "scenes_detected": len(scenes),
                "scenes_data": json.dumps(self.scene_detector.export_scene_data(scenes))
            })

            self.logger.info(f"[OK] Thumbnails generated")

            # Store ALL detected scenes for stills extraction later
            self.all_detected_scenes = scenes

            # Show scene selection UI (runs in GUI thread)
            self.logger.info("\n[5/9] Awaiting scene selection...")
            self._show_scene_selection(scenes)

        except Exception as e:
            self.logger.error(f"Processing error: {e}", exc_info=True)
            if self.state_manager.session_id:
                self.state_manager.update_status('failed', str(e))
            self._show_error("Processing Error", f"An error occurred:\n\n{str(e)}")
            self._reset_gui()

    def _show_scene_selection(self, scenes):
        """Show scene selection window"""
        def on_scenes_selected(selected_scenes, grouped_scenes):
            """Handle scene selection completion"""
            if selected_scenes is None:
                # Cancelled
                self.logger.info("Scene selection cancelled")
                self._reset_gui()
                return

            # Continue processing with selected scenes
            self._continue_processing(selected_scenes, grouped_scenes)

        # Create and show scene selection window
        SceneSelectionWindow(
            parent=self.gui.root,
            scenes=scenes,
            on_complete=on_scenes_selected
        )

    def _continue_processing(self, selected_scenes, grouped_scenes):
        """Continue processing after scene selection"""
        try:
            params = self.current_params
            folders = self.current_folders
            info = self.current_info
            artwork_name = params['artwork_name']
            master_path = params['master_path']

            self.logger.info(f"\n[OK] {len(selected_scenes)} individual scenes, {len(grouped_scenes)} groups selected")

            # Get aspect ratio
            aspect_ratio = self.processor.detect_aspect_ratio(
                info['width'], info['height']
            )

            # Prepare metadata
            metadata = {
                'Copyright': self.config.get('copyright', '© Yambo Studio'),
                'Creator': 'Yambo Studio Video Archive Tool',
                'Software': 'Video Archive Tool v1.0',
                'Description': f"Artwork: {artwork_name}",
                'Custom': {
                    'artwork_name': artwork_name,
                    'project_date': params['project_date'],
                    'source_file': Path(master_path).name
                }
            }

            # === PHASE 2: Generate Video Clips (FIRST - from selected scenes only) ===
            self.logger.info("\n--- PHASE 2: Generating Video Clips ---")
            self.logger.info("[6/9] Creating video clips from selected scenes...")

            # Get preset settings for video encoding
            preset_id = params.get('preset', 'Webflow Standard')
            preset = self.config.get_preset(preset_id)
            use_gpu = params['encoder'] == 'nvenc'
            preset_settings = preset.get('settings', {}).get('video', {}) if preset else {}
            crf = preset_settings.get('crf', 20)
            preset_name = preset_settings.get('preset', 'slow')

            # Generate individual scene clips
            clip_files = []
            if selected_scenes:
                self.logger.info(f"Creating {len(selected_scenes)} individual clips...")
                individual_clips = self.clip_generator.generate_clips_from_scenes(
                    input_video=master_path,
                    output_dir=str(folders['video_clips']),
                    artwork_name=artwork_name,
                    scenes=selected_scenes,
                    use_gpu=use_gpu,
                    crf=crf,
                    preset=preset_name
                )
                clip_files.extend(individual_clips)

            # Generate grouped scene clips
            if grouped_scenes:
                self.logger.info(f"Creating {len(grouped_scenes)} grouped clips...")
                for group_idx, group in enumerate(grouped_scenes, start=1):
                    group_filename = f"{artwork_name}_group_{group_idx:02d}.mp4"
                    group_path = folders['video_clips'] / group_filename

                    success = self.clip_generator.concatenate_scenes(
                        input_video=master_path,
                        output_path=str(group_path),
                        scenes=group,
                        use_gpu=use_gpu,
                        crf=crf,
                        preset=preset_name
                    )

                    if success:
                        clip_files.append(str(group_path))

            self.logger.info(f"[OK] Created {len(clip_files)} video clips ({len(selected_scenes)} individual + {len(grouped_scenes)} groups)")
            self.state_manager.update_progress("generate_clips")

            # === PHASE 2: Extract Stills (SECOND - from ALL detected scenes) ===
            self.logger.info("\n--- PHASE 2: Extracting Stills from ALL Scenes ---")
            self.logger.info("[7/9] Extracting high-quality PNG stills from ALL detected scenes...")

            # Use ALL detected scenes (stored before selection window)
            all_scenes = self.all_detected_scenes

            # Get midpoint timestamps for ALL scenes
            timestamps = [
                scene.start_time + (scene.duration / 2)
                for scene in all_scenes
            ]

            self.logger.info(f"Extracting stills from {len(all_scenes)} total scenes (regardless of selection)...")

            # Extract HQ PNGs
            hq_files = self.image_processor.batch_extract_stills(
                video_path=master_path,
                timestamps=timestamps,
                output_dir=str(folders['stills_hq']),
                artwork_name=artwork_name,
                file_type="HQ",
                ffmpeg_wrapper=self.ffmpeg,
                aspect_ratio=aspect_ratio,
                metadata=metadata
            )

            self.logger.info(f"[OK] Extracted {len(hq_files)} HQ stills from ALL scenes")
            self.state_manager.update_progress("extract_stills_hq")

            # === PHASE 2: Compress to JPEG ===
            self.logger.info("[8/9] Compressing to web-optimized JPEG...")

            # Get preset for JPEG quality
            jpeg_quality = 90
            if preset:
                web_settings = preset.get('settings', {}).get('stills_web', {})
                jpeg_quality = web_settings.get('quality', 90)

            jpeg_files = self.image_processor.batch_compress_to_jpeg(
                png_files=hq_files,
                output_dir=str(folders['stills_compressed']),
                quality=jpeg_quality,
                metadata=metadata
            )

            self.logger.info(f"[OK] Created {len(jpeg_files)} JPEG stills")
            self.state_manager.update_progress("compress_stills")

            # === COMPLETE ===
            self.logger.info("[9/9] Finalizing...")
            self.state_manager.update_status('completed')

            # Cleanup temp thumbnails
            import shutil
            thumbnail_dir = folders['root'] / "temp_thumbnails"
            if thumbnail_dir.exists():
                shutil.rmtree(thumbnail_dir)

            self.logger.info("\n" + "="*60)
            self.logger.info("PHASE 2 PROCESSING COMPLETE")
            self.logger.info("="*60)
            self.logger.info(f"Output: {folders['root']}")
            self.logger.info(f"Total scenes detected: {len(all_scenes)}")
            self.logger.info(f"Scenes selected for clips: {len(selected_scenes)} individual + {len(grouped_scenes)} groups")
            self.logger.info(f"Stills created from ALL scenes: {len(hq_files)} PNG, {len(jpeg_files)} JPEG")
            self.logger.info(f"Video clips created: {len(clip_files)}")

            # Show success
            summary_parts = [
                f"• {len(all_scenes)} total scenes detected",
                f"• {len(hq_files)} high-quality PNG stills (from ALL scenes)",
                f"• {len(jpeg_files)} web-optimized JPEG stills (from ALL scenes)",
                f"• {len(clip_files)} video clips created (from {len(selected_scenes)} individual + {len(grouped_scenes)} groups)",
                f"• Metadata embedded in all files"
            ]

            self._show_success(
                "Processing Complete!",
                f"Phase 2 processing completed successfully!\n\n"
                f"Output: {folders['root']}\n\n"
                f"Created:\n" + "\n".join(summary_parts)
            )

            # Auto-open folder
            if params.get('auto_open_output', True):
                import os
                import subprocess
                import platform

                if platform.system() == 'Windows':
                    os.startfile(folders['root'])
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folders['root']])
                else:
                    subprocess.run(['xdg-open', folders['root']])

        except Exception as e:
            self.logger.error(f"Processing error: {e}", exc_info=True)
            if self.state_manager.session_id:
                self.state_manager.update_status('failed', str(e))
            self._show_error("Processing Error", f"An error occurred:\n\n{str(e)}")

        finally:
            self._reset_gui()

    def _reset_gui(self):
        """Reset GUI to ready state"""
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
