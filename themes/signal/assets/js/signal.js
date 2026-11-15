/* Signal theme — interactions: scroll-reveal, reading progress, TOC active state, mobile menu */
(function () {
  'use strict';

  /* ---- mobile menu ---- */
  var header = document.querySelector('header.site');
  var menuBtn = header && header.querySelector('.menu-btn');
  function setMenu(open) {
    if (!header || !menuBtn) return;
    header.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  document.addEventListener('click', function (e) {
    if (e.target.closest('.menu-btn')) setMenu(!header.classList.contains('open'));
    else if (e.target.closest('.navlinks a')) setMenu(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header && header.classList.contains('open')) {
      setMenu(false);
      menuBtn.focus();
    }
  });

  /* ---- переключатель темы: выбор сохраняется, без выбора — системная тема ---- */
  (function () {
    var btn = document.querySelector('.theme-btn');
    if (!btn) return;
    var root = document.documentElement;
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    function current() { return root.getAttribute('data-theme') || (mq.matches ? 'dark' : 'light'); }
    function sync() {
      var dark = current() === 'dark';
      btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
      btn.setAttribute('aria-label', dark ? 'Светлая тема' : 'Тёмная тема');
    }
    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      sync();
    });
    if (mq.addEventListener) mq.addEventListener('change', sync);
    sync();
  })();

  /* ---- copy article link ---- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.copy-link');
    if (!btn) return;
    var status = btn.parentNode.querySelector('.copy-status');
    function say(t) { if (status) { status.textContent = t; setTimeout(function () { status.textContent = ''; }, 2500); } }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(location.href).then(
        function () { say('Ссылка скопирована'); },
        function () { say('Не удалось скопировать ссылку'); });
    } else {
      say('Скопируйте адрес из строки браузера');
    }
  });

  /* ---- scroll reveal (home & lists) ---- */
  (function reveal() {
    document.querySelectorAll('.sec-head, .about-grid, .factbox, .hero-in > div, .svc-foot, .page-hero .inner, .gal-intro')
      .forEach(function (el) { el.classList.add('reveal'); });
    document.querySelectorAll('.svc-grid, .room-grid, .post-grid, .term-cloud, .album-grid, .gal-grid')
      .forEach(function (el) { el.classList.add('stagger'); });

    var targets = document.querySelectorAll('.reveal, .stagger');
    if (!targets.length) return;
    if (!('IntersectionObserver' in window) ||
        window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      targets.forEach(function (el) { el.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el) { io.observe(el); });
  })();

  /* ---- reading progress + TOC active (article) ---- */
  (function article() {
    var bar = document.getElementById('progress');
    var tocLinks = [].slice.call(document.querySelectorAll('.toc nav a[href^="#"], .toc-inline nav a[href^="#"]'));
    if (!bar && !tocLinks.length) return;

    var sections = tocLinks.map(function (a) {
      try { return document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))); }
      catch (err) { return null; }
    });

    // Раз в кадр: сначала все чтения раскладки, потом записи.
    // Индикатор двигается через transform, без пересчёта раскладки.
    var queued = false;
    function update() {
      queued = false;
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var ratio = max > 0 ? Math.min(1, h.scrollTop / max) : 0;
      var cur = -1;
      for (var i = 0; i < sections.length; i++) {
        if (sections[i] && sections[i].getBoundingClientRect().top < 140) cur = i;
      }
      if (bar) bar.style.transform = 'scaleX(' + ratio + ')';
      tocLinks.forEach(function (a, i) { a.classList.toggle('active', i === cur); });
    }
    function onScroll() {
      if (!queued) { queued = true; requestAnimationFrame(update); }
    }
    document.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
  })();
})();

