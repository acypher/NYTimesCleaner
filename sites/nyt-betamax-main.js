/**
 * MAIN world (page JS realm): intercept NYT video autoplay that page scripts rely on.
 * Isolated content scripts cannot reliably override HTMLVideoElement.prototype.play.
 *
 * - Betamax: data-testid="betamax-video" under nyt-betamax; gesture via composedPath;
 *   unhides overlay/cover "hide"/"hidden" CSS-module classes.
 * - Cinemagraph promos: data-testid="cinemagraph"; gesture on the video or wrapping
 *   link; blocks attribute-driven autoplay (trusted play).
 * - VHS homepage promos: <video> inside .vhs-grid-page or .react-vhs-container;
 *   typically no autoplay attribute — page calls play(); gated like cinemagraph.
 *   Rejecting play() leaves the player in a buffering/wait UI; we hide that until gesture
 *   (data-nunus-vhs-awaiting-gesture + injected CSS; cleared on grant / playing).
 * - Gallery carousels: <video> inside section[data-testid="Gallery"] (e.g. live blogs);
 *   gesture anywhere on the gallery (slide, link, arrows) allows play on its videos.
 * - Vi large-breakpoint promos: <video> inside section.story-wrapper section[data-tpl="lb"]
 *   (Magazine / hero interview video + headline); gesture on the lb block or video.
 * - Gallery image carousels (same section, ol.carousel-ol): setInterval/setTimeout callbacks
 *   with 2.8s–13s delays are no-op'd while that carousel DOM is present. This is the safe
 *   interval-only approach; the class-revert MutationObserver approach was removed (crash).
 *
 * Defaults on; the popup can disable it.
 */
