/**
 * Guardian (isolated world): pause gu-video-loop card videos and strip autoplay attrs.
 * Programmatic play() is blocked in guardian-videos-main.js (MAIN world).
 *
 * Defaults on; the popup can disable it. document_start; MutationObserver singleton.
 */
(function() {
  const ext = globalThis.browser ?? globalThis.chrome;
  const h = window.location.hostname;
  const onGuardian =
    h === 'www.theguardian.com' ||
    h === 'theguardian.com' ||
    (typeof h === 'string' && h.endsWith('.theguardian.com'));
  if (!onGuardian) return;

  const STORAGE_KEY = 'nytCleanerAutoplayBlock';
  const ns = (window.__nunusGuardianVideos = window.__nunusGuardianVideos || {});

  function isEnabledFromSession() {
    try {
      const value = sessionStorage.getItem(STORAGE_KEY);
      if (value === '0') return false;
      if (value === '1') return true;
    } catch (_) {}
    return true;
  }

  function isGuardianVideoLoop(el) {
    try {
      return (
        el instanceof HTMLVideoElement &&
        !!el.closest('[data-component="gu-video-loop"]')
      );
    } catch (_) {
      return false;
    }
  }

  function applyVideo(el) {
    if (ns.enabled === false) return;
    if (!isGuardianVideoLoop(el)) return;
    if (el.dataset.nunusGuardianVideoPatched === '1') return;
    el.dataset.nunusGuardianVideoPatched = '1';

    if (el.hasAttribute('autoplay')) el.removeAttribute('autoplay');
    try {
      el.autoplay = false;
    } catch (_) {}

    const blockProgrammaticPlayback = e => {
      if (!e.isTrusted) {
        try {
          el.pause();
        } catch (_) {}
      }
    };
    el.addEventListener('play', blockProgrammaticPlayback, true);
    el.addEventListener('playing', blockProgrammaticPlayback, true);

    try {
      el.pause();
    } catch (_) {}
  }

  function scanSubtree(node) {
    if (ns.enabled === false) return;
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return;
    if (node instanceof HTMLVideoElement) {
      applyVideo(node);
      return;
    }
    if (node.querySelectorAll) {
      node.querySelectorAll('[data-component="gu-video-loop"] video').forEach(applyVideo);
    }
  }

  function boot() {
    ns.enabled = isEnabledFromSession();
    if (!ns.enabled) return;
    const root = document.documentElement;
    if (!root) return;
    scanSubtree(root);

    if (ns.docMoAttached) return;
    ns.docMoAttached = true;
    ns.docMo = new MutationObserver(mutations => {
      for (const m of mutations) {
        for (const n of m.addedNodes) {
          if (n.nodeType === Node.ELEMENT_NODE) scanSubtree(n);
        }
      }
    });
    ns.docMo.observe(root, { childList: true, subtree: true });
  }

  boot();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  }

  try {
    ext?.storage?.local?.get({ [STORAGE_KEY]: true }, values => {
      ns.enabled = values[STORAGE_KEY] !== false;
      try {
        sessionStorage.setItem(STORAGE_KEY, ns.enabled ? '1' : '0');
      } catch (_) {}
      if (ns.enabled) boot();
    });
    ext?.storage?.onChanged?.addListener((changes, area) => {
      if (area !== 'local' || !changes[STORAGE_KEY]) return;
      ns.enabled = changes[STORAGE_KEY].newValue !== false;
      try {
        sessionStorage.setItem(STORAGE_KEY, ns.enabled ? '1' : '0');
      } catch (_) {}
      if (ns.enabled) boot();
    });
  } catch (_) {}
})();
