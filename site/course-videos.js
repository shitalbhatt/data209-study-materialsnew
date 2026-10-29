(function () {
  'use strict';
  var root = document.documentElement;
  try { var saved = localStorage.getItem('theme'); if (saved) root.setAttribute('data-theme', saved); } catch (e) {}
  document.getElementById('theme').addEventListener('click', function () {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  var KINDS = ['All', 'Lecture', 'Lab', 'Revision', 'Guide'];
  var state = { kind: 'All', q: '' };
  var data = null;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function ytUrl(id) { return 'https://www.youtube.com/watch?v=' + encodeURIComponent(id); }
  function pretty(d) {
    var p = d.split('-'); var m = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return parseInt(p[2], 10) + ' ' + m[parseInt(p[1], 10) - 1] + ' ' + p[0];
  }
  function today() { return new Date().toISOString().slice(0, 10); }
  function status(pub) { return pub <= today() ? 'coming soon' : 'scheduled for ' + pretty(pub); }
  function secs(m) { var p = m.split(':'); return parseInt(p[0], 10) * 60 + parseInt(p[1], 10); }

  function media(v) {
    var box = el('div', { 'class': 'cv-media' });
    box.appendChild(el('img', { src: v.thumb, alt: v.title, loading: 'lazy' }));
    box.appendChild(el('span', { 'class': 'cv-dur', text: v.minutes }));
    if (v.file || v.youtubeId) {
      var btn = el('button', { 'class': 'cv-play', type: 'button', 'aria-label': 'Play ' + v.title }, [el('span', { text: '\u25B6' })]);
      btn.addEventListener('click', function () {
        var player;
        if (v.file) {
          player = el('video', { controls: '', autoplay: '', playsinline: '', preload: 'auto', poster: v.thumb, src: v.file });
        } else {
          player = el('iframe', { src: 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(v.youtubeId) + '?autoplay=1&rel=0',
            title: v.title, allow: 'autoplay; encrypted-media; picture-in-picture', allowfullscreen: '' });
        }
        box.textContent = ''; box.appendChild(player);
      });
      box.appendChild(btn);
    }
    return box;
  }

  function card(v) {
    var body = el('div', { 'class': 'cv-body' }, [
      el('span', { 'class': 'cv-kind', text: v.kind + ' · ' + v.code.replace('_', ' ') }),
      el('h3', { text: v.title }),
      el('p', { 'class': 'cv-sum', text: 'You will learn ' + v.summary + '.' })
    ]);
    if (v.chapters && v.chapters.length) {
      var ol = el('ol');
      v.chapters.forEach(function (c) { ol.appendChild(el('li', {}, [el('b', { text: c[0] }), document.createTextNode(c[1])])); });
      body.appendChild(el('details', {}, [el('summary', { text: 'Chapters (' + v.chapters.length + ')' }), ol]));
    }
    var act = el('div', { 'class': 'cv-actions' });
    if (v.file) act.appendChild(el('a', { 'class': 'cv-dl', href: v.file, download: '', text: 'Download MP4' }));
    act.appendChild(v.youtubeId
      ? el('a', { 'class': 'cv-btn', href: ytUrl(v.youtubeId), target: '_blank', rel: 'noopener', text: 'Watch on YouTube' })
      : el('span', { 'class': 'cv-soon', text: 'YouTube: ' + status(v.publish).replace(/^./, function (c) { return c.toLowerCase(); }) }));
    if (v.short) {
      var s = v.short;
      var sd = el('details', { 'class': 'cv-short' }, [el('summary', { text: 'Short (' + s.minutes + '): ' + s.title })]);
      var holder = el('div', { 'class': 'cv-shortbox' });
      sd.appendChild(holder);
      sd.addEventListener('toggle', function () {
        if (sd.open && !holder.firstChild && s.file) holder.appendChild(el('video', { controls: '', playsinline: '', preload: 'metadata', src: s.file }));
        if (!sd.open) { var vid = holder.querySelector('video'); if (vid) vid.pause(); }
      });
      if (s.youtubeId) sd.appendChild(el('a', { href: 'https://www.youtube.com/shorts/' + encodeURIComponent(s.youtubeId), target: '_blank', rel: 'noopener', text: 'Watch this Short on YouTube' }));
      act.appendChild(sd);
    }
    body.appendChild(act);
    return el('article', { 'class': 'cv-card' }, [media(v), body]);
  }

  function match(v) {
    if (state.kind !== 'All' && v.kind !== state.kind) return false;
    if (!state.q) return true;
    var hay = (v.title + ' ' + v.summary + ' ' + v.code + ' ' + (v.short ? v.short.title : '')).toLowerCase();
    return state.q.split(/\s+/).every(function (w) { return hay.indexOf(w) !== -1; });
  }

  function render() {
    var list = document.getElementById('cv-list'); list.textContent = '';
    var shown = 0;
    data.playlists.forEach(function (p) {
      var vs = data.videos.filter(function (v) { return v.playlist === p.title && match(v); });
      if (!vs.length) return;
      shown += vs.length;
      var h2 = el('h2', { text: p.title });
      if (p.url) h2.appendChild(el('a', { href: p.url, target: '_blank', rel: 'noopener', text: 'Open playlist on YouTube ↗' }));
      var grid = el('div', { 'class': 'cv-grid' }); vs.forEach(function (v) { grid.appendChild(card(v)); });
      list.appendChild(el('section', { 'class': 'cv-sec' }, [h2, grid]));
    });
    if (!shown) list.appendChild(el('p', { 'class': 'cv-empty', text: 'No videos match your search.' }));
  }

  function stats() {
    var total = data.videos.reduce(function (a, v) { return a + secs(v.minutes); }, 0);
    var live = data.videos.filter(function (v) { return v.youtubeId; }).length;
    var box = document.getElementById('cv-stats');
    [[data.videos.length, 'videos'], [data.videos.filter(function (v) { return v.short; }).length, 'Shorts'],
     [(total / 3600).toFixed(1) + ' h', 'of teaching'], [data.videos.filter(function (v) { return v.file; }).length + '/' + data.videos.length, 'playable here'], [live + '/' + data.videos.length, 'on YouTube']].forEach(function (s) {
      box.appendChild(el('div', {}, [el('b', { text: String(s[0]) }), el('span', { text: s[1] })]));
    });
  }

  function chips() {
    var box = document.getElementById('cv-chips');
    KINDS.forEach(function (k) {
      var b = el('button', { type: 'button', 'aria-pressed': k === state.kind ? 'true' : 'false', text: k === 'All' ? 'All' : k + 's' });
      b.addEventListener('click', function () {
        state.kind = k; Array.prototype.forEach.call(box.children, function (c) { c.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true'); render();
      });
      box.appendChild(b);
    });
    document.getElementById('cv-q').addEventListener('input', function (e) { state.q = e.target.value.trim().toLowerCase(); render(); });
  }

  fetch('course-videos/videos.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    data = d; stats(); chips(); render();
  }).catch(function () {
    document.getElementById('cv-list').textContent = 'Could not load the video list. Please refresh the page.';
  });
})();
