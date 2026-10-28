"""Turns the course slide PDFs into narrated videos (one video per lecture or lab) and writes site/slide-videos.html.

Usage: python3 scripts/make_slide_videos.py SRC_DIR
SRC_DIR holds the PDFs named in VIDEOS. Needs poppler (pdftoppm, pdftotext), ffmpeg/ffprobe and espeak-ng (or edge-tts).
Set VOICE=edge for the Indian English female voice (en-IN-NeerjaNeural); run with only a few video ids to rebuild just those.
The narration is the prose on each slide read by the voice; code, tables and numbers stay on screen only.
"""
import concurrent.futures as cf, html, json, pathlib, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tts import speak

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "slide-videos"
W, H = 1280, 720

# (id, group, title, pdf, first page, last page or None)
VIDEOS = [
 ("l01", "Module 1", "Lecture 1: Why we explore before we conclude", "DATA209_Lectures_1-6_Slides_Corrected.pdf", 1, 24),
 ("l02", "Module 1", "Lecture 2: Distributions, summary statistics, robustness", "DATA209_Lectures_1-6_Slides_Corrected.pdf", 25, 39),
 ("l03-04", "Module 1", "Lectures 3-4: Data types and structures", "DATA209_Lectures_1-6_Slides_Corrected.pdf", 40, 49),
 ("l05-06", "Module 1", "Lectures 5-6: Images, audio, dimensionality, ethics", "DATA209_Lectures_1-6_Slides_Corrected.pdf", 50, 68),
 ("p01-02", "Module 1", "Practical 1-2: Framing, loading and describing data", "LAB1_2.pdf", 1, None),
 ("p01-02b", "Module 1", "Practical 1-2: Worked example on California Housing", "California_Housing_EDA_updated.pdf", 1, None),
 ("p03-04", "Module 1", "Practical 3-4: Spotting data types and structure", "dataset-types.pdf", 1, None),
 ("p05-06", "Module 1", "Practical 5-6: Image pixels and audio waveforms", "practical5-6-image-audio.pdf", 1, None),
 ("l07-08", "Module 2", "Lectures 7-8: Non-graphical vs graphical EDA (Superstore)", "L7-8_NonGraphical_vs_Graphical_Superstore.pdf", 1, None),
 ("p07-08", "Module 2", "Practical 7-8: Univariate EDA on Superstore", "P7-8_Univariate_EDA_Superstore.pdf", 1, None),
 ("l09-10", "Module 2", "Lectures 9-10: Bivariate analysis", "L9_10_Bivariate_Analysis_Lecture.pdf", 1, None),
 ("p09-10", "Module 2", "Practical 9-10: Bivariate analysis in Python", "P9_10_Bivariate_Analysis_Lab.pdf", 1, None),
 ("l11-12", "Module 2", "Lectures 11-12: Multivariate analysis, VIF, K-means", "L11_12_Multivariate_Analysis_Lecture.pdf", 1, None),
 ("p11-12", "Module 2", "Practical 11-12: Multivariate analysis lab", "P11_12_Multivariate_Analysis_Lab.pdf", 1, None),
 ("l13-14", "Module 2", "Lectures 13-14: Data visualization, from grammar to storytelling", "L13-14_Data_Visualization_Grammar_to_Storytelling.pdf", 1, None),
 ("l15-16", "Module 3", "Lectures 15-16: Data quality, integration and validation", "L15-16_Data_Quality_Integration_and_Validation.pdf", 1, None),
 ("p15-16", "Module 3", "Practical 15-16: Data quality and integration", "DATA209_Lab_P15-16_Data_Quality_Integration.pdf", 1, None),
 ("l17-18", "Module 3", "Lectures 17-18 and Practical 17-18: Missing values", "Missing_Values_L17-18_P17-18_1_.pdf", 1, None),
 ("l19-20", "Module 3", "Lectures 19-20 and Practical 19-20: Outliers", "Outliers_L19-20_P19-20.pdf", 1, None),
 ("l21-22", "Module 3", "Lectures 21-22 and Practical 21-22: Encoding and imbalance", "DATA209_L21-22_P21-22_Encoding_Imbalance_simple.pdf", 1, None),
 ("l23-24", "Module 4", "Lectures 23-24: Transformation and scaling", "L23_24_Transformation_Scaling_2_.pdf", 1, None),
 ("l25-26", "Module 4", "Lectures 25-26: Feature engineering and selection", "DATA209_L25-26_Feature_Engineering_Selection.pdf", 1, None),
 ("p25-26", "Module 4", "Practical 25-26: Feature engineering and selection lab", "DATA209_P25-26_Lab_Feature_Engineering_Selection.pdf", 1, None),
 ("l27-28", "Module 4", "Lectures 27-28: Dimensionality reduction", "DATA209_L27-28_Dimensionality_Reduction.pdf", 1, None),
 ("p27-28", "Module 4", "Practical 27-28: PCA lab", "DATA209_P27-28_Lab_PCA_2_.pdf", 1, None),
 ("l29-30", "Module 4", "Lectures 29-30: From EDA to a pipeline", "DATA209_L29-30_From_EDA_to_Pipeline.pdf", 1, None),
 ("p29-30", "Module 4", "Practical 29-30: Pipeline lab", "DATA209_P29-30_Lab_Pipeline.pdf", 1, None),
]

