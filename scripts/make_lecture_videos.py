"""Builds one narrated video per lecture pair (L1-2 ... L29-30) and per lab, plus site/videos.html.

Needs Pillow, ffmpeg/ffprobe and espeak-ng. Output: site/videos/*.mp4
Lines starting with "$ " are drawn as code.
"""
import html, pathlib, shutil, subprocess, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "videos"
W, H = 1280, 720
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BG, FG, ACC, MUT, CODE = (18, 24, 38), (240, 244, 250), (96, 165, 250), (148, 163, 184), (134, 239, 172)

# (file id, group, title, [(slide title, [lines], narration)])
V = []
def add(i, g, t, s): V.append((i, g, t, s))

# ---------------- Module 1 ----------------
add("l01-02", "Module 1 lectures", "L1-2 Role of EDA, sampling, summary statistics", [
 ("EDA vs confirmatory", ["Exploratory: what is going on? Hypotheses are generated.", "Confirmatory: is this claim supported? Hypothesis fixed first.", "", "Never test a hypothesis on the rows that suggested it.", "Split first, explore one part, confirm once on the held-out part."],
  "Exploratory analysis asks what is going on, and it generates hypotheses. Confirmatory analysis tests a claim that was fixed before seeing the data. Never test a hypothesis on the same rows that suggested it. Split first, explore on one part, and confirm once on the held out part."),
 ("Five jobs of EDA", ["Sanity: does the file match its documentation?", "Quality: missing, duplicates, impossible values, sentinels", "Structure: shapes, relationships, clusters, trends", "Hypotheses worth testing later", "Modelling decisions: transforms, features, baselines", "", "Pima diabetes: Glucose, BloodPressure, BMI = 0 means missing"],
  "EDA has five jobs. Sanity, quality, structure, hypotheses, and modelling decisions. In the Pima diabetes data, describe shows zeros in glucose, blood pressure and B M I. Those zeros are really missing values."),
 ("Sampling and bias", ["Population -> frame -> sample -> estimate", "Bias: systematic, does not shrink with more data", "Variance: random, shrinks about 1 / sqrt(n)", "Error = Bias^2 + Variance + irreducible noise", "", "Selection, self-selection, survivorship, non-response, undercoverage"],
  "Sampling goes from population to frame to sample to estimate. Bias is systematic and does not shrink with more data. Variance is random and shrinks with the square root of n. A big biased sample is more dangerous than a small random one."),
 ("Shape and summary statistics", ["Right skew: mode < median < mean", "Left skew: mean < median < mode", "Excess kurtosis = kurtosis - 3 (tails, not peak)", "IQR fence: Q1 - 1.5 IQR ... Q3 + 1.5 IQR", "", "Symmetric: mean + SD.   Skewed: median + IQR."],
  "In a right skew the mean is above the median. Excess kurtosis is kurtosis minus three, and it measures the tails, not the peak. Use the I Q R fences to flag outliers. Report mean and standard deviation for symmetric data, and median and I Q R for skewed data."),
])
add("l03-04", "Module 1 lectures", "L3-4 Data types and structures", [
 ("Scales of measurement", ["Nominal: blood type, country. Mode, counts", "Ordinal: satisfaction, education. + median, rank", "Interval: Celsius, year. + mean, no ratios", "Ratio: income, weight, age. Everything", "", "Discrete = counted.  Continuous = measured."],
  "There are four scales. Nominal has no order. Ordinal has order. Interval has equal spacing but no true zero, so no ratios. Ratio has a true zero and allows everything. Discrete data is counted, continuous data is measured."),
 ("Structure and text", ["Structured: fixed schema, tables", "Semi-structured: tags, varying fields (JSON, XML, emails)", "Text pipeline: corpus, document, token, term", "Prep: lowercase, stopwords, stem or lemmatise", "", "Time series = trend + seasonality. Separate them first."],
  "Structured data has a fixed schema. Semi structured data, like J S O N, has tags and varying fields. For text, build a corpus, split into tokens, clean them, and count terms. For time series, separate trend from seasonality before concluding anything."),
])
add("l05-06", "Module 1 lectures", "L5-6 Images, audio, dimensionality, ethics", [
 ("Everything is numbers", ["Image: (height, width) grid, 0 to 255", "Colour adds a third axis: 1024 x 1024 x 3 = 3,145,728", "Audio: 16 kHz x 10 s = 160,000 numbers", "", "Image EDA starts with the pixel histogram", "Spikes at 0 or 255 mean clipping"],
  "Images and audio are just numbers. A colour image of one thousand twenty four by one thousand twenty four has over three million values. Start image analysis with the pixel intensity histogram. Spikes at zero or two fifty five mean clipping."),
 ("Curse of dimensionality", ["10 points per axis needs 10^d points", "Data becomes sparse; nearest ~ farthest", "Data hugs the edges; models overfit", "", "Fixes: feature selection, PCA,", "regularisation, more relevant data"],
  "With d dimensions you need ten to the d points to keep the same density. Data becomes sparse, and nearest and farthest neighbours look alike. Fixes are feature selection, P C A, regularisation, and more relevant data."),
 ("Bias and ethics", ["Bias enters at: world, collection, labelling,", "modelling, deployment (and feeds back)", "", "Ask: Consent, Privacy, Fairness, Consequence", "Split every summary by group", "Check missingness by group; document exclusions"],
  "Bias can enter at every stage, and deployment feeds back into collection. Ask about consent, privacy, fairness and consequence. Split summaries by group, check missingness by group, and document exclusions."),
])

