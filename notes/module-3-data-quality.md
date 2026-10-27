# Module 3: Data quality and anomaly management (L15-22)

- Quality dimensions: accuracy, completeness, consistency, validity. Re-audit after every fix.
- NYC Airbnb merge: 49,895x17 -> 48,895x16; 700 duplicate rows; log1p on price takes skew 19.12 -> 0.55.
- Missingness: MCAR / MAR / MNAR. Imputation always shrinks variance (mean 79%, median 82%, KNN 87% retained).
- Outliers: mistake -> fix/remove; real -> cap/log; limit -> flag. Z-score suffers masking; IQR flags more on skewed data; Isolation Forest, LOF, DBSCAN for multivariate.
- Encoding: one-hot (drop_first), ordinal map, frequency/target encoding (train only).
- Imbalance: stratify, class weights, judge by recall (shared-room recall 9.5% -> 65%).
