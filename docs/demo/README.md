# Demo video

[`acme-pay-demo.mp4`](acme-pay-demo.mp4): a 2 min 51 s walkthrough of ACME Pay from the HR manager's point of view, with burned-in captions and narration. The story follows [../demo-script.md](../demo-script.md): Pay Pulse, a signal, Benchmarks, a below-band employee, a previewed and saved raise, a rejected duplicate, search, the AI analyst, and the test-first commit history.

## Things worth knowing
- **The voice is synthetic.** It is Gemini text-to-speech (voice "Kore"). The captions are the narration text.
- **The numbers are read from the app, not typed.** `plan.mjs` queries the API and writes the narration from the live figures (headcount, payroll, the person and the raise amount), so what is said always matches what is on screen.
- **Recorded on a local copy of the app.** The demo *saves* a salary change, so it ran against a local database with the same code and the same deterministic seed (plus the one extra employee the live database has). The deployed data was left untouched. The recording has no browser chrome, so there is no URL to show.
- **Sync is measured, not assumed.** Playwright's video clock starts after the page opens, by a different amount on every take. `mux.py` finds the offset from the pixels (the moment the title card disappears) and corrects for it. The delivered file is within 0.02 s of the audio.

## How it is made
Four small scripts, each with one job:

| Phase | Script | What it does |
|---|---|---|
| 1. Plan | `plan.mjs` | Reads the running app and writes `plan.json`: the narration beats, built from real numbers |
| 2. Voice | `tts.py` | One TTS clip per beat, cached by text. A text model transcribes each clip so what was actually said can be checked |
| 3. Record | `record.mjs` | Drives the app in a browser while recording. Captions and a visible cursor are overlaid (`overlay.js`); each on-screen action is timed to its sentence |
| 4. Mux | `mux.py` | Places the clips on a timeline, corrects the clock offset and encodes the MP4 (H.264 + AAC) |

```bash
# the app must be running with the seeded data (see the root README)
cd docs/demo && npm install                                    # Playwright (not part of the app)
DEMO_BASE_URL=http://localhost:5173 node plan.mjs              # narration from live numbers
cd ../../backend && uv run python ../docs/demo/tts.py          # voice clips (needs GEMINI_API_KEY)
cd ../docs/demo && DEMO_BASE_URL=http://localhost:5173 node record.mjs
cd ../../backend && uv run --with imageio-ffmpeg python ../docs/demo/mux.py
```

`imageio-ffmpeg` supplies a local ffmpeg binary for the last step; nothing is installed globally. Each take saves a salary change, so reseed (`python -m acme_pay.seed`) between takes.

## Constraints that shaped it
- **Free-tier TTS allows 10 requests per model per day.** The narration is therefore 8 clips of about 20 s, all from one model so the voice is consistent, and finished clips are cached. A style instruction in the prompt made the voice slow to about 1.2 words per second, so the final clips use none. The pace check in `tts.py` flags this.
- **Captions run on their own timers.** A slow action (GitHub is slow to load) can delay what is on screen but never the caption, which follows the voice.
