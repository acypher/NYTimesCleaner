/**
 * MAIN world: block Epoch Times Video.js players that autoplay on load.
 *
 * Epoch article pages use video.js (.video-js / .vjs-preview). The player calls
 * HTMLVideoElement.play() programmatically (often muted). Intercept play() until
 * the user clicks the player or its controls.
 *
 * Defaults on; the popup can disable it (nytCleanerAutoplayBlock).
 */
(function() {
  const h = window.location.hostname;
  const onEpoch =
    h === 'www.theepochtimes.com' ||
    h === 'theepochtimes.com' ||
    (typeof h === 'string' && h.endsWith('.theepochtimes.com'));
  if (!onEpoch) return;

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
    if (window.__nunusEpochMainWaitingForPrefs) return;
    window.__nunusEpochMainWaitingForPrefs = true;
    const startedAt = Date.now();
    const waitForPrefs = () => {
      const nextEnabled = noAutoplayEnabled();
      if (nextEnabled === false) return;
      if (nextEnabled === true || Date.now() - startedAt > 1000) {
        installEpochAutoplayBlocker();
        return;
      }
      requestAnimationFrame(waitForPrefs);
    };
    requestAnimationFrame(waitForPrefs);
    return;
  }

  installEpochAutoplayBlocker();

  function installEpochAutoplayBlocker() {
    if (window.__nunusEpochMainAutoplayLoaded) return;
    window.__nunusEpochMainAutoplayLoaded = true;

    const PLAY_ALLOWED = 'nunusEpochVjsPlayAllowed';

    function isEpochVideoJsElement(el) {
      try {
        return (
          el instanceof HTMLVideoElement &&
          (!!el.closest('.video-js') ||
            !!el.closest('.vjs-preview') ||
            el.classList.contains('vjs-tech'))
        );
      } catch (_) {
        return false;
      }
    }

    function wireEpochVideoPause(video) {
      if (!video || video.dataset.nunusEpochVjsPauseWired === '1') return;
      video.dataset.nunusEpochVjsPauseWired = '1';
      video.addEventListener(
        'pause',
        e => {
          if (e.isTrusted) delete video.dataset[PLAY_ALLOWED];
        },
        true
      );
    }

    function scanEpochVideo(video) {
      if (!isEpochVideoJsElement(video)) return;
      wireEpochVideoPause(video);
      if (video.dataset[PLAY_ALLOWED] !== '1') {
        try {
          video.pause();
        } catch (_) {}
      }
    }

    function processEpochInTree(node) {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
      if (node instanceof HTMLVideoElement) {
        scanEpochVideo(node);
        return;
      }
      if (node.matches?.('.video-js, .vjs-preview')) {
        node.querySelectorAll('video').forEach(scanEpochVideo);
        return;
      }
      if (node.querySelectorAll) {
        node
          .querySelectorAll('.video-js video, .vjs-preview video, video.vjs-tech')
          .forEach(scanEpochVideo);
      }
    }

    const origPlay = HTMLVideoElement.prototype.play;
    HTMLVideoElement.prototype.play = function nunusEpochVjsPlayGuard() {
      if (isEpochVideoJsElement(this)) {
        if (this.dataset[PLAY_ALLOWED] !== '1') {
          try {
            this.pause();
          } catch (_) {}
          return Promise.reject(
            new DOMException('NewsMinus blocked autoplay', 'NotAllowedError')
          );
        }
        return origPlay.apply(this, arguments);
      }
      return origPlay.apply(this, arguments);
    };

    function allowEpochVideo(video) {
      if (!video) return;
      video.dataset[PLAY_ALLOWED] = '1';
      wireEpochVideoPause(video);
    }

    function grantEpochGestures(e) {
      if (!e.isTrusted) return;
      for (const node of e.composedPath()) {
        if (!(node instanceof Element)) continue;
        if (isEpochVideoJsElement(node)) {
          allowEpochVideo(node);
          return;
        }
        const player = node.closest?.('.video-js, .vjs-preview');
        if (player) {
          allowEpochVideo(player.querySelector('video'));
          return;
        }
      }
    }

    document.addEventListener('pointerdown', grantEpochGestures, true);
    document.addEventListener('keydown', grantEpochGestures, true);

    function boot() {
      const root = document.documentElement;
      if (!root) return;
      document
        .querySelectorAll('.video-js video, .vjs-preview video, video.vjs-tech')
        .forEach(scanEpochVideo);

      if (!window.__nunusEpochVjsDocMo) {
        window.__nunusEpochVjsDocMo = new MutationObserver(mutations => {
          for (const m of mutations) {
            for (const n of m.addedNodes) {
              processEpochInTree(n);
            }
          }
        });
        window.__nunusEpochVjsDocMo.observe(root, { childList: true, subtree: true });
      }
    }

    boot();
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', boot, { once: true });
    }
  }
})();