# ---------------- Module 2 ----------------
add("l07-08", "Module 2 lectures", "L7-8 Univariate: non-graphical vs graphical", [
 ("Numbers first, plots second", ["Numerical: mean, median, mode, std, range, IQR,", "skew, kurtosis, isna().sum()", "  plots: histogram, KDE, boxplot, violin", "Categorical: frequency table (counts, %)", "  plots: bar plot, pie (4-5 slices max)"],
  "For a numerical variable, compute the mean, median, spread, skew and kurtosis, then plot a histogram, density and boxplot. For a categorical variable, use a frequency table and a bar plot. Numbers give precision, plots give shape. Check they agree."),
 ("Superstore worked numbers", ["8,399 rows x 21 columns", "Profit: mean $181.18 vs median -$1.50", "Unit Price: skew 14.13, kurtosis 271.17", "Order Quantity: skew -0.02, kurtosis -1.21", "Profit: 1,704 IQR outliers (20.3%)", "50.8% of orders lose money", "Technology avg profit $429 vs Furniture $68"],
  "In the Superstore lab, profit has a mean of one eighty one dollars but a median of minus one fifty. Unit price has a skew of fourteen. Order quantity is close to uniform with no outliers. Over half of orders lose money, and technology earns far more than furniture."),
 ("Lesson", ["Order Quantity: number and plot agree.", "Unit Price: skew warns, boxplot shows the spread", "lives in the outlier dots.", "", "A $27,000 profit order is a real event, not an error."],
  "For order quantity, the number and the plot agree. For unit price the skew is a warning, and only the boxplot shows that the whole spread lives in the outlier dots. A twenty seven thousand dollar order is a real event, not an error."),
])
add("l09-10", "Module 2 lectures", "L9-10 Bivariate: correlation, covariance, cross-tabs", [
 ("Covariance and correlation", ["Cov(X,Y) = sum((x - xbar)(y - ybar)) / (n - 1)", "r = Cov(X,Y) / (sx * sy), between -1 and 1", "Spearman rho: rank first, monotonic, robust", "", "Superstore Discount vs Profit:", "Pearson -0.22, Spearman -0.54"],
  "Covariance gives direction in awkward units. Correlation divides by both standard deviations, so it is scale free. Spearman ranks the data first, so it catches monotonic patterns and resists outliers. For discount versus profit, Pearson is minus point two two and Spearman is minus point five four."),
 ("Which tool for which pair", ["Num-Num: cov, Pearson/Spearman | scatter, heatmap", "Cat-Cat: cross-tab counts, row % | heatmap, stacked bar", "Cat-Num: grouped mean/median/std | boxplot, bar"],
  "Pick the tool by the pair of types. Number with number: correlation and scatter. Category with category: cross tab and heatmap. Category with number: grouped statistics and boxplot."),
 ("Pitfalls", ["Spurious correlation", "Outlier-driven r", "Simpson's paradox", "Tiny cross-tab cells", "", "Similar row % across rows: looks independent", "Different row %: associated (chi-square later)"],
  "Watch for spurious correlation, correlation driven by outliers, Simpson's paradox, and tiny cross tab cells. Always pair r with a scatterplot, and remember correlation is not causation."),
])
add("l11-12", "Module 2 lectures", "L11-12 Multivariate: multicollinearity, VIF, K-means", [
 ("VIF", ["VIF = 1 / (1 - R^2)", "R^2 from regressing one feature on all the others", "1: independent   1-5: acceptable", "5-10: investigate   >10: severe, consider dropping"],
  "The variance inflation factor is one over one minus R squared, where R squared comes from regressing one feature on all the others. Below five is acceptable. Above ten is severe and you should consider dropping a feature."),
 ("K-means", ["1. Choose k    2. Place k centres", "3. Assign each point to the nearest centre", "4. Move centres to the group means. Repeat.", "", "Scale first (StandardScaler): Sales 0-22,638 swamps Discount 0-0.8", "Silhouette: k=2 best (0.504), k=3 more interpretable (0.473)"],
  "K means picks k centres, assigns each point to the nearest one, moves the centres to the group means, and repeats. Scale first, or large unit features dominate. Silhouette helps compare k, but interpretability matters too."),
 ("Reading the clusters (k=3)", ["0: 6,909 rows, avg profit $20.66: everyday orders", "1: 1,068 rows, discount 0.66, profit -$106.79: loss-making", "2: 2,017 rows, avg sales $634, profit $127.77: high value", "", "Clustering describes rows. It does not predict.", "Interpret with groupby(cluster)."],
  "With three clusters we find everyday orders, heavy discount orders that lose money, and high value orders that make money. Clustering describes existing rows, it does not predict. A cluster number means nothing until you interpret it with a group by."),
])
add("l13-14", "Module 2 lectures", "L13-14 Grammar of graphics and storytelling", [
 ("Grammar of graphics", ["data -> aesthetics (x, y, colour, size)", "-> geometry -> scales -> facets -> theme", "", "Most accurate channels:", "position > length > area > colour"],
  "The grammar of graphics maps data to aesthetics, then geometry, scales, facets and a theme. A good plot answers one question and uses the most accurately perceived channel. Position beats length, which beats area, which beats colour."),
 ("Misleading plots", ["Truncated axes", "3-D pies", "Dual axes", "Too many slices", "Colour with no meaning", "Hidden outliers via scale"],
  "Avoid truncated axes, three D pies, dual axes, too many slices, colour with no meaning, and scales that hide outliers."),
 ("Dashboard logic", ["2-3 charts, each tied to a question", "Where do we lose money? -> profit by category", "Why? -> discount vs profit", "Who? -> segment cross-tab", "", "Assignment 1 is built on this storytelling"],
  "A dashboard should have two or three charts, each tied to a question. Where do we lose money? Profit by category. Why? Discount versus profit. Who? A segment cross tab."),
])

