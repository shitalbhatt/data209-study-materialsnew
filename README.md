# DATA209: Advanced Exploratory Data Analysis

Study materials for DATA209 (BTech Hons. Data Science, Semester III).

| Folder | Contents |
|---|---|
| `site/` | Interactive study website (GitHub Pages) with the revision video page |
| `notes/` | Module notes in Markdown |
| `practice/` | 25 practice questions with answers |
| `site/slide-videos/` | 21 narrated videos stepping through your real lecture and lab slides (Modules 1-4), listed on `site/slide-videos.html` |
| `scripts/make_slide_videos.py` | Builds them from the slide PDFs (`python3 scripts/make_slide_videos.py SRC_DIR`) |
| `site/videos/` | 19 narrated videos: one per lecture pair (L1-2 ... L29-30) and 4 lab videos, listed on `site/videos.html` |
| `scripts/make_lecture_videos.py` | Regenerates those videos and `videos.html` |
| `video/` | Revision video (`data209-revision.mp4`, narrated by text-to-speech, 17 slides) |
| `scripts/make_video.py` | Regenerates the video (needs Pillow, ffmpeg and espeak-ng) |

Enable Pages (Settings > Pages > Source: GitHub Actions) to publish the site on every push to `main`.

## Rebuild with the Indian English female voice
Needs internet access to `speech.platform.bing.com`.
```
pip install edge-tts
VOICE=edge python3 scripts/make_slide_videos.py /path/to/slide/pdfs      # all 21 slide videos
VOICE=edge python3 scripts/make_lecture_videos.py                        # summary videos
```
The voice is `en-IN-NeerjaNeural` (change with `EDGE_VOICE`, speed with `EDGE_RATE`).
