"""
Main Window - Social Media Prep Tool
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
from typing import List, Optional, Callable
from pathlib import Path

from core.media_scanner import MediaScanner
from core.template_manager import TemplateManager
from models.media_file import MediaFile


class MainWindow:
    """Main application window for Social Media Prep Tool"""

    def __init__(
        self,
        config_manager,
        template_manager: TemplateManager,
        process_callback: Callable
    ):
        """
        Initialize main window

        Args:
            config_manager: Configuration manager instance
            template_manager: Template manager instance
            process_callback: Callback to start processing
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        self.template_manager = template_manager
        self.process_callback = process_callback

        self.media_scanner = MediaScanner()
        self.media_files: List[MediaFile] = []
        self.selected_index = None

        # Create main window
        self.root = tk.Tk()
        self.root.title("Social Media Prep Tool - Yambo Studio")
        self.root.geometry("900x700")

        # Center window
        self._center_window()

        # Variables
        self.project_name_var = tk.StringVar()
        self.input_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.preset_var = tk.StringVar()
        self.use_gpu_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.IntVar(value=0)

        # Build UI
        self._build_ui()

        # Load presets
        self._load_presets()

    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = 900
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _build_ui(self):
        """Build user interface"""

        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # File list should expand

        row = 0

        # === TITLE ===
        title_label = ttk.Label(
            main_frame,
            text="Social Media Prep Tool",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=row, column=0, pady=(0, 15))
        row += 1

        # === PROJECT NAME ===
        project_frame = ttk.Frame(main_frame)
        project_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        project_frame.columnconfigure(1, weight=1)
        row += 1

        ttk.Label(project_frame, text="📝 Project Name:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        project_entry = ttk.Entry(project_frame, textvariable=self.project_name_var, font=('Arial', 10))
        project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # === INPUT FOLDER ===
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        row += 1

        ttk.Label(input_frame, text="📁 Input Folder:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        ttk.Entry(input_frame, textvariable=self.input_folder_var, state='readonly').grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )

        ttk.Button(input_frame, text="Browse...", command=self._browse_input_folder).grid(
            row=0, column=2
        )

        # === FILE LIST ===
        list_frame = ttk.LabelFrame(main_frame, text="Files (drag to reorder)", padding="10")
        list_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        row += 1

        # Create treeview with scrollbar
        tree_scroll_frame = ttk.Frame(list_frame)
        tree_scroll_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_frame.columnconfigure(0, weight=1)
        tree_scroll_frame.rowconfigure(0, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Treeview
        columns = ('seq', 'filename', 'info', 'template')
        self.file_tree = ttk.Treeview(
            tree_scroll_frame,
            columns=columns,
            show='tree headings',
            selectmode='browse',
            yscrollcommand=scrollbar.set
        )
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar.config(command=self.file_tree.yview)

        # Configure columns
        self.file_tree.column('#0', width=50, minwidth=50, stretch=False)  # Checkbox
        self.file_tree.column('seq', width=50, minwidth=50, stretch=False)
        self.file_tree.column('filename', width=250, minwidth=150, stretch=True)
        self.file_tree.column('info', width=200, minwidth=150, stretch=True)
        self.file_tree.column('template', width=150, minwidth=100, stretch=False)

        # Headings
        self.file_tree.heading('#0', text='☑')
        self.file_tree.heading('seq', text='#')
        self.file_tree.heading('filename', text='Filename')
        self.file_tree.heading('info', text='Info')
        self.file_tree.heading('template', text='Template')

        # Bind events
        self.file_tree.bind('<Double-Button-1>', self._on_tree_double_click)
        self.file_tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        # File list buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(button_frame, text="↑ Move Up", command=self._move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="↓ Move Down", command=self._move_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Auto-Template", command=self._auto_assign_templates).pack(side=tk.LEFT)

        # === COMPRESSION SETTINGS ===
        settings_label = ttk.Label(main_frame, text="━━━ Compression Settings ━━━", font=('Arial', 9))
        settings_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 10))
        row += 1

        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        row += 1

        # Preset
        ttk.Label(settings_frame, text="Preset:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.preset_combo = ttk.Combobox(settings_frame, textvariable=self.preset_var, state='readonly', width=30)
        self.preset_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))

        # Encoding
        ttk.Label(settings_frame, text="Encoding:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))

        encoding_frame = ttk.Frame(settings_frame)
        encoding_frame.grid(row=1, column=1, sticky=tk.W)

        ttk.Radiobutton(
            encoding_frame,
            text="CPU (x264)",
            variable=self.use_gpu_var,
            value=False
        ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Radiobutton(
            encoding_frame,
            text="GPU (NVENC)",
            variable=self.use_gpu_var,
            value=True
        ).pack(side=tk.LEFT)

        # === OUTPUT PATH ===
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)
        row += 1

        ttk.Label(output_frame, text="📂 Output:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        ttk.Entry(output_frame, textvariable=self.output_folder_var, state='readonly').grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )

        ttk.Button(output_frame, text="Browse...", command=self._browse_output_folder).grid(
            row=0, column=2
        )

        # === PROGRESS BAR ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        row += 1

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # === BOTTOM BUTTONS ===
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Button(
            bottom_frame,
            text="Settings",
            command=self._open_settings,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.process_button = ttk.Button(
            bottom_frame,
            text="Process Files",
            command=self._start_processing,
            width=20
        )
        self.process_button.pack(side=tk.RIGHT)

        # === STATUS BAR ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        row += 1

        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _load_presets(self):
        """Load available presets from config"""
        try:
            presets = self.config.get_all_presets()
            preset_names = [p.get('name', p['id']) for p in presets]
            self.preset_combo['values'] = preset_names

            if preset_names:
                self.preset_var.set(preset_names[0])

        except Exception as e:
            self.logger.error(f"Error loading presets: {e}")
            messagebox.showerror("Error", f"Failed to load presets: {e}")

    def _browse_input_folder(self):
        """Browse for input folder"""
        folder = filedialog.askdirectory(title="Select Input Folder")

        if folder:
            self.input_folder_var.set(folder)
            self._scan_folder(folder)

    def _browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")

        if folder:
            self.output_folder_var.set(folder)

    def _scan_folder(self, folder_path: str):
        """Scan folder for media files"""
        try:
            self.status_var.set("Scanning folder...")
            self.root.update()

            # Scan folder
            file_infos = self.media_scanner.scan_folder(folder_path)

            if not file_infos:
                messagebox.showinfo("No Files", "No supported media files found in folder.")
                self.status_var.set("Ready")
                return

            # Create MediaFile objects
            self.media_files = []
            for idx, file_info in enumerate(file_infos, start=1):
                media_file = MediaFile(
                    path=file_info['path'],
                    sequence=idx,
                    file_info=file_info,
                    template_manager=self.template_manager
                )
                self.media_files.append(media_file)

            # Refresh file list display
            self._refresh_file_list()

            self.status_var.set(f"Loaded {len(self.media_files)} files")

        except Exception as e:
            self.logger.error(f"Error scanning folder: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to scan folder: {e}")
            self.status_var.set("Ready")

    def _refresh_file_list(self):
        """Refresh file list treeview"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Add files
        for media_file in self.media_files:
            checkbox = "☑" if media_file.enabled else "☐"

            self.file_tree.insert(
                '',
                'end',
                text=checkbox,
                values=(
                    media_file.sequence,
                    media_file.filename,
                    media_file.get_display_info(),
                    media_file.template
                ),
                tags=(str(media_file.sequence),)
            )

    def _on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item, 'values')
            if values:
                self.selected_index = int(values[0]) - 1  # Sequence to index

    def _on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        region = self.file_tree.identify('region', event.x, event.y)

        if region == 'tree':
            # Toggle checkbox
            self._toggle_selected_file()
        elif region == 'cell':
            # Check if clicked on template column
            column = self.file_tree.identify_column(event.x)
            if column == '#4':  # Template column
                self._change_template()

    def _toggle_selected_file(self):
        """Toggle enabled state of selected file"""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.media_files):
            media_file = self.media_files[self.selected_index]
            media_file.enabled = not media_file.enabled
            self._refresh_file_list()

    def _change_template(self):
        """Change template for selected file"""
        if self.selected_index is None:
            return

        media_file = self.media_files[self.selected_index]
        templates = self.template_manager.get_template_names()
        template_names = self.template_manager.get_template_display_names()

        # Create dialog for template selection
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Template")
        dialog.transient(self.root)
        dialog.grab_set()

        # Calculate position to center on screen
        dialog_width = 450
        dialog_height = 350
        dialog.geometry(f"{dialog_width}x{dialog_height}")

        # Center on screen
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Filename label with wrapping
        ttk.Label(
            dialog,
            text=f"Template for:\n{media_file.filename}",
            wraplength=dialog_width - 40,
            justify=tk.CENTER
        ).pack(pady=15)

        # Separator
        ttk.Separator(dialog, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)

        # Template options frame with scrollbar if needed
        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        template_var = tk.StringVar(value=media_file.template)

        for template_id in templates:
            display_name = template_names[template_id]
            ttk.Radiobutton(
                options_frame,
                text=display_name,
                variable=template_var,
                value=template_id
            ).pack(anchor=tk.W, pady=8)

        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def apply_template():
            media_file.set_template(template_var.get())
            self._refresh_file_list()
            dialog.destroy()

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Apply", command=apply_template).pack(side=tk.RIGHT, padx=5)

    def _move_up(self):
        """Move selected file up in order"""
        if self.selected_index is None or self.selected_index == 0:
            return

        # Swap with previous
        idx = self.selected_index
        self.media_files[idx], self.media_files[idx - 1] = \
            self.media_files[idx - 1], self.media_files[idx]

        # Renumber sequences
        self._renumber_sequences()

        # Update selection
        self.selected_index -= 1

        # Refresh
        self._refresh_file_list()

    def _move_down(self):
        """Move selected file down in order"""
        if self.selected_index is None or self.selected_index >= len(self.media_files) - 1:
            return

        # Swap with next
        idx = self.selected_index
        self.media_files[idx], self.media_files[idx + 1] = \
            self.media_files[idx + 1], self.media_files[idx]

        # Renumber sequences
        self._renumber_sequences()

        # Update selection
        self.selected_index += 1

        # Refresh
        self._refresh_file_list()

    def _renumber_sequences(self):
        """Renumber file sequences after reordering"""
        for idx, media_file in enumerate(self.media_files, start=1):
            media_file.sequence = idx

    def _select_all(self):
        """Select all files"""
        for media_file in self.media_files:
            media_file.enabled = True
        self._refresh_file_list()

    def _deselect_all(self):
        """Deselect all files"""
        for media_file in self.media_files:
            media_file.enabled = False
        self._refresh_file_list()

    def _auto_assign_templates(self):
        """Auto-assign templates in pattern: full, 16-9, 16-9, full, 16-9, 16-9..."""
        pattern = ["full", "16-9", "16-9"]  # Repeating pattern

        for idx, media_file in enumerate(self.media_files):
            template_id = pattern[idx % len(pattern)]
            media_file.set_template(template_id)

        self._refresh_file_list()
        self.status_var.set("Auto-assigned templates in pattern: full, 16:9, 16:9...")

    def _open_settings(self):
        """Open settings window"""
        messagebox.showinfo("Settings", "Settings window coming soon!")

    def _start_processing(self):
        """Start processing files"""
        # Validate inputs
        if not self.project_name_var.get().strip():
            messagebox.showwarning("Missing Project Name", "Please enter a project name.")
            return

        if not self.media_files:
            messagebox.showwarning("No Files", "Please select an input folder with media files.")
            return

        if not self.output_folder_var.get():
            messagebox.showwarning("No Output Folder", "Please select an output folder.")
            return

        enabled_files = [f for f in self.media_files if f.enabled]
        if not enabled_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return

        # Get selected preset
        preset_name = self.preset_var.get()
        preset = self.config.get_preset_by_name(preset_name)

        if not preset:
            messagebox.showerror("Error", "Selected preset not found.")
            return

        # Prepare processing parameters
        params = {
            'project_name': self.project_name_var.get().strip(),
            'media_files': self.media_files,
            'output_dir': self.output_folder_var.get(),
            'preset': preset,
            'use_gpu': self.use_gpu_var.get()
        }

        # Call processing callback
        self.process_callback(params)

    def update_progress(self, current: int, total: int, filename: str, status: str):
        """Update progress bar and status"""
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.progress_var.set(progress_percent)
        self.status_var.set(f"{status} - {filename} ({current}/{total})")
        self.root.update()

    def run(self):
        """Run main window"""
        self.root.mainloop()
