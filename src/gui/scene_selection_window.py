"""Scene selection window for choosing and grouping scenes"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from pathlib import Path

from PIL import Image, ImageTk


class SceneSelectionWindow:
    """Window for selecting and grouping detected scenes"""

    def __init__(self, parent, scenes, on_complete: Callable):
        """
        Initialize scene selection window

        Args:
            parent: Parent window
            scenes: List of Scene objects
            on_complete: Callback function(selected_scenes, grouped_scenes)
        """
        self.parent = parent
        self.scenes = scenes
        self.on_complete = on_complete

        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Scene Selection - Video Archive Tool")
        self.window.geometry("900x750")  # Slightly taller for better scene visibility
        self.window.transient(parent)
        self.window.grab_set()

        # Center window on screen
        self._center_window(900, 750)

        # Selection state
        self.scene_vars = {}  # scene_number -> BooleanVar
        self.groups = []  # List of scene number lists: [[2,3,4,5], [7,8,9]]

        # Build UI
        self._build_ui()

        # Populate scenes
        self._populate_scenes()

    def _center_window(self, width: int, height: int):
        """
        Center window on screen

        Args:
            width: Window width
            height: Window height
        """
        # Update window to get accurate screen dimensions
        self.window.update_idletasks()

        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set position
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Build user interface"""

        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Make scrollable area expandable

        # Header with title and instructions combined
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        header_label = ttk.Label(
            header_frame,
            text=f"Scene Detection - {len(self.scenes)} scenes detected",
            font=('Arial', 12, 'bold')
        )
        header_label.grid(row=0, column=0, sticky=tk.W)

        instructions = ttk.Label(
            header_frame,
            text="Select scenes to export. Use 'Group Selected' to combine multiple scenes into one clip.",
            wraplength=800,
            foreground='gray'
        )
        instructions.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Scrollable scene list - now starts at row 1 (right after header)
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Canvas with scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scene_list_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        canvas_frame = canvas.create_window((0, 0), window=self.scene_list_frame, anchor=tk.NW)

        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.scene_list_frame.bind("<Configure>", configure_scroll_region)

        # Update canvas width when window resizes
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", configure_canvas_width)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Stats frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.stats_label = ttk.Label(stats_frame, text="Selected: 0 scenes (0.0s total)")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

        # Groups section
        groups_label = ttk.Label(
            main_frame,
            text="Scene Groups (will be exported as combined clips):",
            font=('Arial', 10, 'bold')
        )
        groups_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 5))

        # Groups list frame - reduced height
        self.groups_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1, height=80)
        self.groups_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.groups_container = ttk.Frame(self.groups_frame)
        self.groups_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initial placeholder
        self.no_groups_label = ttk.Label(
            self.groups_container,
            text="No groups created yet. Select scenes and click 'Add to Group'.",
            foreground='gray'
        )
        self.no_groups_label.pack()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="Select All", command=self._select_all).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self._deselect_all).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Add to Group", command=self._add_to_group).grid(row=0, column=2, padx=5)

        # Spacer
        button_frame.columnconfigure(3, weight=1)

        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="Export", command=self._export, style='Accent.TButton').grid(row=0, column=5, padx=5)

    def _populate_scenes(self):
        """Populate scene list with checkboxes and thumbnails"""

        for scene in self.scenes:
            # Scene frame
            scene_frame = ttk.Frame(self.scene_list_frame, relief=tk.RIDGE, borderwidth=1)
            scene_frame.grid(row=scene.scene_number - 1, column=0, sticky=(tk.W, tk.E), pady=2, padx=2)
            scene_frame.columnconfigure(2, weight=1)

            # Checkbox
            var = tk.BooleanVar(value=True)  # All selected by default
            self.scene_vars[scene.scene_number] = var

            checkbox = ttk.Checkbutton(
                scene_frame,
                variable=var,
                command=self._update_stats
            )
            checkbox.grid(row=0, column=0, padx=5, pady=5)

            # Thumbnail (slightly smaller to fit more scenes)
            thumbnail_label = None
            if scene.thumbnail_path and Path(scene.thumbnail_path).exists():
                try:
                    img = Image.open(scene.thumbnail_path)
                    # Resize to smaller thumbnail for more compact view
                    img.thumbnail((140, 80), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    thumbnail_label = ttk.Label(scene_frame, image=photo)
                    thumbnail_label.image = photo  # Keep reference
                    thumbnail_label.grid(row=0, column=1, padx=5, pady=3)
                except Exception as e:
                    # If thumbnail fails, use placeholder
                    pass

            if not thumbnail_label:
                placeholder = ttk.Label(scene_frame, text="[No Preview]", width=18, background='lightgray')
                placeholder.grid(row=0, column=1, padx=5, pady=3)

            # Scene info (more compact)
            info_text = (
                f"Scene {scene.scene_number}\n"
                f"{self._format_time(scene.start_time)} - {self._format_time(scene.end_time)}\n"
                f"Duration: {scene.duration:.1f}s"
            )
            info_label = ttk.Label(scene_frame, text=info_text, justify=tk.LEFT)
            info_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=3)

        # Initial stats update
        self._update_stats()

    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _update_stats(self):
        """Update selection statistics"""
        selected_count = sum(1 for var in self.scene_vars.values() if var.get())
        total_duration = sum(
            scene.duration
            for scene in self.scenes
            if self.scene_vars[scene.scene_number].get()
        )

        self.stats_label.config(
            text=f"Selected: {selected_count} scenes ({total_duration:.1f}s total)"
        )

    def _select_all(self):
        """Select all scenes"""
        for var in self.scene_vars.values():
            var.set(True)
        self._update_stats()

    def _deselect_all(self):
        """Deselect all scenes"""
        for var in self.scene_vars.values():
            var.set(False)
        self._update_stats()

    def _add_to_group(self):
        """Add selected scenes to a new group"""
        from tkinter import messagebox

        selected = [
            scene.scene_number
            for scene in self.scenes
            if self.scene_vars[scene.scene_number].get()
        ]

        if len(selected) < 2:
            messagebox.showwarning(
                "Add to Group",
                "Please select at least 2 scenes to create a group"
            )
            return

        # Add to groups list
        self.groups.append(selected)

        # Deselect all scenes (ready for next group)
        self._deselect_all()

        # Update groups display
        self._update_groups_display()

        messagebox.showinfo(
            "Group Created",
            f"Group {len(self.groups)} created with {len(selected)} scenes\n"
            f"Scenes: {', '.join(map(str, selected))}"
        )

    def _update_groups_display(self):
        """Update the groups display section"""
        # Clear existing widgets
        for widget in self.groups_container.winfo_children():
            widget.destroy()

        if not self.groups:
            # Show placeholder
            self.no_groups_label = ttk.Label(
                self.groups_container,
                text="No groups created yet. Select scenes and click 'Add to Group'.",
                foreground='gray'
            )
            self.no_groups_label.pack()
            return

        # Display each group
        for idx, group in enumerate(self.groups):
            group_frame = ttk.Frame(self.groups_container, relief=tk.RAISED, borderwidth=1)
            group_frame.pack(fill=tk.X, pady=2)

            # Group info
            scenes_str = ', '.join(map(str, group))
            total_duration = sum(
                scene.duration
                for scene in self.scenes
                if scene.scene_number in group
            )

            info_text = f"Group {idx + 1}: Scenes [{scenes_str}] - {total_duration:.1f}s"
            ttk.Label(group_frame, text=info_text).pack(side=tk.LEFT, padx=10, pady=5)

            # Remove button
            ttk.Button(
                group_frame,
                text="Remove",
                command=lambda i=idx: self._remove_group(i),
                width=8
            ).pack(side=tk.RIGHT, padx=5, pady=2)

    def _remove_group(self, group_index: int):
        """Remove a group"""
        if 0 <= group_index < len(self.groups):
            del self.groups[group_index]
            self._update_groups_display()

    def _export(self):
        """Export selected scenes and groups"""
        from tkinter import messagebox

        # Get individually selected scenes (not in any group)
        selected_scenes = [
            scene
            for scene in self.scenes
            if self.scene_vars[scene.scene_number].get()
        ]

        # Check if we have anything to export
        if not selected_scenes and not self.groups:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one scene or create a group to export"
            )
            return

        # Convert group scene numbers to Scene objects
        grouped_scenes = []
        for group in self.groups:
            group_scenes = [
                scene
                for scene in self.scenes
                if scene.scene_number in group
            ]
            if group_scenes:
                grouped_scenes.append(group_scenes)

        # Show export summary
        summary_parts = []
        if selected_scenes:
            summary_parts.append(f"{len(selected_scenes)} individual scene(s)")
        if grouped_scenes:
            summary_parts.append(f"{len(grouped_scenes)} group(s)")

        result = messagebox.askyesno(
            "Confirm Export",
            f"Export:\n• " + "\n• ".join(summary_parts) + "\n\nProceed?"
        )

        if not result:
            return

        # Call completion callback
        self.window.destroy()
        self.on_complete(selected_scenes, grouped_scenes)

    def _cancel(self):
        """Cancel scene selection"""
        self.window.destroy()
        # Call callback with None to indicate cancellation
        self.on_complete(None, None)
