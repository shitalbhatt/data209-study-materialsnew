"""Builds vertical YouTube Shorts (1080x1920) from the course slide PDFs: two or three Shorts per lecture/lab video,
each showing one real slide with a headline and big captions, read by the voice from scripts/tts.py.

Usage: VOICE=edge python3 scripts/make_shorts.py SRC_DIR [video ids...]
Output: site/shorts/<id>-<n>.mp4, site/shorts.html, youtube/shorts.csv
"""
import concurrent.futures as cf, csv, html, pathlib, re, subprocess, sys, tempfile, textwrap
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from PIL import Image, ImageDraw, ImageFont
from tts import speak
import make_slide_videos as sv

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "shorts"
W, H = 1080, 1920
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG, FG, ACC, MUT = (18, 24, 38), (245, 248, 252), (96, 165, 250), (148, 163, 184)
MAX_WORDS = 70


def font(p, s): return ImageFont.truetype(p, s)


def heading(lines):
    """The slide's headline: first line unless it is an all-caps kicker."""
    for l in lines[:3]:
        if not l.isupper() and len(l.split()) >= 2:
            return l.strip(" .")
    return lines[0].strip() if lines else "DATA209"


def candidates(pdf, first, last):
    out = []
    for n in range(first + 2, last - 1):
        lines = sv.page_text(pdf, n)
        words = sv.narration(lines).split()
        if 28 <= len(words) <= MAX_WORDS + 10 and "Study the code" not in " ".join(words):
            out.append((n, len(words)))
    return out


def pick(pdf, first, last, k):
    cands = candidates(pdf, first, last)
    if not cands:
        return []
    span = (last - first + 1) / k
    chosen = []
    for i in range(k):
        lo, hi = first + i * span, first + (i + 1) * span
        seg = [c for c in cands if lo <= c[0] < hi]
        if seg:
            chosen.append(max(seg, key=lambda c: c[1])[0])
    return chosen


def chunks(text, size=6):
    w = text.split()
    return [" ".join(w[i:i + size]) for i in range(0, len(w), size)]


def frame(path, slide_png, group, title, caption):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 16], fill=ACC)
    d.text((40, 70), f"DATA209  ·  {group}", font=font(FB, 38), fill=ACC)
    y = 150
    for line in textwrap.wrap(title, 24)[:3]:
        d.text((40, y), line, font=font(FB, 66), fill=FG); y += 82
    s = Image.open(slide_png).convert("RGB")
    s = s.resize((1000, int(s.height * 1000 / s.width)))
    sy = 470
    d.rectangle([34, sy - 6, 1046, sy + s.height + 6], fill=(255, 255, 255))
    im.paste(s, (40, sy))
    y = sy + s.height + 90
    for line in textwrap.wrap(caption, 22):
        d.text((40, y), line, font=font(FB, 68), fill=FG); y += 90
    d.text((40, H - 90), "@data209eda", font=font(FR, 38), fill=MUT)
    im.save(path)


def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def make_short(args):
    vid, group, pdf, page, idx, tmp = args
    tag = f"{vid}-{idx}"
    lines = sv.page_text(pdf, page)
    title = heading(lines)
    text = sv.narration(lines)
    words = text.split()
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS]).rstrip(",;:") + "."
    wav = tmp / f"{tag}.wav"
    speak(text, wav, 160)
    total = dur(wav)
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-singlefile", "-scale-to-x", "1400", "-scale-to-y", "-1", str(pdf), str(tmp / tag)], check=True)
    parts = chunks(text)
    weights = [len(p) for p in parts]
    lst = tmp / f"{tag}.txt"
    rows = []
    for i, p in enumerate(parts):
        png = tmp / f"{tag}-{i:02d}.png"
        frame(png, tmp / f"{tag}.png", group, title, p)
        rows.append(f"file '{png.name}'\nduration {max(0.4, total * weights[i] / sum(weights)):.3f}\n")
    rows.append(f"file '{(tmp / f'{tag}-{len(parts) - 1:02d}.png').name}'\nduration 1.0\n")
    lst.write_text("".join(rows))
    out = OUT / f"{tag}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-vf", "fps=5,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "33", "-c:a", "aac", "-b:a", "64k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return (tag, group, title, page, dur(out), text)


def main():
    src = pathlib.Path(sys.argv[1]); only = set(sys.argv[2:])
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory() as t, cf.ThreadPoolExecutor(3) as pool:
        tmp = pathlib.Path(t)
        for vid, group, vtitle, pdfname, a, b in sv.VIDEOS:
            if only and vid not in only:
                continue
            pdf = src / pdfname
            total = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
            last = b or total
            k = 2 if (last - a + 1) < 20 else 3
            pages = pick(pdf, a, last, k)
            jobs = [(vid, group, pdf, p, i + 1, tmp) for i, p in enumerate(pages)]
            for r in pool.map(make_short, jobs):
                results.append(r + (vtitle,))
                print(r[0], f"{r[4]:.0f}s", flush=True)
    if only:
        return
    results.sort(key=lambda r: r[0])
    with open(ROOT / "youtube" / "shorts.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["file", "playlist", "title", "description", "seconds"])
        for tag, group, title, page, secs, text, vtitle in results:
            yt = f"{title} | DATA209 EDA #Shorts"[:100]
            desc = (f"{title}. From {vtitle}. DATA209 Advanced Exploratory Data Analysis, Vidyashilp University.\n\n"
                    f"Full video and study site: https://shitalbhatt.github.io/data209-study-materialsnew/\n\n#Shorts #DATA209 #EDA #DataScience #Python")
            w.writerow([f"site/shorts/{tag}.mp4", group, yt, desc, f"{secs:.0f}"])
    page = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>DATA209 Shorts</title><style>body{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem}',
            'h2{margin-top:2rem;border-bottom:1px solid #8884}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}',
            'figure{margin:0}video{width:100%;border-radius:10px;background:#000}figcaption{font-size:.85rem;padding:.3rem 0}</style></head><body>',
            '<p><a href="index.html">&larr; Study guide</a> &middot; <a href="slide-videos.html">Full videos</a></p><h1>DATA209 Shorts</h1>',
            '<p>Quick one-idea videos from the course slides. Voice is synthetic.</p>']
    cur = None
    for tag, group, title, page_no, secs, text, vtitle in results:
        if group != cur:
            if cur: page.append("</div>")
            page.append(f"<h2>{html.escape(group)}</h2><div class='grid'>"); cur = group
        page.append(f'<figure><video controls preload="none" src="shorts/{tag}.mp4"></video><figcaption>{html.escape(title)} ({secs:.0f}s)</figcaption></figure>')
    page.append("</div></body></html>")
    (ROOT / "site" / "shorts.html").write_text("\n".join(page))
    print("total shorts", len(results))


if __name__ == "__main__":
    main()
