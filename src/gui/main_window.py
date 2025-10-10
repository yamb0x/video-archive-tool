"""Main application window"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import json
import logging
from typing import Dict, Any, Optional


class MainWindow:
    """Main application window for Video Archive Tool"""

    def __init__(self, config_manager, processor_callback):
        """
        Initialize main window

        Args:
            config_manager: Configuration manager instance
            processor_callback: Callback function to start processing
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        self.processor_callback = processor_callback

        # Create main window
        self.root = tk.Tk()
        self.root.title("Video Archive Tool - Yambo Studio")
        self.root.geometry("800x850")  # Increased height to prevent content cropping

        # Center window on screen
        self._center_window(self.root, 800, 850)

        # Variables
        self.artwork_name_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime("%y-%m-%d"))
        self.master_path_var = tk.StringVar()
        self.rd_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.preset_var = tk.StringVar()
        self.encoder_var = tk.StringVar(value="x264")
        self.use_gpu_var = tk.BooleanVar(value=True)

        # Advanced settings
        self.scene_threshold_var = tk.DoubleVar(value=30.0)
        self.min_scene_length_var = tk.IntVar(value=15)
        self.auto_open_var = tk.BooleanVar(value=True)
        self.generate_log_var = tk.BooleanVar(value=True)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.validation_status_var = tk.StringVar(value="")

        # Build UI
        self._build_ui()

        # Load settings
        self._load_settings()

    def _build_ui(self):
        """Build user interface"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Settings button (top-right corner)
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=0, column=0, sticky=tk.E, pady=(0, 10))

        settings_btn = ttk.Button(
            settings_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            width=12
        )
        settings_btn.grid(row=0, column=0)

        row = 1

        # === PROJECT SETUP ===
        project_label = ttk.Label(main_frame, text="PROJECT SETUP", font=('Arial', 10, 'bold'))
        project_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1

        project_frame = ttk.LabelFrame(main_frame, padding="10")
        project_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        project_frame.columnconfigure(1, weight=1)
        row += 1

        # Artwork Name
        ttk.Label(project_frame, text="Artwork Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        artwork_entry = ttk.Entry(project_frame, textvariable=self.artwork_name_var, width=40)
        artwork_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Date
        ttk.Label(project_frame, text="Date (YY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        date_entry = ttk.Entry(project_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # === INPUT FILES ===
        input_label = ttk.Label(main_frame, text="INPUT FILES", font=('Arial', 10, 'bold'))
        input_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        input_frame = ttk.LabelFrame(main_frame, padding="10")
        input_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        row += 1

        # Master Video
        ttk.Label(input_frame, text="Master Video:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        master_entry = ttk.Entry(input_frame, textvariable=self.master_path_var)
        master_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_master).grid(row=0, column=2, pady=5)

        # Validation status
        self.validation_label = ttk.Label(input_frame, textvariable=self.validation_status_var, foreground="green")
        self.validation_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))

        # R&D Folder
        ttk.Label(input_frame, text="R&D Folder (optional):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        rd_entry = ttk.Entry(input_frame, textvariable=self.rd_path_var)
        rd_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_rd).grid(row=2, column=2, pady=5)

        # Output Folder
        ttk.Label(input_frame, text="Output Root:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        output_entry = ttk.Entry(input_frame, textvariable=self.output_path_var)
        output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_output).grid(row=3, column=2, pady=5)

        # === PRESET SELECTION ===
        preset_label = ttk.Label(main_frame, text="COMPRESSION PRESET", font=('Arial', 10, 'bold'))
        preset_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        preset_frame = ttk.LabelFrame(main_frame, padding="10")
        preset_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        preset_frame.columnconfigure(0, weight=1)
        row += 1

        # Preset dropdown
        presets = self._load_presets()
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, values=presets, state="readonly")
        self.preset_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        if presets:
            self.preset_combo.current(0)

        # === ENCODING OPTIONS ===
        encoding_label = ttk.Label(main_frame, text="ENCODING OPTIONS", font=('Arial', 10, 'bold'))
        encoding_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        encoding_frame = ttk.LabelFrame(main_frame, padding="10")
        encoding_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1

        # Encoder selection
        ttk.Radiobutton(encoding_frame, text="x264 (CPU - Higher Quality)", variable=self.encoder_var, value="x264").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(encoding_frame, text="NVENC (GPU - Faster)", variable=self.encoder_var, value="nvenc").grid(row=1, column=0, sticky=tk.W, pady=2)

        # === ADVANCED SETTINGS (Collapsible) ===
        self.advanced_expanded = tk.BooleanVar(value=False)
        advanced_toggle = ttk.Button(main_frame, text="▶ Advanced Settings", command=self._toggle_advanced)
        advanced_toggle.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        self.advanced_frame = ttk.LabelFrame(main_frame, padding="10")
        row += 1

        # Scene Detection
        ttk.Label(self.advanced_frame, text="Scene Detection Threshold:").grid(row=0, column=0, sticky=tk.W)
        threshold_scale = ttk.Scale(self.advanced_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.scene_threshold_var)
        threshold_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        threshold_label = ttk.Label(self.advanced_frame, textvariable=self.scene_threshold_var)
        threshold_label.grid(row=0, column=2)

        ttk.Label(self.advanced_frame, text="Min Scene Length (frames):").grid(row=1, column=0, sticky=tk.W, pady=5)
        min_scene_spin = ttk.Spinbox(self.advanced_frame, from_=1, to=120, textvariable=self.min_scene_length_var, width=10)
        min_scene_spin.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # Output Options
        ttk.Label(self.advanced_frame, text="Output Options:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Checkbutton(self.advanced_frame, text="Auto-open output folder on completion", variable=self.auto_open_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(self.advanced_frame, text="Generate process log", variable=self.generate_log_var).grid(row=4, column=0, columnspan=2, sticky=tk.W)

        self.advanced_frame.columnconfigure(1, weight=1)

        # === PROCESS BUTTON ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=20)
        button_frame.columnconfigure(0, weight=1)
        row += 1

        self.process_btn = ttk.Button(button_frame, text="PROCESS", command=self._start_processing, style='Accent.TButton')
        self.process_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), ipady=10)

        # === STATUS BAR ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        status_frame.columnconfigure(1, weight=1)
        row += 1

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=0, column=1, sticky=tk.W)

    def _center_window(self, window, width: int, height: int):
        """
        Center window on screen

        Args:
            window: The window to center
            width: Window width
            height: Window height
        """
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set position
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _load_presets(self) -> list:
        """Load available presets"""
        try:
            # Use ConfigManager to get presets
            presets = self.config.get_all_presets()
            return [p['name'] for p in presets]
        except Exception as e:
            self.logger.error(f"Error loading presets: {e}")

        return ["Webflow Standard", "Retina/Web Showcase", "Ultra-Light Web"]

    def _refresh_presets(self):
        """Refresh preset dropdown with latest presets"""
        try:
            presets = self._load_presets()

            # Find the preset combobox and update its values
            if hasattr(self, 'preset_combo'):
                current_value = self.preset_var.get()
                self.preset_combo['values'] = presets

                # Restore selection if it still exists, otherwise select first
                if current_value in presets:
                    self.preset_var.set(current_value)
                elif presets:
                    self.preset_var.set(presets[0])

            self.logger.info(f"Preset list refreshed: {len(presets)} presets available")
        except Exception as e:
            self.logger.error(f"Error refreshing presets: {e}")

    def _load_settings(self):
        """Load saved settings"""
        try:
            # Load last used paths from config
            paths = self.config.get('paths', {})
            self.output_path_var.set(paths.get('last_output_dir', ''))

            # Load defaults
            defaults = self.config.get('defaults', {})
            self.preset_var.set(defaults.get('preset', 'Webflow Standard'))

            encoding = defaults.get('encoding', {})
            self.encoder_var.set(encoding.get('encoder_preference', 'x264'))

            scene_detection = defaults.get('scene_detection', {})
            self.scene_threshold_var.set(scene_detection.get('threshold', 30.0))
            self.min_scene_length_var.set(scene_detection.get('min_scene_length', 15))

            behavior = self.config.get('behavior', {})
            self.auto_open_var.set(behavior.get('auto_open_output', True))
            self.generate_log_var.set(behavior.get('generate_log', True))

        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")

    def _toggle_advanced(self):
        """Toggle advanced settings panel"""
        if self.advanced_expanded.get():
            self.advanced_frame.grid_remove()
            self.advanced_expanded.set(False)
        else:
            self.advanced_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            self.advanced_expanded.set(True)

    def _browse_master(self):
        """Browse for master video file"""
        filename = filedialog.askopenfilename(
            title="Select ProRes Master Video",
            filetypes=[
                ("Video files", "*.mov *.mp4 *.avi"),
                ("All files", "*.*")
            ]
        )

        if filename:
            self.master_path_var.set(filename)
            self._validate_master()

    def _browse_rd(self):
        """Browse for R&D folder"""
        folder = filedialog.askdirectory(title="Select R&D Folder")
        if folder:
            self.rd_path_var.set(folder)

    def _browse_output(self):
        """Browse for output root folder"""
        folder = filedialog.askdirectory(title="Select Output Root Folder")
        if folder:
            self.output_path_var.set(folder)

    def _validate_master(self):
        """Validate selected master video"""
        master_path = self.master_path_var.get()
        if not master_path or not Path(master_path).exists():
            self.validation_status_var.set("")
            return

        try:
            from core.ffmpeg_wrapper import FFmpegWrapper

            ffmpeg = FFmpegWrapper()
            if ffmpeg.validate_prores(master_path):
                info = ffmpeg.get_video_info(master_path)
                status = f"✓ ProRes {info.get('profile', '')} - {info.get('width')}x{info.get('height')} @ {info.get('fps', 0):.2f} fps"
                self.validation_status_var.set(status)
                self.validation_label.config(foreground="green")
            else:
                self.validation_status_var.set("✗ Not a valid ProRes file")
                self.validation_label.config(foreground="red")

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            self.validation_status_var.set(f"✗ Validation failed: {str(e)}")
            self.validation_label.config(foreground="red")

    def _open_settings(self):
        """Open settings window"""
        from gui.settings_window import SettingsWindow

        def on_settings_saved():
            """Callback when settings are saved"""
            self.logger.info("Settings saved, reloading configuration")
            self._load_settings()  # Reload settings in main window
            self._refresh_presets()  # Refresh preset dropdown to show any new/edited presets

        SettingsWindow(self.root, self.config, on_save=on_settings_saved)

    def _start_processing(self):
        """Start processing with validation"""

        # Validate inputs
        if not self.artwork_name_var.get().strip():
            messagebox.showerror("Error", "Please enter an artwork name")
            return

        if not self.master_path_var.get() or not Path(self.master_path_var.get()).exists():
            messagebox.showerror("Error", "Please select a valid master video file")
            return

        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select an output folder")
            return

        # Gather parameters
        params = {
            'artwork_name': self.artwork_name_var.get().strip(),
            'project_date': self.date_var.get(),
            'master_path': self.master_path_var.get(),
            'rd_path': self.rd_path_var.get() if self.rd_path_var.get() else None,
            'output_root': self.output_path_var.get(),
            'preset': self.preset_var.get(),
            'encoder': self.encoder_var.get(),
            'use_gpu': self.use_gpu_var.get(),
            'scene_threshold': self.scene_threshold_var.get(),
            'min_scene_length': self.min_scene_length_var.get(),
            'auto_open_output': self.auto_open_var.get(),
            'generate_log': self.generate_log_var.get()
        }

        # Call processor callback
        if self.processor_callback:
            self.process_btn.config(state='disabled')
            self.status_var.set("Processing...")
            self.processor_callback(params)

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

    def close(self):
        """Close the window"""
        self.root.destroy()