# ---------------- Module 3 ----------------
add("l15-16", "Module 3 lectures", "L15-16 Data quality, integration, validation", [
 ("Four dimensions", ["Accuracy: correct vs reality", "Completeness: how much and why missing", "Consistency: one fact, one spelling", "Validity: range, set, format, type, uniqueness", "", "A $10,000 private room is valid but not accurate"],
  "Data quality has four dimensions. Accuracy, completeness, consistency and validity. A ten thousand dollar private room passes validity rules but fails accuracy when compared with its peers."),
 ("Integration steps", ["Match key", "Align schema (rename price_usd to price)", "Resolve conflicts (case-only: keep source A)", "Re-audit", "", "Standardising labels created 300 new exact duplicates."],
  "To integrate sources, match the key, align the schema, resolve conflicts, and then re audit. Standardising labels created three hundred new exact duplicates, so always re audit after every fix."),
 ("NYC Airbnb merge", ["49,895 x 17  ->  48,895 x 16", "700 duplicate rows, 1 duplicate column (price_usd)", "20,573 missing cells; 11 listings at $0", "66 priced > 20x peer median", "log1p on price: skew 19.12 -> 0.55", "Then StandardScaler. Log first, scale second."],
  "In the Airbnb lab, the merge removed seven hundred duplicate rows and one duplicate column. There were over twenty thousand missing cells and eleven listings at zero dollars. A log transform cut the price skew from nineteen to point five five. Log first, scale second."),
])
add("l17-18", "Module 3 lectures", "L17-18 Missing values", [
 ("MCAR, MAR, MNAR", ["MCAR: missing by pure chance. Never proven (Little's test)", "MAR: depends on another observed column", "  Airbnb: all 10,116 missing reviews_per_month", "  rows have number_of_reviews = 0", "MNAR: depends on the missing value itself", "  (high earners hide income). Needs domain knowledge"],
  "Missing completely at random means pure chance, and it can never be proven. Missing at random depends on another observed column. In Airbnb, every missing reviews per month row has zero reviews. Missing not at random depends on the hidden value itself, and needs domain knowledge."),
 ("Imputation compared", ["Observed variance 2.824 (reviews_per_month)", "Mean 1.373: variance kept 79.4%", "Median 0.71: 82.0%", "Regression: 81.9% (R^2 only 0.33)", "KNN k=5: 86.7%, respects MAR"],
  "Mean imputation keeps about seventy nine percent of the variance. Median keeps eighty two. Regression is similar, and K N N keeps almost eighty seven percent while respecting the pattern. Every imputation shrinks variance."),
 ("Detecting missingness", ["$ df.isnull().mean() * 100", "$ pd.crosstab(df.x.isnull(), df.other == 0)", "$ KNNImputer(n_neighbors=5).fit_transform(df[cols])", "", "Scale features before KNN."],
  "Detect missing values with is null, a missingness matrix, and a cross tab against an observed column. For K N N imputation, scale the features first."),
])
add("l19-20", "Module 3 lectures", "L19-20 Outliers", [
 ("Causes and types", ["Causes: entry error, genuine extreme, measurement cap", "(California 500,001), different population", "Types: global, contextual, collective, multivariate", "", "A flag is a question, not a verdict."],
  "Outliers come from entry errors, genuine extremes, measurement caps like California's five hundred thousand and one, or a different population. They can be global, contextual, collective or multivariate."),
 ("Detection", ["Z-score |z| > 3 (bell-shaped only)", "  price limit mean + 3 sd = $873; masking hides outliers", "IQR fences: Q1 69, Q3 175 -> upper $334", "  flags 2,972, about 8x the Z-score count", "Isolation Forest, LOF, DBSCAN (-1 = outlier)"],
  "The Z score rule only suits bell shaped data and suffers from masking. I Q R fences flag about eight times more points on skewed data. For many columns at once, use isolation forest, L O F or D B SCAN."),
 ("Treatment and effect (price)", ["raw: mean 152.72, skew 19.12, R^2 0.12", "IQR capped: mean 132.98, skew 1.02, R^2 0.44", "KNN imputed: mean 124.12, skew 0.79, R^2 0.49", "log1p: skew 0.55", "", "Mistake: fix. Real: cap or log. Limit: flag."],
  "Treating outliers improved the model. R squared rose from point one two to point four nine. Decide by cause. Fix mistakes, cap or log real values, and flag measurement limits. Only removal loses rows."),
])
add("l21-22", "Module 3 lectures", "L21-22 Encoding and imbalanced classes", [
 ("Choosing an encoding", ["No order, few levels: one-hot, drop_first=True", "Has an order: your own map()", "Many levels: frequency or target encoding", "Multi-class target: label encoding"],
  "Use one hot encoding for unordered categories with few levels, and drop one. For ordered levels use your own map. For many levels use frequency or target encoding. Label encoding is for a multi class target."),
 ("Traps", ["Label encoding invents an order for nominal data", "All k dummies = dummy variable trap", "Target encoding: training rows only", "Groups under 10 rows fall back to overall median"],
  "Label encoding invents an order for nominal data. Keeping all dummies causes the dummy variable trap. Target encoding must use training rows only, and small groups fall back to the overall median."),
 ("Imbalance results", ["Airbnb shared rooms: 2.4%, ratio 21.9:1", "Recall 9.5% -> 65% with balanced class weights", "Accuracy 82% -> 73%", "Online Shoppers: 15.6% buy, recall 64% -> 86%", "", "Stratify + class weights + judge by recall"],
  "Shared rooms are only two point four percent of Airbnb listings. Balanced class weights lifted recall from nine percent to sixty five percent, while accuracy fell. That trade is worth it. Stratify, weight, and judge by recall."),
])

