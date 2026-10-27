# Module 2: Core advanced EDA (L7-14)

## Univariate (Superstore, 8,399 x 21)
Numbers first, plots second, then check they agree. Profit mean $181.18 vs median -$1.50; Unit Price skew 14.13, kurtosis 271.17; Order Quantity is near uniform; 50.8% of orders lose money.

## Bivariate
Cov(X,Y) = sum((x-xbar)(y-ybar))/(n-1); r = Cov/(sx sy). Spearman ranks first. Discount vs Profit: Pearson -0.22, Spearman -0.54. Pitfalls: spurious correlation, outlier-driven r, Simpson's paradox, tiny cross-tab cells.

| Pair | Summary | Visual |
|---|---|---|
| Num-Num | cov, Pearson/Spearman | scatter, pairplot, heatmap |
| Cat-Cat | cross-tab | heatmap, stacked bar |
| Cat-Num | grouped mean/median | boxplot, bar |

## Multivariate
VIF = 1/(1-R^2): 1 independent, 1-5 fine, 5-10 investigate, >10 severe. K-means: scale first; k=3 gave everyday / heavy-discount loss / high-value clusters.

## Graphics and storytelling
Grammar: data, aesthetics, geometry, scales, facets, theme. Position > length > area > colour. Avoid truncated axes, 3-D pies, dual axes.
