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
    document.querySelectorAll('.sec-head, .about-grid, .factbox, .hero-in > div, .svc-foot, .page-hero .inner')
      .forEach(function (el) { el.classList.add('reveal'); });
    document.querySelectorAll('.svc-grid, .room-grid, .post-grid, .term-cloud')
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
