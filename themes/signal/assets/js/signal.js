/* Signal theme — interactions: scroll-reveal, reading progress, TOC active state, mobile menu */
(function () {
  'use strict';

  /* ---- mobile menu ---- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.menu-btn');
    if (btn) {
      var h = document.querySelector('header.site');
      if (h) h.classList.toggle('open');
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

    function onScroll() {
      var h = document.documentElement;
      if (bar) {
        var max = h.scrollHeight - h.clientHeight;
        bar.style.width = (max > 0 ? (h.scrollTop / max * 100) : 0) + '%';
      }
      if (tocLinks.length) {
        var cur = -1;
        for (var i = 0; i < sections.length; i++) {
          if (sections[i] && sections[i].getBoundingClientRect().top < 140) cur = i;
        }
        tocLinks.forEach(function (a, i) { a.classList.toggle('active', i === cur); });
      }
    }
    document.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
  })();
})();

/* ---- gallery lightbox ---- */
(function () {
  var grid = document.getElementById('gal-grid');
  var box = document.getElementById('lb');
  if (!grid || !box) return;

  var items = [].slice.call(grid.querySelectorAll('.gal-item'));
  if (!items.length) return;

  var img = box.querySelector('.lb-img');
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
    lastFocus = document.activeElement;
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
