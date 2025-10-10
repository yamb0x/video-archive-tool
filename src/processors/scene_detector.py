"""Scene detection using PySceneDetect"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from scenedetect import detect, ContentDetector, AdaptiveDetector
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager


@dataclass
class Scene:
    """Scene information"""
    scene_number: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    thumbnail_path: Optional[str] = None


class SceneDetector:
    """Detect scenes in video using PySceneDetect"""

    def __init__(self, ffmpeg_wrapper=None):
        """
        Initialize scene detector

        Args:
            ffmpeg_wrapper: FFmpeg wrapper for thumbnail generation
        """
        self.logger = logging.getLogger(__name__)
        self.ffmpeg = ffmpeg_wrapper

    def detect_scenes(
        self,
        video_path: str,
        threshold: float = 30.0,
        min_scene_len: int = 15,
        method: str = "content"
    ) -> List[Scene]:
        """
        Detect scenes in video

        Args:
            video_path: Path to video file
            threshold: Detection threshold (higher = less sensitive)
            min_scene_len: Minimum scene length in frames
            method: Detection method ("content" or "adaptive")

        Returns:
            List of Scene objects
        """
        try:
            self.logger.info(f"Detecting scenes in: {video_path}")
            self.logger.info(f"Threshold: {threshold}, Min length: {min_scene_len}")

            # Use simple detect API from scenedetect
            if method == "adaptive":
                scene_list = detect(
                    video_path,
                    AdaptiveDetector(adaptive_threshold=threshold, min_scene_len=min_scene_len)
                )
            else:
                scene_list = detect(
                    video_path,
                    ContentDetector(threshold=threshold, min_scene_len=min_scene_len)
                )

            # Convert to Scene objects
            scenes = []
            for idx, (start_time, end_time) in enumerate(scene_list, start=1):
                scene = Scene(
                    scene_number=idx,
                    start_frame=start_time.get_frames(),
                    end_frame=end_time.get_frames(),
                    start_time=start_time.get_seconds(),
                    end_time=end_time.get_seconds(),
                    duration=end_time.get_seconds() - start_time.get_seconds()
                )
                scenes.append(scene)

            self.logger.info(f"Detected {len(scenes)} scenes")

            # Log scene details
            for scene in scenes:
                self.logger.debug(
                    f"Scene {scene.scene_number}: "
                    f"{scene.start_time:.2f}s - {scene.end_time:.2f}s "
                    f"({scene.duration:.2f}s)"
                )

            return scenes

        except Exception as e:
            self.logger.error(f"Error detecting scenes: {e}", exc_info=True)
            raise

    def generate_thumbnails(
        self,
        video_path: str,
        scenes: List[Scene],
        output_dir: str,
        artwork_name: str
    ) -> List[Scene]:
        """
        Generate thumbnail images for scenes

        Args:
            video_path: Path to video file
            scenes: List of Scene objects
            output_dir: Directory for thumbnails
            artwork_name: Artwork name for filenames

        Returns:
            Updated list of Scene objects with thumbnail paths
        """
        if not self.ffmpeg:
            self.logger.warning("FFmpeg wrapper not available, skipping thumbnails")
            return scenes

        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            for scene in scenes:
                # Extract frame from scene midpoint
                midpoint = scene.start_time + (scene.duration / 2)

                thumbnail_filename = f"{artwork_name}_scene_{scene.scene_number:02d}_thumb.jpg"
                thumbnail_path = output_path / thumbnail_filename

                # Build FFmpeg command for thumbnail
                cmd = [
                    self.ffmpeg.ffmpeg_path,
                    "-ss", str(midpoint),
                    "-i", video_path,
                    "-frames:v", "1",
                    "-vf", "scale=320:-1",  # Width 320, maintain aspect ratio
                    "-q:v", "5",  # JPEG quality
                    "-y",
                    str(thumbnail_path)
                ]

                result = self.ffmpeg.run_command(cmd, timeout=30)

                if result.returncode == 0 and thumbnail_path.exists():
                    scene.thumbnail_path = str(thumbnail_path)
                    self.logger.debug(f"Generated thumbnail: {thumbnail_path}")
                else:
                    self.logger.warning(f"Failed to generate thumbnail for scene {scene.scene_number}")

            self.logger.info(f"Generated thumbnails in: {output_dir}")
            return scenes

        except Exception as e:
            self.logger.error(f"Error generating thumbnails: {e}")
            return scenes

    def get_scene_at_time(self, scenes: List[Scene], timestamp: float) -> Optional[Scene]:
        """
        Get scene containing a specific timestamp

        Args:
            scenes: List of Scene objects
            timestamp: Time in seconds

        Returns:
            Scene object or None
        """
        for scene in scenes:
            if scene.start_time <= timestamp <= scene.end_time:
                return scene
        return None

    def merge_scenes(self, scenes: List[Scene], scene_numbers: List[int]) -> Scene:
        """
        Merge multiple scenes into one

        Args:
            scenes: List of all Scene objects
            scene_numbers: Scene numbers to merge

        Returns:
            New merged Scene object
        """
        # Get scenes to merge
        to_merge = [s for s in scenes if s.scene_number in scene_numbers]

        if not to_merge:
            raise ValueError("No scenes to merge")

        # Sort by start time
        to_merge.sort(key=lambda s: s.start_time)

        # Create merged scene
        merged = Scene(
            scene_number=to_merge[0].scene_number,
            start_frame=to_merge[0].start_frame,
            end_frame=to_merge[-1].end_frame,
            start_time=to_merge[0].start_time,
            end_time=to_merge[-1].end_time,
            duration=to_merge[-1].end_time - to_merge[0].start_time
        )

        self.logger.info(
            f"Merged scenes {scene_numbers} into one "
            f"({merged.duration:.2f}s)"
        )

        return merged

    def export_scene_data(self, scenes: List[Scene]) -> List[Dict[str, Any]]:
        """
        Export scene data to dict format for JSON storage

        Args:
            scenes: List of Scene objects

        Returns:
            List of scene dictionaries
        """
        return [
            {
                'scene_number': s.scene_number,
                'start_frame': s.start_frame,
                'end_frame': s.end_frame,
                'start_time': s.start_time,
                'end_time': s.end_time,
                'duration': s.duration,
                'thumbnail_path': s.thumbnail_path
            }
            for s in scenes
        ]

    def import_scene_data(self, scene_data: List[Dict[str, Any]]) -> List[Scene]:
        """
        Import scene data from dict format

        Args:
            scene_data: List of scene dictionaries

        Returns:
            List of Scene objects
        """
        return [
            Scene(
                scene_number=s['scene_number'],
                start_frame=s['start_frame'],
                end_frame=s['end_frame'],
                start_time=s['start_time'],
                end_time=s['end_time'],
                duration=s['duration'],
                thumbnail_path=s.get('thumbnail_path')
            )
            for s in scene_data
        ]
