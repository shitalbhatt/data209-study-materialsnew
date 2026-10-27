(function () {
  // theme toggle
  var root = document.documentElement;
  try { var saved = localStorage.getItem('theme'); if (saved) root.setAttribute('data-theme', saved); } catch (e) {}
  document.getElementById('theme').addEventListener('click', function () {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  // code tabs
  var tabs = document.querySelectorAll('#codetabs button');
  tabs.forEach(function (b) {
    b.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.toggle('on', x === b); });
      document.querySelectorAll('.pane').forEach(function (p) { p.classList.toggle('on', p.id === b.dataset.t); });
    });
  });

  // active nav link
  var links = document.querySelectorAll('#nav a');
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        links.forEach(function (l) { l.classList.toggle('on', l.getAttribute('href') === '#' + e.target.id); });
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  document.querySelectorAll('main section[id]').forEach(function (s) { io.observe(s); });

  // quiz
  var Q = [
    ['Online Shoppers sessions are logged only for people who visited. Which bias limits claims about non-visitors?', ['Undercoverage / coverage error', 'Variance', 'Overfitting', 'Kurtosis'], 0, 'The sampling frame contains no row for someone who never visited, so it cannot explain why non-visitors stayed away.'],
    ['More data most directly reduces which error?', ['Bias', 'Variance (random error)', 'Both equally', 'Neither'], 1, 'Variance shrinks roughly like 1/√n. Bias is systematic and only better design fixes it.'],
    ['A right-skewed column has which ordering?', ['mean < median < mode', 'mode < median < mean', 'all equal', 'median < mode < mean'], 1, 'The long right tail drags the mean up, so mode < median < mean.'],
    ['Excess kurtosis of +4 means:', ['Thin tails', 'Heavy tails, outliers more likely', 'A sharper peak only', 'Symmetric data'], 1, 'Kurtosis measures tail weight. Excess kurtosis > 0 is leptokurtic.'],
    ['Temperature in °C is which scale?', ['Nominal', 'Ordinal', 'Interval', 'Ratio'], 2, 'Equal gaps but zero is not "none", so you cannot say "twice as hot".'],
    ['The usual order for text prep is:', ['token → document → corpus', 'corpus → document → token → term', 'term → corpus → token', 'document → term → corpus'], 1, 'Corpus is the collection, documents are items in it, tokens are the pieces, terms the unique vocabulary.'],
    ['Why does the curse of dimensionality hurt k-NN?', ['Too few rows of text', 'Distances become similar, so "nearest" loses meaning', 'It removes outliers', 'It makes data symmetric'], 1, 'In high dimensions the nearest-to-farthest distance ratio approaches 1.'],
    ['Discount vs Profit is −0.22 by Pearson and −0.54 by Spearman. The gap suggests:', ['Perfect linearity', 'A monotonic but non-linear/outlier-affected relationship', 'No relationship', 'A coding error'], 1, 'Spearman uses ranks, so it is robust to the extreme points that flattened the straight-line number.'],
    ['A VIF of 12 for a feature means:', ['No issue', 'Moderate', 'Severe multicollinearity, consider dropping', 'It is a target variable'], 2, 'VIF = 1/(1−R²). Above 10 is severe.'],
    ['Why scale features before K-means?', ['To make k smaller', 'So the largest-range feature does not dominate distance', 'To remove outliers', 'To get labels'], 1, 'Sales in dollars would swamp Discount in 0–0.8 without standardisation.'],
    ['All 10,116 missing reviews_per_month rows have number_of_reviews = 0. This is:', ['MCAR', 'MAR', 'MNAR', 'Not missing data'], 1, 'Missingness is explained by another observed column, the definition of MAR.'],
    ['Which imputation kept the most variance in the lab?', ['Mean', 'Median', 'Regression', 'KNN (86.7%)'], 3, 'KNN fills each row from similar rows, not one constant.'],
    ['Why can Z-score miss outliers in long-tailed data?', ['It needs labels', 'Outliers inflate the std, which hides them (masking)', 'It only works on categories', 'It always flags too many'], 1, 'Three $10,000 homes pushed the price limit up to $873, hiding $334–$873 outliers that IQR catches.'],
    ['A house value stored at exactly 500,001 is best handled by:', ['Deleting everything above 500,000', 'Flagging it as capped (true value unknown)', 'Z-score removal', 'One-hot encoding'], 1, 'It is a measurement limit. Mark it rather than treat it as a real value.'],
    ['Standardising labels with .str.title() then showing 300 new duplicates teaches:', ['Duplicates are random', 'Re-audit after every cleaning step', 'Never standardise', 'Use label encoding'], 1, '"brooklyn" and "Brooklyn" hid exact duplicates until casing was fixed.'],
    ['For borough (5 unlabelled categories) in a linear model use:', ['Label encoding', 'One-hot with drop_first=True', 'Ordinal map', 'Leave as text'], 1, 'Label encoding invents an order. Dropping one dummy avoids the dummy variable trap.'],
    ['Shared rooms are 2.4% of listings. A model that always predicts "Entire home" is 52% accurate. The right fix is to:', ['Trust accuracy', 'Use stratify, class weights and check recall per class', 'Drop shared rooms', 'Use label encoding'], 1, 'Accuracy hides the rare class. Class weights lifted shared-room recall from 9.5% to 65%.'],
    ['Target encoding must be computed on:', ['The whole dataset', 'Training rows only', 'Test rows only', 'Any rows'], 1, 'Using all rows leaks the answer into the features (data leakage).'],
    ['The pre-exam handout says an answer earns full marks when:', ['Code alone runs', 'Concept, code/output and dataset-specific interpretation are all right', 'It is long', 'It cites a textbook'], 1, 'Half marks if only the explanation or only the code is right.'],
    ['You found 4000 in a column of values near 250–310. The correct first step is to:', ['Delete it silently', 'Ask why: error, rare real value, or different population', 'Replace with mean', 'Ignore it'], 1, 'A flag is a question, not a verdict. Deleting silently is one of the six costly mistakes.']
  ];
  var i = 0, score = 0, answered = false;
  var card = document.getElementById('qcard'), next = document.getElementById('qnext');
  var prog = document.getElementById('qprog'), sc = document.getElementById('qscore');

  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  function render() {
    if (i >= Q.length) {
      card.innerHTML = '<p class="q">Finished: ' + score + ' / ' + Q.length + '</p><p class="note">' +
        (score / Q.length >= 0.8 ? 'Strong. Practise the cheat-sheet code on a fresh dataset next.' :
          'Revisit the modules where you slipped, then restart the quiz.') + '</p>';
      next.disabled = true; prog.textContent = 'Done'; return;
    }
    answered = false; next.disabled = true;
    var q = Q[i];
    prog.textContent = 'Question ' + (i + 1) + ' of ' + Q.length;
    sc.textContent = 'Score ' + score;
    card.innerHTML = '<p class="q">' + esc(q[0]) + '</p>' +
      q[1].map(function (o, k) { return '<button class="opt" data-k="' + k + '">' + esc(o) + '</button>'; }).join('') +
      '<div id="why"></div>';
    card.querySelectorAll('.opt').forEach(function (b) {
      b.addEventListener('click', function () { pick(+b.dataset.k); });
    });
  }

  function pick(k) {
    if (answered) return;
    answered = true;
    var q = Q[i], opts = card.querySelectorAll('.opt');
    opts.forEach(function (b, n) {
      b.disabled = true;
      if (n === q[2]) b.classList.add('right');
      else if (n === k) b.classList.add('wrong');
    });
    if (k === q[2]) score++;
    sc.textContent = 'Score ' + score;
    document.getElementById('why').innerHTML = '<div class="why">' + esc(q[3]) + '</div>';
    next.disabled = false;
    next.textContent = i === Q.length - 1 ? 'See result' : 'Next';
  }

  next.addEventListener('click', function () { i++; render(); });
  document.getElementById('qreset').addEventListener('click', function () { i = 0; score = 0; next.textContent = 'Next'; render(); });
  render();
})();