(function() {
  const h = window.location.hostname;
  const onNyt =
    h === 'www.nytimes.com' ||
    h === 'nytimes.com' ||
    (typeof h === 'string' && h.endsWith('.nytimes.com'));
  if (!onNyt) return;

  const STORAGE_KEY = 'nytCleanerAutoplayBlock';
  const PREFS_READY_KEY = 'nytCleanerPrefsReady';

  function noAutoplayEnabled() {
    try {
      if (sessionStorage.getItem(PREFS_READY_KEY) !== '1') return null;
      const value = sessionStorage.getItem(STORAGE_KEY);
      if (value === '0') return false;
      if (value === '1') return true;
    } catch (_) {}
    return true;
  }

  const enabled = noAutoplayEnabled();
  if (enabled === false) return;
  if (enabled === null) {
    if (window.__nytCleanerMainWaitingForPrefs) return;
    window.__nytCleanerMainWaitingForPrefs = true;
    const startedAt = Date.now();
    const waitForPrefs = () => {
      const nextEnabled = noAutoplayEnabled();
      if (nextEnabled === false) return;
      if (nextEnabled === true || Date.now() - startedAt > 1000) {
        installAutoplayBlocker();
        return;
      }
      requestAnimationFrame(waitForPrefs);
    };
    requestAnimationFrame(waitForPrefs);
    return;
  }

  installAutoplayBlocker();

  function installAutoplayBlocker() {
    if (window.__nytCleanerMainAutoplayLoaded) return;
    window.__nytCleanerMainAutoplayLoaded = true;

  function installGalleryImageCarouselIntervalBlock() {
    if (window.__nunusGalleryCarouselIntervalHook) return;
    window.__nunusGalleryCarouselIntervalHook = true;

    const DELAY_MIN_MS = 2800;
    const DELAY_MAX_MS = 13000;

    function shouldBlockGalleryTick() {
      try {
        return !!document.querySelector(
          'section[data-testid="Gallery"] ol.carousel-ol'
        );
      } catch (_) {
        return false;
      }
    }

    const origSetInterval = window.setInterval;
    window.setInterval = function nunusGalleryGuardedSetInterval(fn, delay) {
      const tail = Array.prototype.slice.call(arguments, 2);
      if (
        typeof fn === 'function' &&
        typeof delay === 'number' &&
        delay >= DELAY_MIN_MS &&
        delay <= DELAY_MAX_MS
      ) {
        const wrapped = function nunusGalleryNoAutoTick(...cbArgs) {
          if (shouldBlockGalleryTick()) return;
          return fn.apply(this, cbArgs);
        };
        return origSetInterval.apply(this, [wrapped, delay].concat(tail));
      }
      return origSetInterval.apply(this, arguments);
    };

    const origSetTimeout = window.setTimeout;
    window.setTimeout = function nunusGalleryGuardedSetTimeout(fn, delay) {
      const tail = Array.prototype.slice.call(arguments, 2);
      if (
        typeof fn === 'function' &&
        typeof delay === 'number' &&
        delay >= DELAY_MIN_MS &&
        delay <= DELAY_MAX_MS
      ) {
        const wrapped = function nunusGalleryNoAutoTimeout(...cbArgs) {
          if (shouldBlockGalleryTick()) return;
          return fn.apply(this, cbArgs);
        };
        return origSetTimeout.apply(this, [wrapped, delay].concat(tail));
      }
      return origSetTimeout.apply(this, arguments);
    };
  }
  installGalleryImageCarouselIntervalBlock();

  var __nunusOrigPlay = HTMLVideoElement.prototype.play;
  HTMLVideoElement.prototype.play = function nunusEarlyPlayGuard() {
    try {
      var betamaxHost = betamaxHostFromVideo(this);
      if (betamaxHost && betamaxHost.dataset.nunusBetamaxPlayAllowed === '1') {
        this.dataset.nunusBetamaxPlayAllowed = '1';
      }
      if (betamaxHost && this.dataset.nunusBetamaxPlayAllowed !== '1') {
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
    } catch (_) {}
    return __nunusOrigPlay.apply(this, arguments);
  };

  if (window.__nunusBetamaxMainInit) return;
  window.__nunusBetamaxMainInit = true;

  function injectNunusVhsGridStyles() {
    if (window.__nunusVhsGridStyleInjected) return;
    window.__nunusVhsGridStyleInjected = true;
    const el = document.createElement('style');
    el.id = 'nunus-vhs-grid-style';
    el.textContent = `
.vhs-grid-page[data-nunus-vhs-awaiting-gesture="1"] .vhs-buffering-container,
.vhs-grid-page[data-nunus-vhs-awaiting-gesture="1"] .vhs-buffering-container * {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
.vhs-grid-page .react-vhs-player.idle .vhs-buffering-container,
.vhs-grid-page .react-vhs-player.idle .vhs-buffering-container *,
.react-vhs-player.idle .vhs-buffering-container,
.react-vhs-player.idle .vhs-buffering-container * {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
`.trim();
    (document.head || document.documentElement).appendChild(el);
  }
  injectNunusVhsGridStyles();

  function markVhsGridAwaitingGesture(video) {
    const grid = video?.closest?.('.vhs-grid-page, .react-vhs-container, .react-vhs-player, .nytd-player-container');
    if (grid) grid.dataset.nunusVhsAwaitingGesture = '1';
    const player = video?.closest?.('.react-vhs-player, .nytd-player-container');
    if (player) {
      try {
        player.classList.add('idle');
      } catch (_) {}
    }
  }

  function clearVhsGridAwaitingGesture(video) {
    const grid = video?.closest?.('.vhs-grid-page, .react-vhs-container, .react-vhs-player, .nytd-player-container');
    if (grid) delete grid.dataset.nunusVhsAwaitingGesture;
  }

  function isBetamaxVideoElement(el) {
    return el instanceof HTMLVideoElement && el.getAttribute('data-testid') === 'betamax-video';
  }

  function isCinemagraphVideoElement(el) {
    return el instanceof HTMLVideoElement && el.getAttribute('data-testid') === 'cinemagraph';
  }

  function isVhsGridPageVideoElement(el) {
    try {
      return el instanceof HTMLVideoElement && !!el.closest(
        '.vhs-grid-page, .react-vhs-container, .react-vhs-player, .nytd-player-container'
      );
    } catch (_) {
      return false;
    }
  }

  function isGalleryCarouselVideoElement(el) {
    try {
      return (
        el instanceof HTMLVideoElement && !!el.closest('section[data-testid="Gallery"]')
      );
    } catch (_) {
      return false;
    }
  }

  function isTplLbStoryPromoVideoElement(el) {
    try {
      if (!(el instanceof HTMLVideoElement)) return false;
      if (!el.closest('section[data-tpl="lb"]')) return false;
      return !!el.closest('section.story-wrapper');
    } catch (_) {
      return false;
    }
  }

  function isGenericArticleVideoElement(el) {
    try {
      if (!(el instanceof HTMLVideoElement)) return false;
      if (el.getAttribute('data-testid') === 'betamax-video') return false;
      if (betamaxHostFromVideo(el)) return false;
      if (el.getAttribute('data-testid') === 'cinemagraph') return false;
      if (isVhsGridPageVideoElement(el)) return false;
      if (isGalleryCarouselVideoElement(el)) return false;
      if (isTplLbStoryPromoVideoElement(el)) return false;
      return true;
    } catch (_) {
      return false;
    }
  }

  function betamaxHostFromVideo(el) {
    let root = el.getRootNode();
    while (root instanceof ShadowRoot) {
      const host = root.host;
      if (host && host.tagName === 'NYT-BETAMAX') return host;
      root = host.getRootNode();
    }
    try {
      const light = el.closest && el.closest('nyt-betamax');
      if (light) return light;
    } catch (_) {}
    return null;
  }

  function stripHiddenishClasses(el) {
    if (!el || !el.classList) return;
    [...el.classList].forEach(c => {
      const lc = c.toLowerCase();
      if (lc.includes('hide') || lc.includes('hidden')) el.classList.remove(c);
    });
  }

  function unhideBetamaxUi(host) {
    try {
      host.querySelectorAll('nyt-betamax-overlay-controls').forEach(oc => {
        const sr = oc.shadowRoot;
        if (!sr) return;
        const ctr = sr.querySelector('[data-testid="betamax-overlay-controls"]');
        if (ctr) stripHiddenishClasses(ctr);
      });
      host.querySelectorAll('nyt-betamax-cover').forEach(cov => {
        const sr = cov.shadowRoot;
        if (!sr) return;
        const inner =
          sr.querySelector('[data-testid="betamax-cover"]') ||
          sr.querySelector('div[class*="cover"]');
        if (inner) stripHiddenishClassesOnTree(inner);
      });
    } catch (_) {}
  }

  function stripHiddenishClassesOnTree(el) {
    stripHiddenishClasses(el);
    el.querySelectorAll?.('*').forEach(stripHiddenishClasses);
  }

  function scheduleBetamaxUnhide(host) {
    const run = () => unhideBetamaxUi(host);
    run();
    requestAnimationFrame(run);
    setTimeout(run, 50);
    setTimeout(run, 200);
    setTimeout(run, 1000);
  }

  function wireBetamaxHostUnhideObserver(host) {
    if (!host || host.dataset.nunusBetamaxUnhideMo === '1') return;
    host.dataset.nunusBetamaxUnhideMo = '1';
    scheduleBetamaxUnhide(host);
    try {
      const mo = new MutationObserver(() => unhideBetamaxUi(host));
      mo.observe(host, { childList: true, subtree: true });
    } catch (_) {}
  }

  function wireBetamaxVideoPause(video) {
    if (!video || video.dataset.nunusBetamaxPauseWired === '1') return;
    video.dataset.nunusBetamaxPauseWired = '1';
    var lastPlayingTs = 0;
    video.addEventListener(
      'playing',
      function() {
        lastPlayingTs = Date.now();
      },
      true
    );
    video.addEventListener(
      'pause',
      function(e) {
        if (!e.isTrusted) return;
        // Carousel / Betamax often pauses right after a short play (one frame/step). Treating
        // that pause like "user stopped" cleared nunusBetamaxPlayAllowed and blocked the next play().
        if (Date.now() - lastPlayingTs < 900) return;
        delete video.dataset.nunusBetamaxPlayAllowed;
        const host = betamaxHostFromVideo(video);
        if (host) delete host.dataset.nunusBetamaxPlayAllowed;
      },
      true
    );
    try {
      const attrMo = new MutationObserver(() => {
        if (video.hasAttribute('autoplay') && video.dataset.nunusBetamaxPlayAllowed !== '1') {
          stripBetamaxAutoplay(video);
          video.pause();
        }
      });
      attrMo.observe(video, { attributes: true, attributeFilter: ['autoplay'] });
    } catch (_) {}
  }

  function wireCinemagraphVideoPause(video) {
    if (!video || video.dataset.nunusCinemagraphPauseWired === '1') return;
    video.dataset.nunusCinemagraphPauseWired = '1';
    video.addEventListener(
      'pause',
      e => {
        if (e.isTrusted) delete video.dataset.nunusCinemagraphPlayAllowed;
      },
      true
    );
  }

  function scanCinemagraphVideo(video) {
    if (!isCinemagraphVideoElement(video)) return;
    wireCinemagraphVideoPause(video);
    try {
      video.pause();
    } catch (_) {}
  }

  function processCinemagraphInTree(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (isCinemagraphVideoElement(node)) {
      scanCinemagraphVideo(node);
      return;
    }
    if (node.querySelectorAll) {
      node.querySelectorAll('video[data-testid="cinemagraph"]').forEach(scanCinemagraphVideo);
    }
  }

  function wireVhsGridVideoPause(video) {
    if (!video || video.dataset.nunusVhsGridPauseWired === '1') return;
    video.dataset.nunusVhsGridPauseWired = '1';
    video.addEventListener(
      'pause',
      e => {
        if (e.isTrusted) delete video.dataset.nunusVhsGridPlayAllowed;
      },
      true
    );
    video.addEventListener(
      'playing',
      () => clearVhsGridAwaitingGesture(video),
      true
    );
  }

  function scanVhsGridVideo(video) {
    if (!isVhsGridPageVideoElement(video)) return;
    wireVhsGridVideoPause(video);
    markVhsGridAwaitingGesture(video);
    try {
      video.pause();
    } catch (_) {}
  }

  function processVhsGridPageInTree(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node instanceof HTMLVideoElement && isVhsGridPageVideoElement(node)) {
      scanVhsGridVideo(node);
      return;
    }
    if (node.matches?.('.vhs-grid-page, .react-vhs-container, .react-vhs-player, .nytd-player-container')) {
      node.querySelectorAll('video').forEach(scanVhsGridVideo);
      return;
    }
    if (node.querySelectorAll) {
      node
        .querySelectorAll('.vhs-grid-page video, .react-vhs-container video, .react-vhs-player video, .nytd-player-container video')
        .forEach(scanVhsGridVideo);
    }
  }

  function wireGalleryCarouselVideoPause(video) {
    if (!video || video.dataset.nunusGalleryPauseWired === '1') return;
    video.dataset.nunusGalleryPauseWired = '1';
    video.addEventListener(
      'pause',
      e => {
        if (e.isTrusted) delete video.dataset.nunusGalleryPlayAllowed;
      },
      true
    );
  }

  function allowGalleryCarouselVideos(gallery) {
    gallery.querySelectorAll('video').forEach(v => {
      v.dataset.nunusGalleryPlayAllowed = '1';
      wireGalleryCarouselVideoPause(v);
    });
  }

  function scanGalleryCarouselVideo(video) {
    if (!isGalleryCarouselVideoElement(video)) return;
    wireGalleryCarouselVideoPause(video);
    try {
      video.pause();
    } catch (_) {}
  }

  function processGalleryCarouselInTree(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.matches?.('section[data-testid="Gallery"]')) {
      node.querySelectorAll('video').forEach(scanGalleryCarouselVideo);
      return;
    }
    if (node instanceof HTMLVideoElement && isGalleryCarouselVideoElement(node)) {
      scanGalleryCarouselVideo(node);
      return;
    }
    if (node.querySelectorAll) {
      node
        .querySelectorAll('section[data-testid="Gallery"] video')
        .forEach(scanGalleryCarouselVideo);
    }
  }

  function wireTplLbStoryPromoVideoPause(video) {
    if (!video || video.dataset.nunusTplLbPauseWired === '1') return;
    video.dataset.nunusTplLbPauseWired = '1';
    video.addEventListener(
      'pause',
      e => {
        if (e.isTrusted) delete video.dataset.nunusTplLbPlayAllowed;
      },
      true
    );
  }

  function scanTplLbStoryPromoVideo(video) {
    if (!isTplLbStoryPromoVideoElement(video)) return;
    wireTplLbStoryPromoVideoPause(video);
    try {
      video.pause();
    } catch (_) {}
  }

  function processTplLbStoryPromoInTree(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node instanceof HTMLVideoElement && isTplLbStoryPromoVideoElement(node)) {
      scanTplLbStoryPromoVideo(node);
      return;
    }
    if (node.matches?.('section.story-wrapper section[data-tpl="lb"]')) {
      node.querySelectorAll('video').forEach(scanTplLbStoryPromoVideo);
      return;
    }
    if (node.querySelectorAll) {
      node
        .querySelectorAll('section.story-wrapper section[data-tpl="lb"] video')
        .forEach(scanTplLbStoryPromoVideo);
    }
  }

  function wireGenericArticleVideoPause(video) {
    if (!video || video.dataset.nunusGenericPauseWired === '1') return;
    video.dataset.nunusGenericPauseWired = '1';
    video.addEventListener(
      'pause',
      e => {
        if (e.isTrusted) delete video.dataset.nunusGenericPlayAllowed;
      },
      true
    );
    // These videos get `controls` forced on (isolated-world script), but the
    // player often sits inside a card link (<a href>) or SPA router click
    // target. Operating the controls would otherwise navigate to the article,
    // so keep the click from bubbling up to that link. Native controls already
    // handled the event by the time it bubbles to the video element.
    video.addEventListener(
      'click',
      e => {
        if (!e.isTrusted) return;
        e.stopPropagation();
        try {
          if (video.closest && video.closest('a[href]')) e.preventDefault();
        } catch (_) {}
      },
      false
    );
  }

  function scanGenericArticleVideo(video) {
    if (!isGenericArticleVideoElement(video)) return;
    wireGenericArticleVideoPause(video);
    try {
      video.pause();
    } catch (_) {}
  }

  function processGenericArticleVideoInTree(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node instanceof HTMLVideoElement) {
      scanGenericArticleVideo(node);
      return;
    }
    if (node.querySelectorAll) {
      node.querySelectorAll('video').forEach(scanGenericArticleVideo);
    }
  }

  function stripBetamaxAutoplay(vid) {
    try {
      vid.removeAttribute('autoplay');
      vid.autoplay = false;
    } catch (_) {}
  }

  function findBetamaxVideo(sr) {
    return sr.querySelector('video[data-testid="betamax-video"]') || sr.querySelector('video');
  }

  /** Slotted / light-DOM players: video is under nyt-betamax but not inside its shadow tree. */
  function findBetamaxVideoInLightDom(host) {
    if (!host || !host.querySelectorAll) return null;
    let any = null;
    try {
      host.querySelectorAll('video').forEach(v => {
        try {
          if (v.closest('nyt-betamax') !== host) return;
        } catch (_) {
          return;
        }
        if (v.getAttribute('data-testid') === 'betamax-video') any = v;
        else if (!any) any = v;
      });
    } catch (_) {}
    return any;
  }

  function findBetamaxVideoForHost(host) {
    const sr = host.shadowRoot;
    if (sr) {
      const inSr = findBetamaxVideo(sr);
      if (inSr) return inSr;
    }
    return findBetamaxVideoInLightDom(host);
  }

  function allowBetamaxHostPlayback(host, vid) {
    if (!host) return;
    host.dataset.nunusBetamaxPlayAllowed = '1';
    const video = vid || findBetamaxVideoForHost(host);
    if (video) {
      video.dataset.nunusBetamaxPlayAllowed = '1';
      wireBetamaxVideoPause(video);
    }
  }

  function applyBetamaxVideoBlock(host, vid) {
    if (host?.dataset?.nunusBetamaxPlayAllowed === '1') {
      vid.dataset.nunusBetamaxPlayAllowed = '1';
    }
    stripBetamaxAutoplay(vid);
    if (vid.dataset.nunusBetamaxPlayAllowed !== '1') {
      try {
        vid.pause();
      } catch (_) {}
    }
    wireBetamaxVideoPause(vid);
    wireBetamaxHostUnhideObserver(host);
  }

  function wireBetamaxHostVideoObserver(host, sr) {
    if (host.dataset.nunusBetamaxSrMo === '1') return;
    host.dataset.nunusBetamaxSrMo = '1';
    const mos = [];
    const disconnect = () => {
      for (let i = 0; i < mos.length; i++) {
        try {
          mos[i].disconnect();
        } catch (_) {}
      }
    };
    const onMut = () => {
      const vid = findBetamaxVideoForHost(host);
      if (vid) {
        disconnect();
        applyBetamaxVideoBlock(host, vid);
      }
    };
    if (sr) {
      const mo = new MutationObserver(onMut);
      mo.observe(sr, { childList: true, subtree: true });
      mos.push(mo);
    }
    const moLight = new MutationObserver(onMut);
    try {
      moLight.observe(host, { childList: true, subtree: true });
      mos.push(moLight);
    } catch (_) {}
  }

  function scanHost(host) {
    wireBetamaxHostUnhideObserver(host);
    const sr = host.shadowRoot;
    const vid = findBetamaxVideoForHost(host);
    if (vid) {
      applyBetamaxVideoBlock(host, vid);
    } else {
      wireBetamaxHostVideoObserver(host, sr);
    }
  }

  function processAddedRoot(node) {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.tagName === 'NYT-BETAMAX') {
      scanHost(node);
    } else if (node.querySelectorAll) {
      node.querySelectorAll('nyt-betamax').forEach(scanHost);
    }
    processCinemagraphInTree(node);
    processVhsGridPageInTree(node);
    processGalleryCarouselInTree(node);
    processTplLbStoryPromoInTree(node);
    processGenericArticleVideoInTree(node);
  }

  HTMLVideoElement.prototype.play = function play() {
    const betamaxHost = betamaxHostFromVideo(this);
    if (betamaxHost) {
      if (betamaxHost.dataset.nunusBetamaxPlayAllowed === '1') {
        this.dataset.nunusBetamaxPlayAllowed = '1';
      }
      if (this.dataset.nunusBetamaxPlayAllowed !== '1') {
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    if (isCinemagraphVideoElement(this)) {
      if (this.dataset.nunusCinemagraphPlayAllowed !== '1') {
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    if (isVhsGridPageVideoElement(this)) {
      if (this.dataset.nunusVhsGridPlayAllowed !== '1') {
        markVhsGridAwaitingGesture(this);
        try {
          this.pause();
        } catch (_) {}
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    if (isGalleryCarouselVideoElement(this)) {
      if (this.dataset.nunusGalleryPlayAllowed !== '1') {
        try {
          this.pause();
        } catch (_) {}
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    if (isTplLbStoryPromoVideoElement(this)) {
      if (this.dataset.nunusTplLbPlayAllowed !== '1') {
        try {
          this.pause();
        } catch (_) {}
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    if (isGenericArticleVideoElement(this)) {
      if (this.dataset.nunusGenericPlayAllowed !== '1') {
        try {
          this.pause();
        } catch (_) {}
        return Promise.reject(
          new DOMException('Nunus blocked autoplay', 'NotAllowedError')
        );
      }
      return __nunusOrigPlay.apply(this, arguments);
    }
    return __nunusOrigPlay.apply(this, arguments);
  };

  function grantBetamaxGestures(e) {
    if (!e.isTrusted) return;
    // Walk composedPath() directly so nyt-betamax elements inside a component's
    // shadow root (e.g. the /video/watch feed player) are found.
    // document.querySelectorAll() does not pierce shadow DOMs.
    for (const node of e.composedPath()) {
      if (node instanceof Element && node.tagName === 'NYT-BETAMAX') {
        const vid = findBetamaxVideoForHost(node);
        allowBetamaxHostPlayback(node, vid);
        wireBetamaxHostUnhideObserver(node);
      }
    }
  }

  function grantCinemagraphGestures(e) {
    if (!e.isTrusted) return;
    const path = e.composedPath();
    for (const node of path) {
      if (isCinemagraphVideoElement(node)) {
        node.dataset.nunusCinemagraphPlayAllowed = '1';
        wireCinemagraphVideoPause(node);
        return;
      }
    }
    let t = e.target;
    if (t && t.nodeType !== Node.ELEMENT_NODE) t = t.parentElement;
    const a = t && t.closest && t.closest('a[href]');
    if (!a) return;
    const vid = a.querySelector('video[data-testid="cinemagraph"]');
    if (vid) {
      vid.dataset.nunusCinemagraphPlayAllowed = '1';
      wireCinemagraphVideoPause(vid);
    }
  }

  function grantVhsGridPageGestures(e) {
    if (!e.isTrusted) return;
    const path = e.composedPath();
    for (const node of path) {
      if (!(node instanceof Element)) continue;
      if (isVhsGridPageVideoElement(node)) {
        node.dataset.nunusVhsGridPlayAllowed = '1';
        clearVhsGridAwaitingGesture(node);
        wireVhsGridVideoPause(node);
        return;
      }
      const grid = node.closest && node.closest(
        '.vhs-grid-page, .react-vhs-container, .react-vhs-player, .nytd-player-container'
      );
      if (grid) {
        const vid = grid.querySelector('video');
        if (vid) {
          vid.dataset.nunusVhsGridPlayAllowed = '1';
          clearVhsGridAwaitingGesture(vid);
          wireVhsGridVideoPause(vid);
          return;
        }
      }
    }
    let t = e.target;
    if (t && t.nodeType !== Node.ELEMENT_NODE) t = t.parentElement;
    const a = t && t.closest && t.closest('a[href]');
    if (!a) return;
    const vidWrap = a.querySelector(
      '.vhs-grid-page video, .react-vhs-container video, .react-vhs-player video, .nytd-player-container video, video'
    );
    if (vidWrap && isVhsGridPageVideoElement(vidWrap)) {
      vidWrap.dataset.nunusVhsGridPlayAllowed = '1';
      clearVhsGridAwaitingGesture(vidWrap);
      wireVhsGridVideoPause(vidWrap);
    }
  }

  function grantGalleryCarouselGestures(e) {
    if (!e.isTrusted) return;
    const path = e.composedPath();
    for (const node of path) {
      if (!(node instanceof Element)) continue;
      const gallery = node.closest?.('section[data-testid="Gallery"]');
      if (gallery) {
        allowGalleryCarouselVideos(gallery);
        return;
      }
    }
  }

  function grantTplLbStoryPromoGestures(e) {
    if (!e.isTrusted) return;
    for (const node of e.composedPath()) {
      if (!(node instanceof Element)) continue;
      if (isTplLbStoryPromoVideoElement(node)) {
        node.dataset.nunusTplLbPlayAllowed = '1';
        wireTplLbStoryPromoVideoPause(node);
        return;
      }
      const lb = node.closest?.('section[data-tpl="lb"]');
      const wrap = node.closest?.('section.story-wrapper');
      if (lb && wrap && wrap.contains(lb)) {
        const vid = lb.querySelector('video');
        if (vid) {
          vid.dataset.nunusTplLbPlayAllowed = '1';
          wireTplLbStoryPromoVideoPause(vid);
          return;
        }
      }
    }
  }

  function grantGenericArticleVideoGestures(e) {
    if (!e.isTrusted) return;
    for (const node of e.composedPath()) {
      if (isGenericArticleVideoElement(node)) {
        node.dataset.nunusGenericPlayAllowed = '1';
        wireGenericArticleVideoPause(node);
        return;
      }
    }
    let t = e.target;
    if (t && t.nodeType !== Node.ELEMENT_NODE) t = t.parentElement;
    const wrap = t && t.closest && t.closest('figure, a[href]');
    if (!wrap) return;
    const vid = wrap.querySelector('video');
    if (vid && isGenericArticleVideoElement(vid)) {
      vid.dataset.nunusGenericPlayAllowed = '1';
      wireGenericArticleVideoPause(vid);
    }
  }

  function grantVideoGestures(e) {
    grantBetamaxGestures(e);
    grantCinemagraphGestures(e);
    grantVhsGridPageGestures(e);
    grantGalleryCarouselGestures(e);
    grantTplLbStoryPromoGestures(e);
    grantGenericArticleVideoGestures(e);
  }

  document.addEventListener('pointerdown', grantVideoGestures, true);
  document.addEventListener('keydown', grantVideoGestures, true);

  function boot() {
    const root = document.documentElement;
    if (!root) return;
    document.querySelectorAll('nyt-betamax').forEach(scanHost);
    document.querySelectorAll('video[data-testid="cinemagraph"]').forEach(scanCinemagraphVideo);
    document
      .querySelectorAll('.vhs-grid-page video, .react-vhs-container video, .react-vhs-player video, .nytd-player-container video')
      .forEach(scanVhsGridVideo);
    document
      .querySelectorAll('section[data-testid="Gallery"] video')
      .forEach(scanGalleryCarouselVideo);
    document
      .querySelectorAll('section.story-wrapper section[data-tpl="lb"] video')
      .forEach(scanTplLbStoryPromoVideo);
    document.querySelectorAll('video').forEach(scanGenericArticleVideo);

    if (!window.__nunusBetamaxDocMo) {
      window.__nunusBetamaxDocMo = new MutationObserver(mutations => {
        for (const m of mutations) {
          for (const n of m.addedNodes) {
            processAddedRoot(n);
          }
        }
      });
      window.__nunusBetamaxDocMo.observe(root, { childList: true, subtree: true });
    }
  }

  boot();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  }
  if (typeof customElements !== 'undefined' && customElements != null && typeof customElements.whenDefined === 'function') {
    customElements.whenDefined('nyt-betamax').then(boot);
  }
  }
})();
