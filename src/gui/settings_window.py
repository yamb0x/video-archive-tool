"""Settings window for application configuration"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path
import logging


class SettingsWindow:
    """Settings window with tabbed interface for app configuration"""

    def __init__(self, parent, config_manager, on_save: Optional[Callable] = None):
        """
        Initialize settings window

        Args:
            parent: Parent window
            config_manager: Configuration manager instance
            on_save: Optional callback when settings are saved
        """
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.config = config_manager
        self.on_save = on_save

        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Video Archive Tool")
        self.window.geometry("900x650")
        self.window.transient(parent)
        self.window.grab_set()

        # Center window
        self._center_window(900, 650)

        # Track changes
        self.has_changes = False
        self.temp_settings = {}
        self.temp_presets = []

        # Build UI
        self._build_ui()

        # Load current settings
        self._load_current_settings()

    def _center_window(self, width: int, height: int):
        """Center window on screen"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Build settings window UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Create tabs
        self._create_presets_tab()
        self._create_naming_tab()
        self._create_behavior_tab()
        self._create_scene_detection_tab()
        self._create_paths_tab()
        self._create_about_tab()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=0, sticky=tk.E, padx=5)
        ttk.Button(button_frame, text="Save Changes", command=self._save_changes, style='Accent.TButton').grid(row=0, column=1, sticky=tk.E)

    def _create_presets_tab(self):
        """Create compression presets management tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎬 Compression Presets")

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            tab,
            text="Manage Compression Presets",
            font=('Arial', 11, 'bold')
        )
        header_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Presets list frame
        list_frame = ttk.Frame(tab)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview for presets
        columns = ('name', 'description', 'quality', 'editable')
        self.presets_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        self.presets_tree.heading('name', text='Preset Name')
        self.presets_tree.heading('description', text='Description')
        self.presets_tree.heading('quality', text='Quality')
        self.presets_tree.heading('editable', text='Type')

        self.presets_tree.column('name', width=200)
        self.presets_tree.column('description', width=300)
        self.presets_tree.column('quality', width=100)
        self.presets_tree.column('editable', width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.presets_tree.yview)
        self.presets_tree.configure(yscrollcommand=scrollbar.set)

        self.presets_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind double-click to edit
        self.presets_tree.bind('<Double-Button-1>', self._on_preset_double_click)

        # Button frame
        preset_btn_frame = ttk.Frame(tab)
        preset_btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        ttk.Button(preset_btn_frame, text="➕ New Preset", command=self._new_preset).grid(row=0, column=0, padx=5)
        ttk.Button(preset_btn_frame, text="✏️ Edit", command=self._edit_preset).grid(row=0, column=1, padx=5)
        ttk.Button(preset_btn_frame, text="📋 Duplicate", command=self._duplicate_preset).grid(row=0, column=2, padx=5)
        ttk.Button(preset_btn_frame, text="🗑️ Delete", command=self._delete_preset).grid(row=0, column=3, padx=5)

        # Spacer
        preset_btn_frame.columnconfigure(4, weight=1)

        ttk.Button(preset_btn_frame, text="📥 Import", command=self._import_preset).grid(row=0, column=5, padx=5)
        ttk.Button(preset_btn_frame, text="💾 Export", command=self._export_preset).grid(row=0, column=6, padx=5)

    def _create_naming_tab(self):
        """Create output & naming customization tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="💾 Output & Naming")

        # Header
        header_label = ttk.Label(
            tab,
            text="Customize Output Folder Structure and File Naming",
            font=('Arial', 11, 'bold')
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        row = 1

        # Folder naming section
        folder_section = ttk.LabelFrame(tab, text="Folder Names", padding="10")
        folder_section.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_section.columnconfigure(1, weight=1)
        row += 1

        self.folder_vars = {}
        folders = [
            ('masters', 'Masters Folder:', 'Masters'),
            ('video_clips', 'Video Clips Folder:', 'Video-clips'),
            ('stills', 'Stills Folder:', 'Stills'),
            ('rd', 'R&D Folder:', 'R&D')
        ]

        for idx, (key, label, default) in enumerate(folders):
            ttk.Label(folder_section, text=label).grid(row=idx, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            var = tk.StringVar(value=default)
            self.folder_vars[key] = var
            entry = ttk.Entry(folder_section, textvariable=var, width=30)
            entry.grid(row=idx, column=1, sticky=(tk.W, tk.E), pady=5)
            # Update preview on change
            var.trace_add('write', lambda *args: self._update_naming_preview())

        # File naming section
        naming_section = ttk.LabelFrame(tab, text="File Naming Templates", padding="10")
        naming_section.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        naming_section.columnconfigure(1, weight=1)
        row += 1

        # Project folder template
        ttk.Label(naming_section, text="Project Folder:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.project_folder_var = tk.StringVar(value="{date}_{artwork}")
        project_entry = ttk.Entry(naming_section, textvariable=self.project_folder_var, width=40)
        project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.project_folder_var.trace_add('write', lambda *args: self._update_naming_preview())

        ttk.Label(naming_section, text="Available: {date}, {artwork}", foreground='gray').grid(row=1, column=1, sticky=tk.W)

        # File naming template
        ttk.Label(naming_section, text="File Names:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5), padx=(0, 10))
        self.file_naming_var = tk.StringVar(value="{artwork}_{type}_{seq}_{aspect}")
        file_entry = ttk.Entry(naming_section, textvariable=self.file_naming_var, width=40)
        file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        self.file_naming_var.trace_add('write', lambda *args: self._update_naming_preview())

        ttk.Label(naming_section, text="Available: {artwork}, {type}, {seq}, {aspect}", foreground='gray').grid(row=3, column=1, sticky=tk.W)

        # Preview section
        preview_section = ttk.LabelFrame(tab, text="Preview", padding="10")
        preview_section.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        preview_section.columnconfigure(0, weight=1)
        row += 1

        preview_text = tk.Text(preview_section, height=8, width=70, wrap=tk.WORD, state='disabled')
        preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.naming_preview = preview_text

        # Reset button
        ttk.Button(tab, text="↻ Reset to Defaults", command=self._reset_naming).grid(row=row, column=0, sticky=tk.W, pady=(10, 0))

    def _create_behavior_tab(self):
        """Create application behavior settings tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🔧 Behavior")

        # Header
        header_label = ttk.Label(
            tab,
            text="Application Behavior Settings",
            font=('Arial', 11, 'bold')
        )
        header_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        row = 1

        # Output behavior
        output_section = ttk.LabelFrame(tab, text="Output Behavior", padding="10")
        output_section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1

        self.auto_open_var = tk.BooleanVar(value=True)
        self.generate_log_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            output_section,
            text="Auto-open output folder on completion",
            variable=self.auto_open_var
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        ttk.Checkbutton(
            output_section,
            text="Generate process log file",
            variable=self.generate_log_var
        ).grid(row=1, column=0, sticky=tk.W, pady=5)

        # Encoder preferences
        encoder_section = ttk.LabelFrame(tab, text="Encoding Defaults", padding="10")
        encoder_section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1

        self.default_encoder_var = tk.StringVar(value="x264")

        ttk.Label(encoder_section, text="Default Encoder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            encoder_section,
            text="x264 (CPU - Higher Quality)",
            variable=self.default_encoder_var,
            value="x264"
        ).grid(row=1, column=0, sticky=tk.W, padx=(20, 0), pady=2)

        ttk.Radiobutton(
            encoder_section,
            text="NVENC (GPU - Faster)",
            variable=self.default_encoder_var,
            value="nvenc"
        ).grid(row=2, column=0, sticky=tk.W, padx=(20, 0), pady=2)

    def _create_scene_detection_tab(self):
        """Create scene detection defaults tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎭 Scene Detection")

        # Header
        header_label = ttk.Label(
            tab,
            text="Scene Detection Default Settings",
            font=('Arial', 11, 'bold')
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Detection settings
        detection_section = ttk.LabelFrame(tab, text="Detection Parameters", padding="10")
        detection_section.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        detection_section.columnconfigure(1, weight=1)

        # Threshold (integer only)
        ttk.Label(detection_section, text="Threshold (1-100):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.scene_threshold_var = tk.IntVar(value=30)  # Changed to IntVar
        threshold_frame = ttk.Frame(detection_section)
        threshold_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        threshold_scale = ttk.Scale(
            threshold_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.scene_threshold_var,
            command=lambda val: self.scene_threshold_var.set(int(float(val)))  # Force integer
        )
        threshold_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        threshold_frame.columnconfigure(0, weight=1)

        threshold_label = ttk.Label(threshold_frame, textvariable=self.scene_threshold_var, width=5)
        threshold_label.grid(row=0, column=1)

        # Min scene length
        ttk.Label(detection_section, text="Min Scene Length (frames):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_scene_length_var = tk.IntVar(value=15)
        ttk.Spinbox(
            detection_section,
            from_=1,
            to=120,
            textvariable=self.min_scene_length_var,
            width=10
        ).grid(row=1, column=1, sticky=tk.W, pady=5)

    def _create_paths_tab(self):
        """Create default paths tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📁 Default Paths")

        # Header
        header_label = ttk.Label(
            tab,
            text="Default Directory Paths",
            font=('Arial', 11, 'bold')
        )
        header_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        paths_section = ttk.LabelFrame(tab, text="Default Locations", padding="10")
        paths_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        paths_section.columnconfigure(1, weight=1)

        self.path_vars = {}

        # Output directory
        ttk.Label(paths_section, text="Default Output:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.path_vars['output'] = tk.StringVar()
        ttk.Entry(paths_section, textvariable=self.path_vars['output']).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))
        ttk.Button(paths_section, text="Browse", command=lambda: self._browse_path('output')).grid(row=0, column=2, pady=5)

        # R&D directory
        ttk.Label(paths_section, text="Default R&D:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.path_vars['rd'] = tk.StringVar()
        ttk.Entry(paths_section, textvariable=self.path_vars['rd']).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))
        ttk.Button(paths_section, text="Browse", command=lambda: self._browse_path('rd')).grid(row=1, column=2, pady=5)

    def _create_about_tab(self):
        """Create about tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="ℹ️ About")

        # App info
        app_name = ttk.Label(
            tab,
            text="Video Archive Tool",
            font=('Arial', 16, 'bold')
        )
        app_name.grid(row=0, column=0, pady=(20, 5))

        version_label = ttk.Label(tab, text="Version 1.0.0 - Phase 2", foreground='gray')
        version_label.grid(row=1, column=0, pady=(0, 20))

        copyright_label = ttk.Label(tab, text="© 2024 Yambo Studio", font=('Arial', 10))
        copyright_label.grid(row=2, column=0, pady=(0, 30))

        # System info
        info_frame = ttk.LabelFrame(tab, text="System Information", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # FFmpeg check
        try:
            from core.ffmpeg_wrapper import FFmpegWrapper
            ffmpeg = FFmpegWrapper()
            ffmpeg_status = "✓ Installed"
            ffmpeg_color = "green"
        except:
            ffmpeg_status = "✗ Not Found"
            ffmpeg_color = "red"

        ttk.Label(info_frame, text="FFmpeg:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(info_frame, text=ffmpeg_status, foreground=ffmpeg_color).grid(row=0, column=1, sticky=tk.W, pady=5)

        # GPU check
        ttk.Label(info_frame, text="CUDA/NVENC:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Label(info_frame, text="Detection in progress...", foreground='gray').grid(row=1, column=1, sticky=tk.W, pady=5)

    def _load_current_settings(self):
        """Load current settings from config"""
        # Load behavior settings
        self.auto_open_var.set(self.config.get('behavior.auto_open_output', True))
        self.generate_log_var.set(self.config.get('behavior.generate_log', True))
        self.default_encoder_var.set(self.config.get('defaults.encoding.encoder_preference', 'x264'))

        # Load scene detection
        self.scene_threshold_var.set(int(self.config.get('defaults.scene_detection.threshold', 30)))
        self.min_scene_length_var.set(self.config.get('defaults.scene_detection.min_scene_length', 15))

        # Load paths
        self.path_vars['output'].set(self.config.get('paths.last_output_dir', ''))
        self.path_vars['rd'].set(self.config.get('paths.last_rd_dir', ''))

        # Load naming settings
        naming = self.config.get('naming', {})
        self.project_folder_var.set(naming.get('project_folder', '{date}_{artwork}'))
        self.file_naming_var.set(naming.get('file_template', '{artwork}_{type}_{seq}_{aspect}'))

        folders = naming.get('folders', {})
        self.folder_vars['masters'].set(folders.get('masters', 'Masters'))
        self.folder_vars['video_clips'].set(folders.get('video_clips', 'Video-clips'))
        self.folder_vars['stills'].set(folders.get('stills', 'Stills'))
        self.folder_vars['rd'].set(folders.get('rd', 'R&D'))

        # Load presets
        self._load_presets()

        # Update preview
        self._update_naming_preview()

    def _load_presets(self):
        """Load presets into treeview"""
        # Clear existing
        for item in self.presets_tree.get_children():
            self.presets_tree.delete(item)

        # Load presets
        presets = self.config.get_all_presets()
        self.temp_presets = presets.copy()

        for preset in presets:
            # Determine quality indicator
            video_settings = preset.get('settings', {}).get('video', {})
            crf = video_settings.get('crf', 20)
            quality = f"CRF {crf}"

            # Editable status
            editable = "Custom" if preset.get('editable', False) else "Built-in"

            self.presets_tree.insert('', 'end', values=(
                preset.get('name', 'Unnamed'),
                preset.get('description', ''),
                quality,
                editable
            ), tags=(preset.get('id', ''),))

    def _browse_path(self, path_type: str):
        """Browse for directory path"""
        folder = filedialog.askdirectory(title=f"Select Default {path_type.title()} Directory")
        if folder:
            self.path_vars[path_type].set(folder)
            self.has_changes = True

    def _update_naming_preview(self):
        """Update naming preview"""
        self.naming_preview.config(state='normal')
        self.naming_preview.delete('1.0', tk.END)

        # Generate preview
        project = self.project_folder_var.get().replace('{date}', '25-01-15').replace('{artwork}', 'MyArtwork')
        file_ex = self.file_naming_var.get().replace('{artwork}', 'MyArtwork').replace('{type}', 'HQ').replace('{seq}', '01').replace('{aspect}', '16x9')

        masters = self.folder_vars['masters'].get()
        clips = self.folder_vars['video_clips'].get()
        stills = self.folder_vars['stills'].get()
        rd = self.folder_vars['rd'].get()

        preview = f"""Example Output Structure:

{project}/
├── {masters}/
│   └── original.mov
├── {clips}/
│   └── {file_ex}.mp4
├── {stills}/
│   ├── HQ/
│   │   └── {file_ex}.png
│   └── Compressed/
│       └── {file_ex}.jpg
└── {rd}/
    └── [R&D files]
"""

        self.naming_preview.insert('1.0', preview)
        self.naming_preview.config(state='disabled')

    def _reset_naming(self):
        """Reset naming to defaults"""
        self.project_folder_var.set('{date}_{artwork}')
        self.file_naming_var.set('{artwork}_{type}_{seq}_{aspect}')
        self.folder_vars['masters'].set('Masters')
        self.folder_vars['video_clips'].set('Video-clips')
        self.folder_vars['stills'].set('Stills')
        self.folder_vars['rd'].set('R&D')
        self._update_naming_preview()
        self.has_changes = True

    def _on_preset_double_click(self, event):
        """Handle double-click on preset"""
        self._edit_preset()

    def _new_preset(self):
        """Create new preset"""
        from gui.preset_editor_window import PresetEditorWindow

        def on_save(preset):
            """Callback when preset is saved"""
            if self.config.add_preset(preset):
                self._load_presets()  # Refresh list
                messagebox.showinfo("Success", f"Preset '{preset.get('name')}' created successfully!")
                self.has_changes = True
            else:
                messagebox.showerror("Error", "Failed to create preset")

        PresetEditorWindow(self.window, mode='new', on_save=on_save)

    def _edit_preset(self):
        """Edit selected preset"""
        selection = self.presets_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a preset to edit")
            return

        # Get preset ID from tags
        preset_id = self.presets_tree.item(selection[0])['tags'][0]
        preset = self.config.get_preset(preset_id)

        if not preset:
            messagebox.showerror("Error", "Preset not found")
            return

        # Check if editable
        if not preset.get('editable', False):
            result = messagebox.askyesno(
                "Built-in Preset",
                "Built-in presets cannot be edited.\n\nWould you like to duplicate this preset and edit the copy?"
            )
            if result:
                self._duplicate_preset()
            return

        # Open editor
        from gui.preset_editor_window import PresetEditorWindow

        def on_save(updated_preset):
            """Callback when preset is saved"""
            if self.config.update_preset(preset_id, updated_preset):
                self._load_presets()  # Refresh list
                messagebox.showinfo("Success", f"Preset '{updated_preset.get('name')}' updated successfully!")
                self.has_changes = True
            else:
                messagebox.showerror("Error", "Failed to update preset")

        PresetEditorWindow(self.window, mode='edit', preset=preset, on_save=on_save)

    def _duplicate_preset(self):
        """Duplicate selected preset"""
        selection = self.presets_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a preset to duplicate")
            return

        # Get preset ID from tags
        preset_id = self.presets_tree.item(selection[0])['tags'][0]
        preset = self.config.get_preset(preset_id)

        if not preset:
            messagebox.showerror("Error", "Preset not found")
            return

        # Create duplicate
        import time
        import copy

        duplicate = copy.deepcopy(preset)
        timestamp = int(time.time())
        duplicate['id'] = f"{preset_id}_copy_{timestamp}"
        duplicate['name'] = f"{preset.get('name', 'Preset')} (Copy)"
        duplicate['editable'] = True  # Duplicates are always editable

        # Open editor for customization
        from gui.preset_editor_window import PresetEditorWindow

        def on_save(new_preset):
            """Callback when preset is saved"""
            if self.config.add_preset(new_preset):
                self._load_presets()  # Refresh list
                messagebox.showinfo("Success", f"Preset '{new_preset.get('name')}' created successfully!")
                self.has_changes = True
            else:
                messagebox.showerror("Error", "Failed to create duplicate preset")

        PresetEditorWindow(self.window, mode='new', preset=duplicate, on_save=on_save)

    def _delete_preset(self):
        """Delete selected preset"""
        selection = self.presets_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a preset to delete")
            return

        # Get preset ID from tags
        preset_id = self.presets_tree.item(selection[0])['tags'][0]
        preset = self.config.get_preset(preset_id)

        if not preset:
            messagebox.showerror("Error", "Preset not found")
            return

        # Check if editable
        if not preset.get('editable', False):
            messagebox.showerror("Cannot Delete", "Built-in presets cannot be deleted.\n\nYou can duplicate it to create a custom version.")
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "Delete Preset",
            f"Delete preset '{preset.get('name')}'?\n\nThis action cannot be undone."
        )

        if result:
            if self.config.delete_preset(preset_id):
                self._load_presets()  # Refresh list
                messagebox.showinfo("Success", "Preset deleted successfully!")
                self.has_changes = True
            else:
                messagebox.showerror("Error", "Failed to delete preset")

    def _import_preset(self):
        """Import preset from JSON"""
        import copy
        import time

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Import Preset",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Load JSON file
            with open(file_path, 'r') as f:
                imported_preset = json.load(f)

            # Validate structure
            required_keys = ['id', 'name', 'settings']
            missing_keys = [key for key in required_keys if key not in imported_preset]

            if missing_keys:
                messagebox.showerror(
                    "Invalid Preset",
                    f"Missing required fields: {', '.join(missing_keys)}"
                )
                return

            # Check for ID conflicts
            existing_preset = self.config.get_preset(imported_preset['id'])
            if existing_preset:
                # Auto-rename with timestamp
                timestamp = int(time.time())
                old_id = imported_preset['id']
                imported_preset['id'] = f"{old_id}_imported_{timestamp}"
                imported_preset['name'] = f"{imported_preset.get('name', 'Preset')} (Imported)"

                messagebox.showinfo(
                    "ID Conflict",
                    f"A preset with ID '{old_id}' already exists.\n\nImported preset renamed to:\n{imported_preset['name']}"
                )

            # All imports are custom/editable
            imported_preset['editable'] = True

            # Add preset
            if self.config.add_preset(imported_preset):
                self._load_presets()  # Refresh list
                messagebox.showinfo("Success", f"Preset '{imported_preset.get('name')}' imported successfully!")
                self.has_changes = True
            else:
                messagebox.showerror("Error", "Failed to import preset")

        except json.JSONDecodeError:
            messagebox.showerror("Invalid JSON", "The file is not a valid JSON file")
        except Exception as e:
            self.logger.error(f"Error importing preset: {e}")
            messagebox.showerror("Error", f"Failed to import preset:\n{str(e)}")

    def _export_preset(self):
        """Export preset to JSON"""
        selection = self.presets_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a preset to export")
            return

        # Get preset ID from tags
        preset_id = self.presets_tree.item(selection[0])['tags'][0]
        preset = self.config.get_preset(preset_id)

        if not preset:
            messagebox.showerror("Error", "Preset not found")
            return

        # Open save dialog
        default_filename = f"{preset.get('name', 'preset').replace(' ', '_')}.json"
        file_path = filedialog.asksaveasfilename(
            title="Export Preset",
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(preset, f, indent=2)

            messagebox.showinfo("Success", f"Preset exported to:\n{file_path}")

        except Exception as e:
            self.logger.error(f"Error exporting preset: {e}")
            messagebox.showerror("Error", f"Failed to export preset:\n{str(e)}")

    def _save_changes(self):
        """Save all changes to config"""
        try:
            # Save behavior settings
            self.config.set('behavior.auto_open_output', self.auto_open_var.get())
            self.config.set('behavior.generate_log', self.generate_log_var.get())
            self.config.set('defaults.encoding.encoder_preference', self.default_encoder_var.get())

            # Save scene detection
            self.config.set('defaults.scene_detection.threshold', self.scene_threshold_var.get())
            self.config.set('defaults.scene_detection.min_scene_length', self.min_scene_length_var.get())

            # Save paths
            self.config.set('paths.last_output_dir', self.path_vars['output'].get())
            self.config.set('paths.last_rd_dir', self.path_vars['rd'].get())

            # Save naming settings
            naming = {
                'project_folder': self.project_folder_var.get(),
                'file_template': self.file_naming_var.get(),
                'folders': {
                    'masters': self.folder_vars['masters'].get(),
                    'video_clips': self.folder_vars['video_clips'].get(),
                    'stills': self.folder_vars['stills'].get(),
                    'rd': self.folder_vars['rd'].get()
                }
            }
            self.config.set('naming', naming)

            # Save config to file
            if self.config.save():
                messagebox.showinfo("Success", "Settings saved successfully!")

                # Call callback if provided
                if self.on_save:
                    self.on_save()

                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings")

        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")

    def _cancel(self):
        """Cancel and close window"""
        if self.has_changes:
            result = messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?"
            )
            if not result:
                return

        self.window.destroy()
