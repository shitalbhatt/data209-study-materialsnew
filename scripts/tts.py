"""Text to speech helper. VOICE=edge uses the Indian English female neural voice (needs internet and `pip install edge-tts`);
otherwise falls back to the offline espeak-ng voice."""
import asyncio, os, pathlib, subprocess, tempfile, time

EDGE_VOICE = os.environ.get("EDGE_VOICE", "en-IN-NeerjaNeural")
EDGE_RATE = os.environ.get("EDGE_RATE", "-5%")

def speak(text, wav, espeak_speed=155):
    wav = pathlib.Path(wav)
    if os.environ.get("VOICE", "").lower() == "edge":
        import edge_tts
        mp3 = wav.with_suffix(".mp3")
        for attempt in range(4):
            try:
                asyncio.run(edge_tts.Communicate(text, EDGE_VOICE, rate=EDGE_RATE, proxy=os.environ.get("HTTPS_PROXY")).save(str(mp3)))
                if mp3.stat().st_size > 0:
                    break
            except Exception:
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError("edge-tts failed; check network access to speech.platform.bing.com")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), str(wav)], check=True)
        mp3.unlink()
    else:
        subprocess.run(["espeak-ng", "-v", "en-us", "-s", str(espeak_speed), "-w", str(wav), text], check=True)