# ---------------- Module 4 (from the course plan) ----------------
add("l23-24", "Module 4 lectures", "L23-24 Transform and scale", [
 ("Transform and scale", ["Log, Box-Cox for skew", "Standardisation (z), MinMax, Robust (median / IQR)", "Compare distributions before and after", "", "Slides not yet uploaded: built from the course plan"],
  "Use log or Box Cox transforms for skew. Scale with standardisation, min max, or robust scaling, which uses the median and I Q R. Always compare distributions before and after."),
])
add("l25-26", "Module 4 lectures", "L25-26 Features", [
 ("Feature construction and selection", ["Construction, interaction terms, polynomial features", "Filter: correlation, statistics", "Wrapper: RFE", "Embedded: Lasso, tree importance", "", "Built from the course plan"],
  "Construct new features, interaction terms and polynomial features. Select features with filter methods like correlation, wrapper methods like R F E, or embedded methods like Lasso and tree importance."),
])
add("l27-28", "Module 4 lectures", "L27-28 Dimension reduction", [
 ("Dimension reduction", ["PCA: interpret components and variance explained", "LDA: classification view", "t-SNE and UMAP: visualisation only", "VIF for multicollinearity", "", "Built from the course plan"],
  "P C A reduces dimensions while keeping variance, so interpret the components and the variance explained. L D A takes a classification view. T S N E and U MAP are for visualisation only. Use V I F to check multicollinearity."),
])
add("l29-30", "Module 4 lectures", "L29-30 Pipeline, validation and leakage", [
 ("Pipeline", ["Train/test split, cross-validation", "Leakage: fit scalers and encoders on train only", "Sampling skewed data", "Translate EDA into insight", "", "Ends with the full pipeline notebook and final project"],
  "Split into train and test and use cross validation. Prevent leakage by fitting scalers and encoders on the training data only. Handle skewed data with careful sampling, and translate the analysis into insight for the final project."),
])

