"""FFmpeg wrapper with GPU acceleration support"""

import os
import subprocess
import platform
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any


class FFmpegWrapper:
    """Wrapper for FFmpeg operations with GPU acceleration detection and fallback"""

    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize FFmpeg wrapper

        Args:
            ffmpeg_path: Path to ffmpeg executable (default: searches in PATH and App/ffmpeg/)
        """
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_path = self._find_ffmpeg(ffmpeg_path)
        self.ffprobe_path = self._find_ffprobe()
        self.cuda_available = self._check_cuda_support()
        self.nvenc_available = self._check_nvenc_support()

        self.logger.info(f"FFmpeg path: {self.ffmpeg_path}")
        self.logger.info(f"CUDA available: {self.cuda_available}")
        self.logger.info(f"NVENC available: {self.nvenc_available}")

    def _find_ffmpeg(self, custom_path: Optional[str] = None) -> str:
        """Find FFmpeg executable"""
        if custom_path and os.path.exists(custom_path):
            return custom_path

        # Check App/ffmpeg directory
        app_ffmpeg = Path("App/ffmpeg/ffmpeg.exe")
        if app_ffmpeg.exists():
            return str(app_ffmpeg)

        # Check PATH
        try:
            result = subprocess.run(
                ["where" if platform.system() == "Windows" else "which", "ffmpeg"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception as e:
            self.logger.warning(f"Error finding ffmpeg: {e}")

        raise FileNotFoundError("FFmpeg executable not found")

    def _find_ffprobe(self) -> str:
        """Find FFprobe executable"""
        ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
        ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")

        if os.path.exists(ffprobe_path):
            return ffprobe_path

        # Try PATH
        try:
            result = subprocess.run(
                ["where" if platform.system() == "Windows" else "which", "ffprobe"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass

        self.logger.warning("FFprobe not found")
        return ""

    def _check_cuda_support(self) -> bool:
        """Check if CUDA hardware acceleration is available"""
        try:
            import cv2
            if hasattr(cv2, 'cuda'):
                count = cv2.cuda.getCudaEnabledDeviceCount()
                if count > 0:
                    self.logger.info(f"Found {count} CUDA-enabled device(s)")
                    return True
        except Exception as e:
            self.logger.debug(f"CUDA check failed: {e}")

        return False

    def _check_nvenc_support(self) -> bool:
        """Check if NVENC encoder is available in FFmpeg"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-encoders"],
                capture_output=True,
                text=True,
                check=False
            )
            encoders = result.stdout

            has_nvenc = "h264_nvenc" in encoders or "hevc_nvenc" in encoders

            if has_nvenc:
                self.logger.info("NVENC encoder available")
            else:
                self.logger.warning("NVENC encoder not available, will use CPU encoding")

            return has_nvenc
        except Exception as e:
            self.logger.error(f"Error checking NVENC support: {e}")
            return False

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get detailed video information using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video properties
        """
        if not self.ffprobe_path:
            raise RuntimeError("FFprobe not available")

        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)

            # Extract video stream info
            video_stream = next(
                (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
                None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            format_info = data.get('format', {})

            return {
                'codec': video_stream.get('codec_name', ''),
                'codec_long_name': video_stream.get('codec_long_name', ''),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'duration': float(format_info.get('duration', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'size_bytes': int(format_info.get('size', 0)),
                'color_space': video_stream.get('color_space', ''),
                'color_primaries': video_stream.get('color_primaries', ''),
                'color_transfer': video_stream.get('color_transfer', ''),
                'pix_fmt': video_stream.get('pix_fmt', ''),
                'profile': video_stream.get('profile', ''),
                'has_audio': any(s.get('codec_type') == 'audio' for s in data.get('streams', []))
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFprobe error: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            raise

    def validate_prores(self, video_path: str) -> bool:
        """
        Validate if video is ProRes format

        Args:
            video_path: Path to video file

        Returns:
            True if valid ProRes, False otherwise
        """
        try:
            info = self.get_video_info(video_path)
            codec = info.get('codec', '').lower()

            # Check for ProRes codec
            is_prores = 'prores' in codec

            if is_prores:
                profile = info.get('profile', '')
                self.logger.info(f"Valid ProRes video detected: {profile}")
            else:
                self.logger.warning(f"Not ProRes: codec is {info.get('codec_long_name', 'unknown')}")

            return is_prores
        except Exception as e:
            self.logger.error(f"Error validating ProRes: {e}")
            return False

    def build_encode_command(
        self,
        input_path: str,
        output_path: str,
        use_gpu: bool = True,
        crf: int = 20,
        preset: str = "slow",
        audio_bitrate: str = "320k"
    ) -> List[str]:
        """
        Build FFmpeg encoding command

        Args:
            input_path: Input video path
            output_path: Output video path
            use_gpu: Use GPU encoding if available
            crf: Constant Rate Factor (quality, lower = better)
            preset: Encoding preset
            audio_bitrate: Audio bitrate

        Returns:
            FFmpeg command as list
        """
        cmd = [self.ffmpeg_path]

        # Input options
        if use_gpu and self.cuda_available:
            cmd.extend(["-hwaccel", "cuda"])

        cmd.extend(["-i", input_path])

        # Video encoding
        if use_gpu and self.nvenc_available:
            # NVENC encoding
            cmd.extend([
                "-c:v", "h264_nvenc",
                "-preset", "p7",  # Highest quality NVENC preset
                "-rc", "vbr",
                "-cq", str(crf),
                "-b:v", "0",  # VBR mode
                "-profile:v", "high",
                "-level", "4.1"
            ])
        else:
            # x264 CPU encoding
            cmd.extend([
                "-c:v", "libx264",
                "-crf", str(crf),
                "-preset", preset,
                "-profile:v", "high",
                "-level", "4.1"
            ])

        # Audio encoding
        cmd.extend([
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-ar", "48000"
        ])

        # Pixel format
        cmd.extend(["-pix_fmt", "yuv420p"])

        # Output
        cmd.extend(["-y", output_path])  # -y to overwrite

        return cmd

    def build_extract_frame_command(
        self,
        input_path: str,
        output_path: str,
        timestamp: float,
        preserve_color: bool = True
    ) -> List[str]:
        """
        Build command to extract a single frame

        Args:
            input_path: Input video path
            output_path: Output image path
            timestamp: Time in seconds
            preserve_color: Preserve native color space

        Returns:
            FFmpeg command as list
        """
        cmd = [self.ffmpeg_path]

        # Seek to timestamp
        cmd.extend(["-ss", str(timestamp)])

        # Input
        cmd.extend(["-i", input_path])

        # Extract single frame
        cmd.extend(["-frames:v", "1"])

        # High quality PNG encoding with fast compression
        cmd.extend(["-compression_level", "0"])  # Fast compression for extraction speed

        # Explicitly set pixel format to avoid color conversion issues in FFmpeg 8.0
        # rgb24 preserves color accurately and avoids the out_color_matrix=-1 bug
        cmd.extend(["-pix_fmt", "rgb24"])

        # Output
        cmd.extend(["-y", output_path])

        return cmd

    def run_command(
        self,
        cmd: List[str],
        capture_output: bool = True,
        timeout: Optional[int] = None,
        progress_callback=None
    ):
        """
        Run FFmpeg command with optional progress tracking

        Args:
            cmd: Command list
            capture_output: Capture stdout/stderr
            timeout: Timeout in seconds
            progress_callback: Optional callback(percent) for progress updates

        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        self.logger.debug(f"Running command: {' '.join(cmd)}")

        try:
            if progress_callback:
                # Run with progress tracking (requires parsing stderr)
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )

                # Parse FFmpeg progress from stderr
                for line in process.stderr:
                    if progress_callback and 'time=' in line:
                        # Extract progress (this is a simple implementation)
                        # For accurate progress, we'd need to know the total duration
                        # For now, just call the callback
                        try:
                            # Parse time=HH:MM:SS.MS
                            time_str = line.split('time=')[1].split()[0]
                            # Simple progress indication
                            progress_callback(0)  # Placeholder
                        except:
                            pass

                process.wait(timeout=timeout)

                if process.returncode != 0:
                    error_msg = f"FFmpeg error (code {process.returncode})"
                    self.logger.error(error_msg)
                    return False, error_msg
                else:
                    self.logger.debug("FFmpeg command succeeded")
                    return True, None
            else:
                # Simple execution without progress
                result = subprocess.run(
                    cmd,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    check=False
                )

                if result.returncode != 0:
                    error_msg = f"FFmpeg error (code {result.returncode}): {result.stderr}"
                    self.logger.error(error_msg)
                    return False, error_msg
                else:
                    self.logger.debug("FFmpeg command succeeded")
                    return True, None

        except subprocess.TimeoutExpired:
            error_msg = f"FFmpeg command timed out after {timeout}s"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running FFmpeg: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def get_encoder_type(self) -> str:
        """Get the encoder type that will be used"""
        if self.nvenc_available:
            return "nvenc"
        return "x264"
