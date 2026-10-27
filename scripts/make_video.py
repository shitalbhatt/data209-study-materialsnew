"""Builds video/data209-revision.mp4 from the slide list below (silent, on-screen text)."""
import subprocess, textwrap, pathlib
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).resolve().parent.parent / "video"
SL = OUT / "slides"; SL.mkdir(parents=True, exist_ok=True)
W, H = 1280, 720
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG, FG, ACC, MUT = (18, 24, 38), (240, 244, 250), (96, 165, 250), (148, 163, 184)

SLIDES = [
 ("DATA209", ["Advanced Exploratory Data Analysis", "", "Revision video: 4 modules, one idea per slide"], "title"),
 ("EDA vs confirmatory", ["EDA asks: what is going on? (hypotheses generated)", "Confirmatory asks: is this claim supported? (fixed beforehand)", "", "Never test a hypothesis on the rows that suggested it.", "Split first, explore one part, confirm once on the held-out part."], ""),
 ("Sampling and bias", ["Population -> frame -> sample -> estimate", "Bias is systematic and does not shrink with more data.", "Variance is random and shrinks about 1/sqrt(n).", "", "Big and biased is worse than small and random."], ""),
 ("Shape and summary statistics", ["Right skew: mode < median < mean", "Left skew: mean < median < mode", "Excess kurtosis = kurtosis - 3 (tails, not peak)", "IQR fence: Q1 - 1.5 IQR ... Q3 + 1.5 IQR", "", "Symmetric: mean + SD.  Skewed: median + IQR."], ""),
 ("Scales of measurement", ["Nominal: mode, counts", "Ordinal: + median, rank", "Interval: + mean, no ratios", "Ratio: everything, including ratios", "", "Discrete = counted.  Continuous = measured."], ""),
 ("Curse of dimensionality", ["10 points per axis needs 10^d points", "Data gets sparse, distances concentrate", "Models overfit, plots stop working", "", "Fixes: feature selection, PCA, regularisation"], ""),
 ("Univariate EDA (Superstore)", ["Numbers first, plots second, then check they agree", "Profit mean $181.18 vs median -$1.50", "Unit Price skew 14.13: the spread lives in the outliers", "50.8% of orders lose money", "", "Outliers like a $27,000 order are real events"], ""),
 ("Bivariate EDA", ["Pearson r = Cov / (sx sy), in [-1, 1]", "Spearman ranks first: monotonic, outlier-robust", "Discount vs Profit: Pearson -0.22, Spearman -0.54", "", "Always pair r with a scatterplot.", "Correlation is not causation."], ""),
 ("Multivariate EDA", ["VIF = 1 / (1 - R^2):  >5 investigate, >10 severe", "K-means: scale first, then pick k with silhouette + sense", "k=3 clusters: everyday, heavy-discount losses, high value", "", "A cluster number means nothing until you interpret it."], ""),
 ("Grammar of graphics", ["data -> aesthetics -> geometry -> scales -> facets -> theme", "Best channel: position > length > area > colour", "Avoid truncated axes, 3-D pies, dual axes", "", "One plot answers one question."], ""),
 ("Data quality: four dimensions", ["Accuracy: correct vs reality", "Completeness: how much, and why, is missing", "Consistency: one fact, one spelling", "Validity: range, set, format, type, uniqueness", "", "Re-audit after every fix."], ""),
 ("Missing values", ["MCAR: pure chance (can't be proven)", "MAR: depends on another observed column", "MNAR: depends on the missing value itself", "", "Mean/median keep ~80% of variance; KNN keeps ~87%", "Every imputation shrinks variance."], ""),
 ("Outliers", ["Mistake: fix/remove.  Real: cap or log.  Limit: flag.", "Z-score |z|>3 only suits bell shapes (masking!)", "IQR fences flag far more on skewed data", "Isolation Forest, LOF, DBSCAN for many columns", "", "Airbnb price skew: 19.12 -> 0.55 with log1p"], ""),
 ("Encoding and imbalance", ["No order, few levels: one-hot, drop_first=True", "Has an order: map() it yourself", "Many levels: frequency / target encoding (train only)", "", "Imbalance: stratify + class weights + judge by recall"], ""),
 ("Module 4: transform and pipeline", ["Log / Box-Cox for skew; z, MinMax, Robust scaling", "Selection: filter, wrapper (RFE), embedded (Lasso)", "PCA for structure; t-SNE/UMAP for visualisation only", "Fit scalers and encoders on train only (no leakage)"], ""),
 ("Exam day", ["2 hours, 25 questions x 1 mark, Modules 1 and 2", "One A4 sheet, one side. Submit one executed notebook.", "Interpretation in full sentences, tied to YOUR output", "~4-5 minutes per question: skip and return"], ""),
 ("Good luck", ["Full notes, quiz and cheat sheet are in this repo", "", "github.com/shitalbhatt/data209-study-materials"], "title"),
]

def font(p, s): return ImageFont.truetype(p, s)

for i, (title, lines, kind) in enumerate(SLIDES, 1):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, H], fill=ACC)
    if kind == "title":
        d.text((90, 240), title, font=font(B, 84), fill=FG)
        y = 360
        for l in lines: d.text((90, y), l, font=font(R, 34), fill=ACC if l else FG); y += 52
    else:
        d.text((70, 60), title, font=font(B, 52), fill=ACC)
        d.line([70, 135, W - 70, 135], fill=MUT, width=2)
        y = 175
        for l in lines:
            for w in (textwrap.wrap(l, 62) or [""]):
                d.text((70, y), w, font=font(R, 36), fill=FG); y += 52
    d.text((W - 150, H - 50), f"{i}/{len(SLIDES)}", font=font(R, 24), fill=MUT)
    im.save(SL / f"s{i:02d}.png")

# 6 seconds per slide
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1/6", "-i", str(SL / "s%02d.png"),
                "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-movflags", "+faststart",
                str(OUT / "data209-revision.mp4")], check=True)
print("done", len(SLIDES), "slides")
