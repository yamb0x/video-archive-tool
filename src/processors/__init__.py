"""Processor modules for specialized operations"""
from .scene_detector import SceneDetector, Scene
from .image_processor import ImageProcessor
from .video_clip_generator import VideoClipGenerator

__all__ = ['SceneDetector', 'Scene', 'ImageProcessor', 'VideoClipGenerator']
