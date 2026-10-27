# Practice questions (with answers)

1. **Why shouldn't you test a hypothesis on the rows that suggested it?** It inflates false positives; split, explore on one part, confirm on the held-out part.
2. **Mean > median > mode: which skew?** Right skew.
3. **Which central measure for a skewed column?** Median with IQR.
4. **What does excess kurtosis > 0 mean?** Heavy tails (leptokurtic).
5. **Classify "satisfaction rating 1-5".** Ordinal, discrete.
6. **Classify temperature in Celsius.** Interval, continuous.
7. **Why is a big biased sample dangerous?** Bias doesn't shrink with n.
8. **State the IQR outlier rule.** Outside Q1 - 1.5 IQR or Q3 + 1.5 IQR.
9. **Why can |z| > 3 miss outliers?** Masking: outliers inflate the SD. In small samples |z| can't exceed (n-1)/sqrt(n).
10. **Pearson vs Spearman?** Pearson is linear and outlier-sensitive; Spearman ranks, so it catches monotonic relations robustly.
11. **Give the VIF formula and a threshold.** 1/(1-R^2); above 10 is severe.
12. **Why scale before K-means?** Large-unit features dominate the distance.
13. **Does a K-means cluster number mean anything?** Only after interpreting with groupby.
14. **Four data quality dimensions?** Accuracy, completeness, consistency, validity.
15. **MAR example?** Missing reviews_per_month exactly when number_of_reviews = 0.
16. **Effect of imputation on variance?** It shrinks it.
17. **Outlier due to cap (California 500,001): action?** Flag it (is_capped).
18. **Why log1p?** Reduces right skew and handles zeros.
19. **Dummy variable trap?** Keeping all k dummies; drop one as the baseline.
20. **Why is label encoding risky for nominal data?** It invents an order.
21. **Metric for rare classes?** Recall (and per-class report), not accuracy.
22. **Where is target encoding fit?** Training rows only.
23. **What is data leakage?** Test information used in training, e.g. scaler fit on all data.
24. **Which visual for Cat-Num?** Grouped boxplot.
25. **Pie chart limit?** About 4-5 slices.