FOOTER = re.compile(r"^(advanced exploratory data analysis\s*\|.*|data209\s*[·|].*|page \d+|\d{1,3})$", re.I)
CODEISH = re.compile(r"[\[\]{}_=<>\\]|\w\(|^(import|from|df|sns|plt|print|for|X_|np\.|pd\.)\b")

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)

def page_text(pdf, n):
    t = run(["pdftotext", "-f", str(n), "-l", str(n), str(pdf), "-"], capture_output=True, text=True).stdout
    return [l.strip() for l in t.splitlines() if l.strip()]

def narration(lines):
    keep = []
    for l in lines:
        if FOOTER.match(l) or CODEISH.search(l):
            continue
        letters = sum(c.isalpha() for c in l)
        if letters < 0.6 * len(l) or len(l.split()) < 2:
            continue
        keep.append(l.rstrip("."))
    words = " ".join(keep).replace("\u2212", " minus ").replace("&", " and ").replace("%", " percent").replace("→", " leads to ")
    words = re.sub(r"[^\w\s,.;:'?!$-]", " ", words)
    words = re.sub(r"\s+", " ", words).strip().split()
    text = " ".join(words[:60])
    if len(words) > 60:
        text += "."
    return text or "Study the code and output on this slide."

def written_narration(tag, n):
    """Hand-written explanation for slide n of video tag (scripts/narration/<tag>.json), or None."""
    f = pathlib.Path(__file__).resolve().parent / "narration" / f"{tag}.json"
    if f.exists():
        return json.loads(f.read_text()).get(str(n))
    return None

def dur(f):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout)

def make_segment(args):
    pdf, n, tmp, tag = args
    base = tmp / f"{tag}-{n:03d}"
    run(["pdftoppm", "-f", str(n), "-l", str(n), "-png", "-singlefile", "-scale-to-x", str(W), "-scale-to-y", "-1", str(pdf), str(base)])
    wav, seg = base.with_suffix(".wav"), base.with_suffix(".mp4")
    speak(written_narration(tag, n) or narration(page_text(pdf, n)), wav, 155)
    t = max(4.0, dur(wav) + 1.0)
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "5", "-i", str(base.with_suffix(".png")), "-i", str(wav),
         "-t", f"{t:.2f}", "-af", "apad", "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,fps=5,format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "32", "-c:a", "aac", "-b:a", "56k", "-shortest", str(seg)])
    return seg

def build(vid, pdf, first, last, tmp, pool):
    total = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    last = last or total
    segs = list(pool.map(make_segment, [(pdf, n, tmp, vid) for n in range(first, last + 1)]))
    lst = tmp / f"{vid}.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs))
    out = OUT / f"{vid}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])
    return dur(out), last - first + 1

def main():
    src = pathlib.Path(sys.argv[1])
    only = set(sys.argv[2:])
    if only == {"--page"}:
        write_page(rows_from_disk(src)); return
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory() as t, cf.ThreadPoolExecutor(4) as pool:
        tmp = pathlib.Path(t)
        for vid, group, title, pdf, a, b in VIDEOS:
            if only and vid not in only:
                continue
            secs, n = build(vid, src / pdf, a, b, tmp, pool)
            rows.append((vid, group, title, secs, n))
            print(vid, f"{n} slides, {secs / 60:.1f} min", flush=True)
    if only:
        return
    write_page(rows)


def write_page(rows):
    page = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>DATA209 Lecture and Lab Videos</title><style>body{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;line-height:1.5}',
            'h2{margin-top:2.2rem;border-bottom:1px solid #8884;padding-bottom:.3rem}video{width:100%;border-radius:8px;background:#000}',
            'details{margin:.6rem 0}summary{cursor:pointer;font-weight:600;padding:.3rem 0}small{color:#888;font-weight:400}</style></head><body>',
            '<p><a href="index.html">&larr; Study guide</a> &middot; <a href="videos.html">Short summary videos</a> &middot; <a href="shorts.html">Shorts</a></p>',
            '<h1>DATA209 lecture and lab videos</h1>',
            '<p>Each video explains the real course slides one by one, in detail, with an Indian-English synthetic voice. Pause on a slide to study its code and tables. Slide decks for Lectures 13-14 and 15-16: <a href="decks/L13-14_Data_Visualization_Grammar_to_Storytelling.pptx">L13-14 PPT</a> &middot; <a href="decks/L15-16_Data_Quality_Integration_and_Validation.pptx">L15-16 PPT</a>.</p>']
    cur = None
    for vid, group, title, secs, n in rows:
        if group != cur:
            page.append(f"<h2>{html.escape(group)}</h2>"); cur = group
        page.append(f'<details><summary>{html.escape(title)} <small>({n} slides, {int(secs // 60)}:{int(secs % 60):02d})</small></summary>'
                    f'<video controls preload="none" src="slide-videos/{vid}.mp4"></video></details>')
    page.append("</body></html>")
    (ROOT / "site" / "slide-videos.html").write_text("\n".join(page))


def rows_from_disk(src):
    rows = []
    for vid, group, title, pdfname, a, b in VIDEOS:
        f = OUT / f"{vid}.mp4"
        if not f.exists():
            continue
        total = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(src / pdfname)], capture_output=True, text=True).stdout).group(1))
        rows.append((vid, group, title, dur(f), (b or total) - a + 1))
    return rows


if __name__ == "__main__":
    main()
