"""
FFmpeg discovery and configuration utility.
Ensures imageio-ffmpeg or system FFmpeg is accessible for Whisper and audio extraction.
"""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger("ffmpeg_setup")

def ensure_ffmpeg_available() -> str:
    """
    Checks if ffmpeg is in PATH. If not, locates imageio-ffmpeg binary,
    creates a standardized ffmpeg.exe copy if needed, and adds its directory to PATH.
    Returns the absolute path to the ffmpeg executable.
    """
    # 1. Check existing PATH
    existing = shutil.which("ffmpeg")
    if existing:
        logger.info(f"Using system FFmpeg found at: {existing}")
        return existing

    # 2. Check imageio_ffmpeg
    try:
        import imageio_ffmpeg
        exe_path = imageio_ffmpeg.get_ffmpeg_exe()
        if exe_path and os.path.exists(exe_path):
            exe_dir = os.path.dirname(exe_path)
            # Create a standard ffmpeg.exe alias if only the versioned executable exists
            standard_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
            standard_path = os.path.join(exe_dir, standard_name)
            if not os.path.exists(standard_path):
                try:
                    shutil.copyfile(exe_path, standard_path)
                except Exception as e:
                    logger.warning(f"Could not create alias '{standard_name}': {e}")
            
            # Prepend to PATH so subprocesses (including whisper) find it
            if exe_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"Configured bundled FFmpeg at: {standard_path if os.path.exists(standard_path) else exe_path}")
            return standard_path if os.path.exists(standard_path) else exe_path
    except ImportError:
        logger.warning("imageio-ffmpeg is not installed.")

    logger.warning("No FFmpeg executable could be located. MP4 audio extraction may fail.")
    return ""
