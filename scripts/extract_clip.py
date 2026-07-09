"""Extract a short audio clip from a video/audio file using ffmpeg.

Usage:
    python extract_clip.py --input video.mp4 --start 0:07 --duration 2 --output clip.wav

Never modifies the input file. Output is 48kHz mono WAV (what CLAP expects).
Requires ffmpeg on PATH.
"""
import argparse
import platform
import shutil
import subprocess
import sys

_FFMPEG_INSTALL = {
    "Windows": "  Windows: winget install Gyan.FFmpeg  (then restart the terminal)",
    "Darwin": "  Mac: brew install ffmpeg",
}
_FFMPEG_INSTALL_DEFAULT = "  Linux: sudo apt install ffmpeg  (or your distro's package manager)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Source video/audio file")
    parser.add_argument("--start", required=True, help="Start time, e.g. 0:07 or 00:01:23.5")
    parser.add_argument("--duration", default="2", help="Clip length in seconds (default 2)")
    parser.add_argument("--output", default="clip.wav", help="Output WAV path")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        hint = _FFMPEG_INSTALL.get(platform.system(), _FFMPEG_INSTALL_DEFAULT)
        print(f"ffmpeg not found on PATH. Install it first:\n{hint}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        "ffmpeg", "-y",
        "-ss", args.start,
        "-t", args.duration,
        "-i", args.input,
        "-vn",
        "-ac", "1",
        "-ar", "48000",
        args.output,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2000:], file=sys.stderr)
        sys.exit(result.returncode)
    print(f"Extracted -> {args.output}")


if __name__ == "__main__":
    main()
