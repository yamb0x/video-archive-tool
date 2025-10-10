"""Configuration management"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage application configuration from JSON files"""

    def __init__(self, settings_path: str = "config/settings.json", presets_path: str = "config/default_presets.json"):
        """
        Initialize configuration manager

        Args:
            settings_path: Path to settings JSON file
            presets_path: Path to presets JSON file
        """
        self.logger = logging.getLogger(__name__)
        self.settings_path = Path(settings_path)
        self.presets_path = Path(presets_path)

        self.settings = {}
        self.presets = {}

        self._load_config()

    def _load_config(self):
        """Load configuration from files"""
        # Load settings
        try:
            if self.settings_path.exists():
                with open(self.settings_path, 'r') as f:
                    self.settings = json.load(f)
                    self.logger.info(f"Loaded settings from {self.settings_path}")
            else:
                self.logger.warning(f"Settings file not found: {self.settings_path}")
                self.settings = self._get_default_settings()
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.settings = self._get_default_settings()

        # Load presets
        try:
            if self.presets_path.exists():
                with open(self.presets_path, 'r') as f:
                    self.presets = json.load(f)
                    self.logger.info(f"Loaded presets from {self.presets_path}")
            else:
                self.logger.warning(f"Presets file not found: {self.presets_path}")
                self.presets = self._get_default_presets()
        except Exception as e:
            self.logger.error(f"Error loading presets: {e}")
            self.presets = self._get_default_presets()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings if file doesn't exist"""
        return {
            "version": "1.0.0",
            "app_name": "Video Archive Tool",
            "copyright": "© Yambo Studio",
            "paths": {
                "last_output_dir": "",
                "last_master_dir": "",
                "last_rd_dir": ""
            },
            "defaults": {
                "preset": "webflow_standard",
                "scene_detection": {
                    "threshold": 30.0,
                    "min_scene_length": 15
                },
                "encoding": {
                    "encoder_preference": "x264",
                    "gpu_enabled": True
                }
            },
            "behavior": {
                "auto_open_output": True,
                "generate_log": True
            }
        }

    def _get_default_presets(self) -> Dict[str, Any]:
        """Get default presets if file doesn't exist"""
        return {
            "version": "1.0.0",
            "presets": [
                {
                    "id": "webflow_standard",
                    "name": "Webflow Standard",
                    "description": "Optimized for Webflow"
                }
            ]
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation, e.g., 'paths.last_output_dir')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any):
        """
        Set configuration value

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.settings

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save(self):
        """Save configuration to file"""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)

            self.logger.info(f"Settings saved to {self.settings_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False

    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preset by ID

        Args:
            preset_id: Preset identifier

        Returns:
            Preset dictionary or None
        """
        for preset in self.presets.get('presets', []):
            if preset.get('id') == preset_id or preset.get('name') == preset_id:
                return preset
        return None

    def get_all_presets(self) -> list:
        """Get all available presets"""
        return self.presets.get('presets', [])

    def save_presets(self) -> bool:
        """
        Save presets to file

        Returns:
            True if successful
        """
        try:
            self.presets_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.presets_path, 'w') as f:
                json.dump(self.presets, f, indent=2)

            self.logger.info(f"Presets saved to {self.presets_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving presets: {e}")
            return False

    def add_preset(self, preset: Dict[str, Any]) -> bool:
        """
        Add a new preset

        Args:
            preset: Preset dictionary

        Returns:
            True if successful
        """
        try:
            if 'presets' not in self.presets:
                self.presets['presets'] = []

            self.presets['presets'].append(preset)
            return self.save_presets()

        except Exception as e:
            self.logger.error(f"Error adding preset: {e}")
            return False

    def update_preset(self, preset_id: str, preset: Dict[str, Any]) -> bool:
        """
        Update an existing preset

        Args:
            preset_id: ID of preset to update
            preset: Updated preset dictionary

        Returns:
            True if successful
        """
        try:
            for idx, p in enumerate(self.presets.get('presets', [])):
                if p.get('id') == preset_id:
                    # Check if preset is editable
                    if not p.get('editable', False):
                        self.logger.warning(f"Cannot update built-in preset: {preset_id}")
                        return False

                    self.presets['presets'][idx] = preset
                    return self.save_presets()

            self.logger.warning(f"Preset not found: {preset_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error updating preset: {e}")
            return False

    def delete_preset(self, preset_id: str) -> bool:
        """
        Delete a preset

        Args:
            preset_id: ID of preset to delete

        Returns:
            True if successful
        """
        try:
            presets = self.presets.get('presets', [])
            for idx, p in enumerate(presets):
                if p.get('id') == preset_id:
                    # Check if preset is editable
                    if not p.get('editable', False):
                        self.logger.warning(f"Cannot delete built-in preset: {preset_id}")
                        return False

                    del self.presets['presets'][idx]
                    return self.save_presets()

            self.logger.warning(f"Preset not found: {preset_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error deleting preset: {e}")
            return False
