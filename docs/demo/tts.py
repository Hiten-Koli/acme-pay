"""Phase 2: one narration clip per beat in plan.json (Gemini TTS), cached by text.

Free-tier TTS allows only 10 requests per model per day, so this uses ONE model for every
clip (consistent voice), never retries a daily-quota 429, and caches finished clips.
Each clip is then transcribed by a text model so what was actually said can be checked.

Run from backend/ (loads GEMINI_API_KEY from the project's settings):
    uv run python <this file>
"""

import base64
import hashlib
import io
import json
import math
import os
import struct
import time
import wave
from pathlib import Path

import httpx

from acme_pay.core.config import get_settings

HERE = Path(__file__).parent
AUDIO = HERE / "audio"
API = "https://generativelanguage.googleapis.com/v1beta/models"
MODELS = os.environ.get("TTS_MODELS", "gemini-3.1-flash-tts-preview,gemini-3.8-flash-lite-tts").split(",")
VOICE = os.environ.get("TTS_VOICE", "Kore")
RATE = 24000
LEAD_KEEP, TRAIL_KEEP = 0.15, 0.25  # seconds of silence kept around the speech
THRESHOLD = 500


class QuotaExhausted(Exception):
    """The model's free daily quota is used up."""


def synthesize(client: httpx.Client, key: str, model: str, text: str) -> bytes:
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    for attempt in range(1, 5):
        try:
            response = client.post(f"{API}/{model}:generateContent", headers={"x-goog-api-key": key}, json=body, timeout=180)
        except httpx.HTTPError as error:
            print(f"    {type(error).__name__}; retrying")
            time.sleep(5 * attempt)
            continue
        if response.status_code == 200:
            part = response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
            audio = base64.b64decode(part["data"])
            (AUDIO / "raw").mkdir(exist_ok=True)  # never lose a paid-for response to a later bug
            (AUDIO / "raw" / f"{hashlib.sha256(text.encode()).hexdigest()[:10]}-{model}.bin").write_bytes(audio)
            print(f"    {model} returned {part['mimeType']}, {len(audio)} bytes")
            return audio if audio[:4] == b"RIFF" else pcm_to_wav(audio, part["mimeType"])
        message = response.json().get("error", {}).get("message", "")
        if response.status_code == 429 and "PerDay" in response.text:
            raise QuotaExhausted(model)
        print(f"    HTTP {response.status_code} {message[:90]!r}; retrying")
        time.sleep(8 * attempt)
    raise SystemExit(f"{model}: failed repeatedly")


def pcm_to_wav(pcm: bytes, mime_type: str) -> bytes:
    """Wrap headerless 16-bit mono PCM (e.g. 'audio/L16;codec=pcm;rate=24000') in a WAV container."""
    rate = int(mime_type.split("rate=")[1].split(";")[0]) if "rate=" in mime_type else RATE
    out = io.BytesIO()
    with wave.open(out, "wb") as clip:
        clip.setnchannels(1), clip.setsampwidth(2), clip.setframerate(rate)
        clip.writeframes(pcm)
    return out.getvalue()


def trim(raw: bytes) -> bytes:
    """Trim leading and trailing silence, keeping a small margin; return a 16-bit mono WAV."""
    with wave.open(io.BytesIO(raw)) as clip:
        assert (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) == (1, 2, RATE)
        frames = clip.readframes(clip.getnframes())
    samples = struct.unpack(f"<{len(frames) // 2}h", frames)
    first = next((i for i, s in enumerate(samples) if abs(s) > THRESHOLD), 0)
    last = len(samples) - next((i for i, s in enumerate(reversed(samples)) if abs(s) > THRESHOLD), 0)
    start, end = max(0, first - int(LEAD_KEEP * RATE)), min(len(samples), last + int(TRAIL_KEEP * RATE))
    out = io.BytesIO()
    with wave.open(out, "wb") as clip:
        clip.setnchannels(1), clip.setsampwidth(2), clip.setframerate(RATE)
        clip.writeframes(struct.pack(f"<{end - start}h", *samples[start:end]))
    return out.getvalue()


def stats(raw: bytes) -> tuple[float, float]:
    with wave.open(io.BytesIO(raw)) as clip:
        frames = clip.readframes(clip.getnframes())
        seconds = clip.getnframes() / clip.getframerate()
    peak = max(abs(s) for s in struct.unpack(f"<{len(frames) // 2}h", frames)) or 1
    return seconds, 20 * math.log10(peak / 32768)


def transcribe(client: httpx.Client, key: str, raw: bytes) -> str:
    body = {"contents": [{"parts": [
        {"text": "Transcribe this audio verbatim, word for word. Output only the transcript."},
        {"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(raw).decode()}},
    ]}]}
    response = client.post(f"{API}/gemini-3.5-flash-lite:generateContent", headers={"x-goog-api-key": key}, json=body, timeout=120)
    if response.status_code != 200:
        return f"(transcription unavailable: HTTP {response.status_code})"
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def main() -> None:
    plan = json.loads((HERE / "plan.json").read_text(encoding="utf-8"))
    key = get_settings().gemini_api_key
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")
    AUDIO.mkdir(exist_ok=True)
    clips: dict[str, dict[str, object]] = {}
    model = None
    with httpx.Client() as client:
        for beat in plan["beats"]:
            text = beat["text"]
            cached = next(iter(sorted(AUDIO.glob(f"{beat['id']}-{hashlib.sha256((VOICE + '|' + text).encode()).hexdigest()[:10]}-*.wav"))), None)
            if cached:
                raw, source, used = cached.read_bytes(), "cached", cached.stem.split("-", 2)[2]
                path = cached
            else:
                raw = None
                for candidate in ([model] if model else MODELS):
                    try:
                        raw = trim(synthesize(client, key, candidate, text))
                        model = used = candidate
                        break
                    except QuotaExhausted:
                        print(f"    {candidate}: daily quota exhausted")
                if raw is None:
                    raise SystemExit("No TTS model has quota left today; resume later (clips so far are cached)")
                digest = hashlib.sha256((VOICE + "|" + text).encode()).hexdigest()[:10]
                path = AUDIO / f"{beat['id']}-{digest}-{used}.wav"
                path.write_bytes(raw)
                source = "generated"
                time.sleep(3)
            seconds, peak = stats(raw)
            words = len(text.split())
            transcript = transcribe(client, key, raw)
            clips[beat["id"]] = {"file": str(path), "seconds": seconds, "words": words, "transcript": transcript}
            print(f"{beat['id']:8} {source:9} {seconds:5.1f}s  {words / seconds:.2f} words/s  peak {peak:.1f} dBFS  [{used}]")
            print(f"         said: {transcript}")
    (HERE / "clips.json").write_text(json.dumps(clips, indent=2), encoding="utf-8")
    print(f"total speech: {sum(float(c['seconds']) for c in clips.values()):.0f}s")  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
