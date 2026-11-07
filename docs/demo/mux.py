"""Phase 4: lay the narration clips on a timeline and encode captions + voice into an MP4.

Run (needs imageio-ffmpeg for a local ffmpeg binary; nothing is installed globally):
    uv run --with imageio-ffmpeg python mux.py [output.mp4]
"""

import json
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).parent
RATE = 24000
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "acme-pay-demo.mp4"


def video_lag(ffmpeg: str, take: dict) -> float:
    """How far Playwright's video clock runs behind the recorder's clock, measured from pixels.

    The dark title card is removed at a known moment (marks.titleOff, recorder clock); the same
    moment shows up in the raw video as a jump from dark to bright. The difference is the lag.
    """
    fps, window = 20, 40
    raw = subprocess.run(
        [ffmpeg, "-loglevel", "error", "-i", take["videoPath"], "-t", str(window),
         "-vf", f"fps={fps},scale=32:18,format=gray", "-f", "rawvideo", "-"],
        capture_output=True, check=True,
    ).stdout
    size = 32 * 18
    means = [sum(raw[i : i + size]) / size for i in range(0, len(raw) - size + 1, size)]
    jump = next(i for i in range(1, len(means)) if means[i] - means[i - 1] > 40)
    lag = take["marks"]["titleOff"] - jump / fps
    print(f"title card leaves the video at {jump / fps:.2f}s, recorder says {take['marks']['titleOff']:.2f}s -> lag {lag:.2f}s")
    return lag


def main() -> None:
    take = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    lag = video_lag(ffmpeg, take)
    trim = take["trimStart"] - lag  # position in the raw video that corresponds to the recorder's trimStart
    track = bytearray()
    for item in take["timeline"]:
        position = int((item["start"] - take["trimStart"]) * RATE) * 2
        with wave.open(item["file"]) as clip:
            assert (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) == (1, 2, RATE)
            pcm = clip.readframes(clip.getnframes())
        assert position >= len(track) - 2, f"clip {item['id']} would overlap the previous one"
        track.extend(bytes(max(0, position - len(track))))
        track.extend(pcm)
    narration = HERE / "narration.wav"
    with wave.open(str(narration), "wb") as out:
        out.setnchannels(1), out.setsampwidth(2), out.setframerate(RATE)
        out.writeframes(bytes(track))
    print(f"narration track: {len(track) / 2 / RATE:.1f}s")

    command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-ss", f"{trim:.3f}", "-i", take["videoPath"], "-i", str(narration),
        # Playwright writes a frame only when the screen changes, so the first frame after the trim
        # point can be a fraction of a second late. start_time=0 repeats it back to 0 without
        # moving any later frame (and so without disturbing sync with the audio).
        "-vf", "fps=25:start_time=0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "volume=0.9",  # ~1 dB headroom so AAC encoding cannot clip the loudest clips
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
        str(OUTPUT),
    ]
    subprocess.run(command, check=True)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
