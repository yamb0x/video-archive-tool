"""Preset Editor Window for creating and editing compression presets"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable
import logging
import time


class PresetEditorWindow:
    """Editor window for creating and editing compression presets"""

    def __init__(self, parent, mode='new', preset: Optional[Dict[str, Any]] = None, on_save: Optional[Callable] = None):
        """
        Initialize preset editor window

        Args:
            parent: Parent window
            mode: 'new' or 'edit'
            preset: Preset dictionary (for edit mode)
            on_save: Callback function when preset is saved
        """
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.mode = mode
        self.on_save = on_save

        # Initialize preset data
        if preset:
            self.preset_data = preset.copy()
        else:
            self.preset_data = self._get_default_preset()

        # Create window
        self.window = tk.Toplevel(parent)
        title = "Edit Preset" if mode == 'edit' else "Create New Preset"
        self.window.title(f"Preset Editor - {title}")
        self.window.geometry("800x700")
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        self._center_window(800, 700)

        # Build UI
        self._build_ui()

        # Load preset data into UI
        self._load_preset_data()

    def _center_window(self, width: int, height: int):
        """Center window on screen"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _get_default_preset(self) -> Dict[str, Any]:
        """Get default preset template"""
        timestamp = int(time.time())
        return {
            "id": f"custom_preset_{timestamp}",
            "name": "New Preset",
            "description": "Custom compression preset",
            "editable": True,
            "settings": {
                "stills_hq": {
                    "enabled": True,
                    "format": "PNG",
                    "resolution": "source",
                    "color_space": "source"
                },
                "stills_web": {
                    "enabled": True,
                    "format": "JPEG",
                    "quality": 90,
                    "resolution": "source",
                    "progressive": True,
                    "optimize": True,
                    "color_space": "source",
                    "subsample": "4:2:0"
                },
                "video": {
                    "enabled": True,
                    "codec": "h264",
                    "resolution": "source",
                    "crf": 20,
                    "preset": "slow",
                    "profile": "high",
                    "level": "4.1",
                    "pixel_format": "yuv420p",
                    "fps": "source",
                    "two_pass": False
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": "320k",
                    "sample_rate": 48000,
                    "channels": "stereo"
                },
                "thumbnails": {
                    "enabled": False,
                    "format": "JPEG",
                    "quality": 75,
                    "max_width": 400
                }
            }
        }

    def _build_ui(self):
        """Build preset editor UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Preset info
        info_section = ttk.LabelFrame(main_frame, text="Preset Information", padding="10")
        info_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_section.columnconfigure(1, weight=1)

        # Name
        ttk.Label(info_section, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.name_var = tk.StringVar(value=self.preset_data.get('name', 'New Preset'))
        ttk.Entry(info_section, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Description
        ttk.Label(info_section, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.description_var = tk.StringVar(value=self.preset_data.get('description', ''))
        ttk.Entry(info_section, textvariable=self.description_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # ID (readonly for edit mode)
        ttk.Label(info_section, text="ID:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.id_label = ttk.Label(info_section, text=self.preset_data.get('id', ''), foreground='gray')
        self.id_label.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Settings tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Create tabs
        self._create_stills_hq_tab()
        self._create_stills_web_tab()
        self._create_video_tab()
        self._create_audio_tab()
        self._create_thumbnails_tab()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=0, sticky=tk.E, padx=5)
        ttk.Button(button_frame, text="Save Preset", command=self._save_preset, style='Accent.TButton').grid(row=0, column=1, sticky=tk.E)

    def _create_stills_hq_tab(self):
        """Create Stills HQ settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Stills HQ")

        # Enabled checkbox
        self.stills_hq_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="Enable HQ Still Export",
            variable=self.stills_hq_enabled_var
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        settings_frame = ttk.LabelFrame(tab, text="HQ Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)

        # Format (fixed to PNG)
        ttk.Label(settings_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(settings_frame, text="PNG (Lossless)", foreground='gray').grid(row=0, column=1, sticky=tk.W, pady=5)

        # Resolution
        ttk.Label(settings_frame, text="Resolution:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_hq_resolution_var = tk.StringVar(value="source")
        resolution_frame = ttk.Frame(settings_frame)
        resolution_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(resolution_frame, text="Source", variable=self.stills_hq_resolution_var, value="source").grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        ttk.Radiobutton(resolution_frame, text="Custom", variable=self.stills_hq_resolution_var, value="custom").grid(row=0, column=1, sticky=tk.W)

        # Color Space
        ttk.Label(settings_frame, text="Color Space:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_hq_color_var = tk.StringVar(value="source")
        color_combo = ttk.Combobox(settings_frame, textvariable=self.stills_hq_color_var, width=20, state='readonly')
        color_combo['values'] = ('source', 'sRGB', 'Adobe RGB')
        color_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

    def _create_stills_web_tab(self):
        """Create Stills Web (JPEG) settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Stills Web")

        # Enabled checkbox
        self.stills_web_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="Enable Web JPEG Export",
            variable=self.stills_web_enabled_var
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        settings_frame = ttk.LabelFrame(tab, text="JPEG Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        settings_frame.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        # Quality slider
        ttk.Label(settings_frame, text="Quality (1-100):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_web_quality_var = tk.IntVar(value=90)
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        quality_frame.columnconfigure(0, weight=1)

        quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.stills_web_quality_var,
            command=lambda val: self.stills_web_quality_var.set(int(float(val)))
        )
        quality_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        quality_label = ttk.Label(quality_frame, textvariable=self.stills_web_quality_var, width=5)
        quality_label.grid(row=0, column=1)

        # Max Width
        ttk.Label(settings_frame, text="Max Width:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_web_max_width_var = tk.StringVar(value="source")
        width_combo = ttk.Combobox(settings_frame, textvariable=self.stills_web_max_width_var, width=20, state='readonly')
        width_combo['values'] = ('source', '1920', '2560', '3840', 'custom')
        width_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Progressive
        self.stills_web_progressive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Progressive JPEG",
            variable=self.stills_web_progressive_var
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Optimize
        self.stills_web_optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Optimize Encoding",
            variable=self.stills_web_optimize_var
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Color Space
        ttk.Label(settings_frame, text="Color Space:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_web_color_var = tk.StringVar(value="source")
        web_color_combo = ttk.Combobox(settings_frame, textvariable=self.stills_web_color_var, width=20, state='readonly')
        web_color_combo['values'] = ('source', 'sRGB')
        web_color_combo.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Chroma Subsampling
        ttk.Label(settings_frame, text="Chroma Subsampling:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.stills_web_subsample_var = tk.StringVar(value="4:2:0")
        subsample_combo = ttk.Combobox(settings_frame, textvariable=self.stills_web_subsample_var, width=20, state='readonly')
        subsample_combo['values'] = ('4:4:4', '4:2:2', '4:2:0')
        subsample_combo.grid(row=5, column=1, sticky=tk.W, pady=5)

    def _create_video_tab(self):
        """Create Video Encoding settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="⭐ Video Encoding")

        # Enabled checkbox
        self.video_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="Enable Video Clip Export",
            variable=self.video_enabled_var
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        settings_frame = ttk.LabelFrame(tab, text="Encoding Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        settings_frame.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        row = 0

        # Codec (fixed for Phase 2)
        ttk.Label(settings_frame, text="Codec:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(settings_frame, text="H.264 (x264/NVENC)", foreground='gray').grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Resolution
        ttk.Label(settings_frame, text="Resolution:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_resolution_var = tk.StringVar(value="source")
        res_combo = ttk.Combobox(settings_frame, textvariable=self.video_resolution_var, width=20, state='readonly')
        res_combo['values'] = ('source', '1080p', '1440p', '4K', 'custom')
        res_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # CRF slider with quality indicators
        ttk.Label(settings_frame, text="CRF (Quality):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_crf_var = tk.IntVar(value=20)
        crf_frame = ttk.Frame(settings_frame)
        crf_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        crf_frame.columnconfigure(0, weight=1)
        row += 1

        crf_scale = ttk.Scale(
            crf_frame,
            from_=0,
            to=51,
            orient=tk.HORIZONTAL,
            variable=self.video_crf_var,
            command=lambda val: self._update_crf_quality_label()
        )
        crf_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.crf_value_label = ttk.Label(crf_frame, text="20", width=5)
        self.crf_value_label.grid(row=0, column=1)

        # Quality indicator
        self.crf_quality_label = ttk.Label(settings_frame, text="", foreground='green')
        self.crf_quality_label.grid(row=row, column=1, sticky=tk.W, pady=(0, 5))
        row += 1

        ttk.Label(
            settings_frame,
            text="Lower CRF = Higher Quality (0-17: Lossless, 18-23: High, 24-28: Medium, 29+: Low)",
            font=('Arial', 8),
            foreground='gray'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1

        # Preset
        ttk.Label(settings_frame, text="Encoding Preset:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_preset_var = tk.StringVar(value="slow")
        preset_combo = ttk.Combobox(settings_frame, textvariable=self.video_preset_var, width=20, state='readonly')
        preset_combo['values'] = ('ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow')
        preset_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Profile
        ttk.Label(settings_frame, text="Profile:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_profile_var = tk.StringVar(value="high")
        profile_combo = ttk.Combobox(settings_frame, textvariable=self.video_profile_var, width=20, state='readonly')
        profile_combo['values'] = ('baseline', 'main', 'high')
        profile_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Level
        ttk.Label(settings_frame, text="Level:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_level_var = tk.StringVar(value="4.1")
        level_combo = ttk.Combobox(settings_frame, textvariable=self.video_level_var, width=20, state='readonly')
        level_combo['values'] = ('3.0', '3.1', '4.0', '4.1', '5.0', '5.1')
        level_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Pixel Format
        ttk.Label(settings_frame, text="Pixel Format:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_pix_fmt_var = tk.StringVar(value="yuv420p")
        pix_fmt_combo = ttk.Combobox(settings_frame, textvariable=self.video_pix_fmt_var, width=20, state='readonly')
        pix_fmt_combo['values'] = ('yuv420p', 'yuv422p', 'yuv444p')
        pix_fmt_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # FPS
        ttk.Label(settings_frame, text="FPS:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.video_fps_var = tk.StringVar(value="source")
        fps_combo = ttk.Combobox(settings_frame, textvariable=self.video_fps_var, width=20, state='readonly')
        fps_combo['values'] = ('source', '24', '25', '30', '50', '60', 'custom')
        fps_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Two-pass encoding
        self.video_two_pass_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="Two-Pass Encoding (slower, better quality)",
            variable=self.video_two_pass_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Initialize quality label
        self._update_crf_quality_label()

    def _create_audio_tab(self):
        """Create Audio settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Audio")

        settings_frame = ttk.LabelFrame(tab, text="Audio Settings", padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)

        # Codec (fixed for Phase 2)
        ttk.Label(settings_frame, text="Codec:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(settings_frame, text="AAC", foreground='gray').grid(row=0, column=1, sticky=tk.W, pady=5)

        # Bitrate
        ttk.Label(settings_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.audio_bitrate_var = tk.StringVar(value="320k")
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.audio_bitrate_var, width=20, state='readonly')
        bitrate_combo['values'] = ('128k', '192k', '256k', '320k', 'custom')
        bitrate_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Sample Rate
        ttk.Label(settings_frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.audio_sample_rate_var = tk.IntVar(value=48000)
        sample_combo = ttk.Combobox(settings_frame, textvariable=self.audio_sample_rate_var, width=20, state='readonly')
        sample_combo['values'] = (44100, 48000, 96000)
        sample_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Channels
        ttk.Label(settings_frame, text="Channels:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.audio_channels_var = tk.StringVar(value="stereo")
        channels_combo = ttk.Combobox(settings_frame, textvariable=self.audio_channels_var, width=20, state='readonly')
        channels_combo['values'] = ('mono', 'stereo', 'source')
        channels_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

    def _create_thumbnails_tab(self):
        """Create Thumbnails settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Thumbnails")

        # Enabled checkbox
        self.thumbnails_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tab,
            text="Enable Thumbnail Generation",
            variable=self.thumbnails_enabled_var
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        settings_frame = ttk.LabelFrame(tab, text="Thumbnail Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)

        # Format
        ttk.Label(settings_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.thumbnail_format_var = tk.StringVar(value="JPEG")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.thumbnail_format_var, width=20, state='readonly')
        format_combo['values'] = ('JPEG', 'PNG')
        format_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Quality
        ttk.Label(settings_frame, text="Quality (1-100):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.thumbnail_quality_var = tk.IntVar(value=75)
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        quality_frame.columnconfigure(0, weight=1)

        thumb_quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.thumbnail_quality_var,
            command=lambda val: self.thumbnail_quality_var.set(int(float(val)))
        )
        thumb_quality_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        thumb_quality_label = ttk.Label(quality_frame, textvariable=self.thumbnail_quality_var, width=5)
        thumb_quality_label.grid(row=0, column=1)

        # Max Width
        ttk.Label(settings_frame, text="Max Width:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.thumbnail_max_width_var = tk.StringVar(value="400")
        thumb_width_combo = ttk.Combobox(settings_frame, textvariable=self.thumbnail_max_width_var, width=20, state='readonly')
        thumb_width_combo['values'] = ('400', '800', '1200', 'custom')
        thumb_width_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

    def _update_crf_quality_label(self):
        """Update CRF quality indicator label"""
        crf = self.video_crf_var.get()
        self.crf_value_label.config(text=str(crf))

        if crf <= 17:
            quality_text = "Lossless / Near-Lossless"
            color = "blue"
        elif crf <= 23:
            quality_text = "High Quality"
            color = "green"
        elif crf <= 28:
            quality_text = "Medium Quality"
            color = "orange"
        else:
            quality_text = "Low Quality / Small File"
            color = "red"

        self.crf_quality_label.config(text=f"→ {quality_text}", foreground=color)

    def _load_preset_data(self):
        """Load preset data into UI controls"""
        settings = self.preset_data.get('settings', {})

        # Load stills HQ settings
        stills_hq = settings.get('stills_hq', {})
        self.stills_hq_enabled_var.set(stills_hq.get('enabled', True))
        self.stills_hq_resolution_var.set(stills_hq.get('resolution', 'source'))
        self.stills_hq_color_var.set(stills_hq.get('color_space', 'source'))

        # Load stills web settings
        stills_web = settings.get('stills_web', {})
        self.stills_web_enabled_var.set(stills_web.get('enabled', True))
        self.stills_web_quality_var.set(stills_web.get('quality', 90))
        self.stills_web_max_width_var.set(str(stills_web.get('max_width', 'source')))
        self.stills_web_progressive_var.set(stills_web.get('progressive', True))
        self.stills_web_optimize_var.set(stills_web.get('optimize', True))
        self.stills_web_color_var.set(stills_web.get('color_space', 'source'))
        self.stills_web_subsample_var.set(stills_web.get('subsample', '4:2:0'))

        # Load video settings
        video = settings.get('video', {})
        self.video_enabled_var.set(video.get('enabled', True))
        self.video_resolution_var.set(video.get('resolution', 'source'))
        self.video_crf_var.set(video.get('crf', 20))
        self.video_preset_var.set(video.get('preset', 'slow'))
        self.video_profile_var.set(video.get('profile', 'high'))
        self.video_level_var.set(video.get('level', '4.1'))
        self.video_pix_fmt_var.set(video.get('pixel_format', 'yuv420p'))
        self.video_fps_var.set(video.get('fps', 'source'))
        self.video_two_pass_var.set(video.get('two_pass', False))

        # Load audio settings
        audio = settings.get('audio', {})
        self.audio_bitrate_var.set(audio.get('bitrate', '320k'))
        self.audio_sample_rate_var.set(audio.get('sample_rate', 48000))
        self.audio_channels_var.set(audio.get('channels', 'stereo'))

        # Load thumbnail settings
        thumbnails = settings.get('thumbnails', {})
        self.thumbnails_enabled_var.set(thumbnails.get('enabled', False))
        self.thumbnail_format_var.set(thumbnails.get('format', 'JPEG'))
        self.thumbnail_quality_var.set(thumbnails.get('quality', 75))
        self.thumbnail_max_width_var.set(str(thumbnails.get('max_width', '400')))

        # Update CRF quality label
        self._update_crf_quality_label()

    def _validate_preset(self) -> bool:
        """Validate preset data before saving"""
        # Check name is not empty
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Preset name cannot be empty")
            return False

        # Check at least one output type is enabled
        if not (self.stills_hq_enabled_var.get() or
                self.stills_web_enabled_var.get() or
                self.video_enabled_var.get() or
                self.thumbnails_enabled_var.get()):
            messagebox.showerror("Validation Error", "At least one output type must be enabled")
            return False

        return True

    def _build_preset_dict(self) -> Dict[str, Any]:
        """Build preset dictionary from UI controls"""
        # Convert max_width values
        stills_web_max_width = self.stills_web_max_width_var.get()
        if stills_web_max_width == 'source':
            stills_web_max_width_val = 'source'
        elif stills_web_max_width != 'custom':
            stills_web_max_width_val = int(stills_web_max_width)
        else:
            stills_web_max_width_val = 1920  # Default for custom

        thumbnail_max_width = self.thumbnail_max_width_var.get()
        if thumbnail_max_width != 'custom':
            thumbnail_max_width_val = int(thumbnail_max_width)
        else:
            thumbnail_max_width_val = 400  # Default for custom

        preset = {
            "id": self.preset_data.get('id'),
            "name": self.name_var.get().strip(),
            "description": self.description_var.get().strip(),
            "editable": True,  # Custom presets are always editable
            "settings": {
                "stills_hq": {
                    "enabled": self.stills_hq_enabled_var.get(),
                    "format": "PNG",
                    "resolution": self.stills_hq_resolution_var.get(),
                    "color_space": self.stills_hq_color_var.get()
                },
                "stills_web": {
                    "enabled": self.stills_web_enabled_var.get(),
                    "format": "JPEG",
                    "quality": self.stills_web_quality_var.get(),
                    "resolution": "source",
                    "max_width": stills_web_max_width_val,
                    "progressive": self.stills_web_progressive_var.get(),
                    "optimize": self.stills_web_optimize_var.get(),
                    "color_space": self.stills_web_color_var.get(),
                    "subsample": self.stills_web_subsample_var.get()
                },
                "video": {
                    "enabled": self.video_enabled_var.get(),
                    "codec": "h264",
                    "resolution": self.video_resolution_var.get(),
                    "crf": self.video_crf_var.get(),
                    "preset": self.video_preset_var.get(),
                    "profile": self.video_profile_var.get(),
                    "level": self.video_level_var.get(),
                    "pixel_format": self.video_pix_fmt_var.get(),
                    "fps": self.video_fps_var.get(),
                    "two_pass": self.video_two_pass_var.get()
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": self.audio_bitrate_var.get(),
                    "sample_rate": self.audio_sample_rate_var.get(),
                    "channels": self.audio_channels_var.get()
                },
                "thumbnails": {
                    "enabled": self.thumbnails_enabled_var.get(),
                    "format": self.thumbnail_format_var.get(),
                    "quality": self.thumbnail_quality_var.get(),
                    "max_width": thumbnail_max_width_val
                }
            }
        }

        return preset

    def _save_preset(self):
        """Validate and save preset"""
        if not self._validate_preset():
            return

        # Build preset dictionary
        preset = self._build_preset_dict()

        # Call save callback if provided
        if self.on_save:
            self.on_save(preset)

        # Close window
        self.window.destroy()

    def _cancel(self):
        """Cancel and close window"""
        result = messagebox.askyesno(
            "Cancel",
            "Are you sure you want to cancel? Any changes will be lost."
        )
        if result:
            self.window.destroy()