# ---------------- Labs ----------------
add("lab-p01-06", "Labs", "Labs P1-6: Pima diabetes first look", [
 ("First look", ["$ df.info(); df.describe(); df.isna().sum()", "$ df.duplicated().sum()", "", "describe() shows Glucose, BloodPressure, BMI = 0", "Zeros here are missing values in disguise."],
  "In the first labs, run info, describe and a missing value count. In the Pima data, describe shows zeros in glucose, blood pressure and B M I. These zeros are really missing values."),
 ("Shape and summaries", ["$ s.skew(), s.kurtosis()   # kurtosis is excess", "$ pd.pivot_table(df, values='x', index='a', aggfunc='mean')", "$ sns.histplot(df.x, kde=True)", "", "Report median + IQR when skewed."],
  "Compute skew and kurtosis, build pivot tables, and plot histograms with density. Report the median and I Q R when data is skewed."),
])
add("lab-p07-14", "Labs", "Labs P7-14: Superstore univariate to clustering", [
 ("Univariate and bivariate code", ["$ sns.histplot(df.x, kde=True); sns.boxplot(x=df.x)", "$ df.cat.value_counts(normalize=True)", "$ df[['a','b']].corr('spearman')", "$ sns.heatmap(df[nums].corr(), annot=True, center=0)", "$ pd.crosstab(df.c1, df.c2, normalize='index')"],
  "Use histograms and boxplots for single numeric columns, and value counts for categories. For pairs, use Spearman correlation, a correlation heatmap, and cross tabs with row percentages."),
 ("VIF and K-means code", ["$ Z = StandardScaler().fit_transform(df[['a','b']])", "$ df['cl'] = KMeans(3, n_init=10, random_state=42).fit_predict(Z)", "$ df.groupby('cl').mean(numeric_only=True)", "$ vif(X.values, i) for i in range(X.shape[1])"],
  "For clustering, scale first, fit K means with a fixed random state, and summarise each cluster with group by. Check V I F for each column."),
 ("What the numbers say", ["Profit mean $181.18 vs median -$1.50", "Discount vs Profit: Pearson -0.22, Spearman -0.54", "k=3: everyday / loss-making / high value", "", "Write interpretation in full sentences tied to your output."],
  "Profit is highly skewed. Discount is negatively related to profit. Three clusters separate everyday, loss making and high value orders. In the exam, write interpretations in full sentences tied to your own output."),
])
add("lab-p15-20", "Labs", "Labs P15-20: Airbnb data quality, missing values, outliers", [
 ("Cleaning code", ["$ df.drop_duplicates(); df.loc[:, ~df.T.duplicated()]", "$ df['c'] = df['c'].str.strip().str.title()", "$ rules = pd.DataFrame({'price>=0': df.price >= 0})", "$ (~rules).sum()   # failures per rule", "", "Re-audit duplicates after every fix."],
  "Drop duplicate rows and columns, standardise text labels, and write validation rules. Count the failures per rule, and re audit duplicates after every fix."),
 ("Missing and outlier code", ["$ df['x'].fillna(df['x'].median())", "$ KNNImputer(n_neighbors=5).fit_transform(df[cols])", "$ q1, q3 = d.quantile(.25), d.quantile(.75); i = q3 - q1", "$ capped = d.clip(q1 - 1.5*i, q3 + 1.5*i, axis=1)", "$ IsolationForest(contamination=.02).fit_predict(X) == -1"],
  "Fill missing values with the median or K N N. Detect outliers with I Q R fences, then cap with clip. Use isolation forest for many columns at once."),
 ("Results", ["49,895 x 17 -> 48,895 x 16", "Price skew 19.12 -> 0.55 with log1p", "R^2 of price model: 0.12 -> 0.49 after treatment", "", "Log first, scale second."],
  "The cleaned Airbnb data has forty eight thousand rows. The log transform cuts skew from nineteen to point five five, and the model R squared improves from point one two to point four nine."),
])
add("lab-p21-22", "Labs", "Labs P21-22: Encoding and imbalanced classes", [
 ("Encoding code", ["$ df['code'] = df['room'].map({'Shared':0,'Private':1,'Entire':2})", "$ pd.get_dummies(df, columns=['borough'], drop_first=True, dtype=int)", "$ df['freq'] = df.area.map(df.area.value_counts(normalize=True))"],
  "Map ordered categories yourself, one hot encode unordered ones with drop first, and use frequency encoding for high cardinality columns."),
 ("Imbalance code", ["$ train_test_split(X, y, test_size=.2, random_state=42, stratify=y)", "$ DecisionTreeClassifier(max_depth=5, class_weight='balanced')", "$ classification_report(y_test, pred)   # check recall per class", "", "Shared-room recall 9.5% -> 65%"],
  "Split with stratify, fit a tree with balanced class weights, and read the classification report. Check recall for the rare class. Shared room recall improved from nine percent to sixty five percent."),
])


