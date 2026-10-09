/**
 * NYTimes onsite message cleanup.
 *
 * Removes subscription upsell docks and similar NYT-owned onsite messaging
 * units. Defaults on; the popup can disable it.
 */
(function() {
  const ext = globalThis.browser ?? globalThis.chrome;
  const h = window.location.hostname;
  const onNyt =
    h === 'www.nytimes.com' ||
    h === 'nytimes.com' ||
    (typeof h === 'string' && h.endsWith('.nytimes.com'));
  if (!onNyt) return;

  const STORAGE_KEY = 'nytCleanerNoTimesAds';
  const ns = (window.__nytCleanerNoTimesAds = window.__nytCleanerNoTimesAds || {});

  const SELECTORS = [
    '#dock-container[data-testid^="onsite-messaging-unit-"]',
    '[data-testid^="onsite-messaging-unit-"][data-campaign]',
    '[data-campaign^="ACCT_UPGRADE_"][data-testid^="onsite-messaging-unit-"]',
    'aside[data-testid="loaf"][data-gtm-element="newsletter_loaf_form"]',
    'div[id^="story-ad-"][id$="-wrapper"]',
    '#top-wrapper',
    '#sponsor-wrapper',
    '#bottom-wrapper'
  ];

  function isEnabledFromSession() {
    try {
      const value = sessionStorage.getItem(STORAGE_KEY);
      if (value === '0') return false;
      if (value === '1') return true;
    } catch (_) {}
    return true;
  }

  function removeAds(root) {
    if (!ns.enabled || !root?.querySelectorAll) return;
    try {
      root.querySelectorAll(SELECTORS.join(',')).forEach(el => el.remove());
    } catch (_) {}
  }

  function boot() {
    ns.enabled = isEnabledFromSession();
    if (!ns.enabled) return;

    const root = document.documentElement;
    if (!root) return;
    removeAds(root);

    if (ns.docMo) return;
    ns.docMo = new MutationObserver(mutations => {
      if (!ns.enabled) return;
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType !== Node.ELEMENT_NODE) return;
          if (node.matches?.(SELECTORS.join(','))) {
            node.remove();
            return;
          }
          removeAds(node);
        });
      });
    });
    ns.docMo.observe(root, { childList: true, subtree: true });
  }

  function setEnabled(enabled) {
    ns.enabled = enabled;
    try {
      sessionStorage.setItem(STORAGE_KEY, enabled ? '1' : '0');
    } catch (_) {}
    if (enabled) boot();
  }

  boot();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  }

  try {
    ext?.storage?.local?.get({ [STORAGE_KEY]: true }, values => {
      setEnabled(values[STORAGE_KEY] !== false);
    });
    ext?.storage?.onChanged?.addListener((changes, area) => {
      if (area === 'local' && changes[STORAGE_KEY]) {
        setEnabled(changes[STORAGE_KEY].newValue !== false);
      }
    });
  } catch (_) {}
})();
