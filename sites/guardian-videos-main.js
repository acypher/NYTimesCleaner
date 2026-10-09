/**
 * MAIN world: block Guardian card video loops that autoplay on scroll.
 *
 * SelfHostedVideo (data-component="gu-video-loop") calls HTMLVideoElement.play()
 * when the card becomes visible. Intercept play() until the user clicks the card
 * or its controls.
 *
 * Defaults on; the popup can disable it (nytCleanerAutoplayBlock).
 */
(function() {
  const h = window.location.hostname;
  const onGuardian =
    h === 'www.theguardian.com' ||
    h === 'theguardian.com' ||
    (typeof h === 'string' && h.endsWith('.theguardian.com'));
  if (!onGuardian) return;

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
    if (window.__nunusGuardianMainWaitingForPrefs) return;
    window.__nunusGuardianMainWaitingForPrefs = true;
    const startedAt = Date.now();
    const waitForPrefs = () => {
      const nextEnabled = noAutoplayEnabled();
      if (nextEnabled === false) return;
      if (nextEnabled === true || Date.now() - startedAt > 1000) {
        installGuardianAutoplayBlocker();
        return;
      }
      requestAnimationFrame(waitForPrefs);
    };
    requestAnimationFrame(waitForPrefs);
    return;
  }

  installGuardianAutoplayBlocker();

  function installGuardianAutoplayBlocker() {
    if (window.__nunusGuardianMainAutoplayLoaded) return;
    window.__nunusGuardianMainAutoplayLoaded = true;

    const PLAY_ALLOWED = 'nunusGuardianLoopPlayAllowed';

    function isGuardianVideoLoopElement(el) {
      try {
        return (
          el instanceof HTMLVideoElement &&
          !!el.closest('[data-component="gu-video-loop"]')
        );
      } catch (_) {
        return false;
      }
    }

    function wireGuardianLoopVideoPause(video) {
      if (!video || video.dataset.nunusGuardianLoopPauseWired === '1') return;
      video.dataset.nunusGuardianLoopPauseWired = '1';
      video.addEventListener(
        'pause',
        e => {
          if (e.isTrusted) delete video.dataset[PLAY_ALLOWED];
        },
        true
      );
    }

    function scanGuardianLoopVideo(video) {
      if (!isGuardianVideoLoopElement(video)) return;
      wireGuardianLoopVideoPause(video);
      if (video.dataset[PLAY_ALLOWED] !== '1') {
        try {
          video.pause();
        } catch (_) {}
      }
    }

    function processGuardianLoopInTree(node) {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
      if (node instanceof HTMLVideoElement) {
        scanGuardianLoopVideo(node);
        return;
      }
      if (node.matches?.('[data-component="gu-video-loop"]')) {
        node.querySelectorAll('video').forEach(scanGuardianLoopVideo);
        return;
      }
      if (node.querySelectorAll) {
        node
          .querySelectorAll('[data-component="gu-video-loop"] video')
          .forEach(scanGuardianLoopVideo);
      }
    }

    const origPlay = HTMLVideoElement.prototype.play;
    HTMLVideoElement.prototype.play = function nunusGuardianLoopPlayGuard() {
      if (isGuardianVideoLoopElement(this)) {
        if (this.dataset[PLAY_ALLOWED] !== '1') {
          try {
            this.pause();
          } catch (_) {}
          return Promise.reject(
            new DOMException('Nunus blocked autoplay', 'NotAllowedError')
          );
        }
        return origPlay.apply(this, arguments);
      }
      return origPlay.apply(this, arguments);
    };

    function allowGuardianLoopVideo(video) {
      if (!video) return;
      video.dataset[PLAY_ALLOWED] = '1';
      wireGuardianLoopVideoPause(video);
    }

    function grantGuardianLoopGestures(e) {
      if (!e.isTrusted) return;
      for (const node of e.composedPath()) {
        if (!(node instanceof Element)) continue;
        if (isGuardianVideoLoopElement(node)) {
          allowGuardianLoopVideo(node);
          return;
        }
        const loop = node.closest?.('[data-component="gu-video-loop"]');
        if (loop) {
          const vid = loop.querySelector('video');
          allowGuardianLoopVideo(vid);
          return;
        }
      }
    }

    document.addEventListener('pointerdown', grantGuardianLoopGestures, true);
    document.addEventListener('keydown', grantGuardianLoopGestures, true);

    function boot() {
      const root = document.documentElement;
      if (!root) return;
      document
        .querySelectorAll('[data-component="gu-video-loop"] video')
        .forEach(scanGuardianLoopVideo);

      if (!window.__nunusGuardianLoopDocMo) {
        window.__nunusGuardianLoopDocMo = new MutationObserver(mutations => {
          for (const m of mutations) {
            for (const n of m.addedNodes) {
              processGuardianLoopInTree(n);
            }
          }
        });
        window.__nunusGuardianLoopDocMo.observe(root, { childList: true, subtree: true });
      }
    }

    boot();
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', boot, { once: true });
    }
  }
})();