/* ---- gallery lightbox ---- */
(function () {
  var grid = document.getElementById('gal-grid');
  var box = document.getElementById('lb');
  if (!grid || !box) return;

  var items = [].slice.call(grid.querySelectorAll('.gal-item'));
  if (!items.length) return;

  // картинку создаём здесь, чтобы в HTML не было <img> без src
  var img = document.createElement('img');
  img.className = 'lb-img';
  img.alt = '';
  box.querySelector('.lb-fig').prepend(img);
  var cap = box.querySelector('.lb-cap');
  var count = box.querySelector('.lb-count');
  var btnX = box.querySelector('.lb-x');
  var btnPrev = box.querySelector('.lb-prev');
  var btnNext = box.querySelector('.lb-next');
  var i = 0;
  var lastFocus = null;

  function show(idx) {
    i = (idx + items.length) % items.length;
    var a = items[i];
    var inner = a.querySelector('img');
    img.src = a.getAttribute('href');
    img.alt = a.getAttribute('data-alt') || (inner && inner.alt) || '';
    cap.textContent = a.getAttribute('data-caption') || '';
    count.textContent = (i + 1) + ' / ' + items.length;
  }

  function open(idx) {
    // после закрытия вернуть фокус на кадр, с которого открыли просмотр
    lastFocus = items[idx];
    show(idx);
    box.hidden = false;
    document.body.classList.add('lb-open');
    btnX.focus();
  }

  function close() {
    box.hidden = true;
    document.body.classList.remove('lb-open');
    img.removeAttribute('src');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  grid.addEventListener('click', function (e) {
    var a = e.target.closest('.gal-item');
    if (!a || !grid.contains(a)) return;
    e.preventDefault();
    open(items.indexOf(a));
  });

  btnX.addEventListener('click', close);
  btnPrev.addEventListener('click', function () { show(i - 1); });
  btnNext.addEventListener('click', function () { show(i + 1); });
  img.addEventListener('click', function () { show(i + 1); });
  box.addEventListener('click', function (e) { if (e.target === box) close(); });

  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'Tab') {
      // держим фокус внутри окна просмотра (aria-modal)
      var f = [btnX, btnPrev, btnNext];
      var at = f.indexOf(document.activeElement);
      e.preventDefault();
      f[(at + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
    }
    else if (e.key === 'ArrowLeft') show(i - 1);
    else if (e.key === 'ArrowRight') show(i + 1);
  });
})();

/* ---- email-ссылки: адрес собирается на клиенте (защита от спам-ботов) ---- */
(function () {
  document.querySelectorAll('a.js-mail').forEach(function (a) {
    var u = a.getAttribute('data-user'), h = a.getAttribute('data-host');
    if (u && h) a.setAttribute('href', 'mailto:' + u + '@' + h);
  });
})();

/* ---- поиск по сайту: индекс /search.json, поиск в браузере ---- */
(function () {
  var input = document.getElementById('q');
  if (!input) return;
  var list = document.getElementById('search-results');
  var status = document.getElementById('search-status');
  var data = null, loading = null, timer;
  function norm(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) loading = fetch(input.getAttribute('data-index')).then(function (r) { return r.json(); }).then(function (j) {
      data = j.map(function (p) { p._t = norm(p.t); p._g = norm((p.g || []).join(' ') + ' ' + (p.c || '')); p._s = norm(p.s); p._x = norm(p.x); return p; });
      return data;
    });
    return loading;
  }
  function snippet(p, words) {
    var text = p.x || p.s || '', low = norm(text), at = -1;
    for (var i = 0; i < words.length && at < 0; i++) at = low.indexOf(words[i]);
    if (at < 0) return esc(p.s || '');
    var from = Math.max(0, at - 80), part = text.slice(from, from + 220);
    var out = esc((from ? '…' : '') + part + (from + 220 < text.length ? '…' : ''));
    words.forEach(function (w) { if (w.length > 1) out = out.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>'); });
    return out;
  }
  function plural(n) { var a = n % 10, b = n % 100; return a === 1 && b !== 11 ? 'материал' : (a >= 2 && a <= 4 && (b < 12 || b > 14) ? 'материала' : 'материалов'); }
  function run() {
    var q = input.value.trim();
    var url = new URL(location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    history.replaceState(null, '', url);
    var words = norm(q).split(/\s+/).filter(function (w) { return w.length > 1; });
    if (!words.length) { list.innerHTML = ''; status.textContent = ''; return; }
    load().then(function (items) {
      var res = [];
      items.forEach(function (p) {
        var score = 0;
        for (var i = 0; i < words.length; i++) {
          var w = words[i], sc = 0;
          if (p._t.indexOf(w) >= 0) sc += 6;
          if (p._g.indexOf(w) >= 0) sc += 4;
          if (p._s.indexOf(w) >= 0) sc += 2;
          if (p._x.indexOf(w) >= 0) sc += 1;
          if (!sc) return;
          score += sc;
        }
        res.push([score, p]);
      });
      res.sort(function (a, b) { return b[0] - a[0]; });
      status.textContent = res.length ? 'Найдено: ' + res.length + ' ' + plural(res.length) : 'Ничего не нашлось. Попробуйте другое слово или откройте «Темы».';
      list.innerHTML = res.slice(0, 50).map(function (r) {
        var p = r[1];
        return '<li><a href="' + p.u + '">' + esc(p.t) + '</a><div class="sr-meta">' + (p.c ? '<span>' + esc(p.c) + '</span>' : '') + (p.d ? '<span>' + p.d + '</span>' : '') + '</div><p>' + snippet(p, words) + '</p></li>';
      }).join('');
    }).catch(function () { status.textContent = 'Не удалось загрузить индекс поиска. Обновите страницу.'; });
  }
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 150); });
  input.addEventListener('focus', load, { once: true });
  var q0 = new URL(location.href).searchParams.get('q');
  if (q0) { input.value = q0; run(); } else { input.focus(); }
})();