def font(p, s): return ImageFont.truetype(p, s)

def draw(path, title, lines, idx, n):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, H], fill=ACC)
    d.text((70, 50), title, font=font(FB, 46 if len(title) < 34 else 38), fill=ACC)
    d.line([70, 120, W - 70, 120], fill=MUT, width=2)
    y = 150
    for l in lines:
        if l.startswith("$ "):
            for w in textwrap.wrap(l[2:], 70) or [""]:
                d.text((70, y), w, font=font(FM, 27), fill=CODE); y += 44
        else:
            for w in textwrap.wrap(l, 66) or [""]:
                d.text((70, y), w, font=font(FR, 32), fill=FG); y += 48
    d.text((W - 130, H - 50), f"{idx}/{n}", font=font(FR, 24), fill=MUT)
    im.save(path)

def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)

def build(vid, title, slides, tmp):
    segs = []
    for i, (st, lines, narr) in enumerate(slides, 1):
        png, wav, seg = tmp / f"{vid}-{i}.png", tmp / f"{vid}-{i}.wav", tmp / f"{vid}-{i}.mp4"
        draw(png, st, lines, i, len(slides))
        subprocess.run(["espeak-ng", "-v", "en-us", "-s", "150", "-w", str(wav), narr], check=True)
        t = dur(wav) + 1.2
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "5", "-i", str(png), "-i", str(wav),
                        "-t", f"{t:.2f}", "-af", "apad", "-vf", "fps=10,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                        "-tune", "stillimage", "-crf", "30", "-c:a", "aac", "-b:a", "64k", "-shortest", str(seg)], check=True)
        segs.append(seg)
    lst = tmp / f"{vid}.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs))
    out = OUT / f"{vid}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(out)], check=True)
    return dur(out)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    rows = []
    try:
        for vid, group, title, slides in V:
            secs = build(vid, title, slides, tmp)
            rows.append((vid, group, title, secs))
            print(vid, f"{secs:.0f}s")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    page = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>DATA209 Videos</title><style>body{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;line-height:1.5}',
            'h2{margin-top:2.2rem;border-bottom:1px solid #8884;padding-bottom:.3rem}video{width:100%;border-radius:8px;background:#000}',
            'details{margin:.6rem 0}summary{cursor:pointer;font-weight:600;padding:.3rem 0}small{color:#888;font-weight:400}</style></head><body>',
            '<p><a href="index.html">&larr; Study guide</a></p><h1>DATA209 lecture and lab videos</h1>',
            '<p>Short narrated slide videos (synthetic voice). Module 4 videos are built from the course plan because the lecture slides were not available.</p>',
            '<h2>Full revision video</h2><video controls preload="none" src="data209-revision.mp4"></video>']
    cur = None
    for vid, group, title, secs in rows:
        if group != cur:
            page.append(f"<h2>{html.escape(group)}</h2>"); cur = group
        page.append(f'<details><summary>{html.escape(title)} <small>({int(secs // 60)}:{int(secs % 60):02d})</small></summary>'
                    f'<video controls preload="none" src="videos/{vid}.mp4"></video></details>')
    page.append("</body></html>")
    (ROOT / "site" / "videos.html").write_text("\n".join(page))

if __name__ == "__main__":
    main()
