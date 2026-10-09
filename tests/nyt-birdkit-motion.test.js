const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function setup(preference = '1', ready = '1') {
  const values = new Map([
    ['nytCleanerAutoplayBlock', preference],
    ['nytCleanerPrefsReady', ready]
  ]);
  const nativeMedia = {
    get matches() { assert.equal(this, nativeMedia); return false; },
    get media() { assert.equal(this, nativeMedia); return '(prefers-reduced-motion: reduce)'; },
    addEventListener() { assert.equal(this, nativeMedia); }
  };
  const context = vm.createContext({
    sessionStorage: { getItem: key => values.get(key) },
    window: { location: { hostname: 'www.nytimes.com' }, matchMedia: () => nativeMedia },
    // Exercise the complete script while isolating the unrelated video blocker.
    requestAnimationFrame() {}
  });
  values.set('nytCleanerPrefsReady', '0');
  vm.runInContext(fs.readFileSync(require.resolve('../sites/nyt-betamax-main.js'), 'utf8'), context);
  values.set('nytCleanerPrefsReady', ready);
  return { context, values, nativeMedia };
}

const graphicSource = 'https://static01.nytimes.com/newsgraphics/PHPTs7LboZ_ZHw/immutable/nodes/promo.js';
function graphicQuery(context, query = '(prefers-reduced-motion: reduce)') {
  return vm.runInContext(`window.matchMedia(${JSON.stringify(query)})`, context, { filename: graphicSource });
}

test('calendar selects its still mode, without suppressing layout work or replacing its DOM', () => {
  const { context } = setup();
  // The animation-start decision used by the supplied Birdkit promo module.
  assert.equal(vm.runInContext(`(() => {
    let timerStarted = false, revealed = 0;
    const quotes = [1, 2, 3, 4];
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || quotes.length < 2) {
      revealed = quotes.length;
    } else { timerStarted = true; }
    return revealed === 4 && !timerStarted;
  })()`, context, { filename: graphicSource }), true);
});

test('unrelated scripts, other graphics, and other media queries keep native results', () => {
  const { context, nativeMedia } = setup();
  assert.equal(vm.runInContext("window.matchMedia('(prefers-reduced-motion: reduce)')", context), nativeMedia);
  assert.equal(vm.runInContext("window.matchMedia('(prefers-reduced-motion: reduce)')", context,
    { filename: 'https://static01.nytimes.com/newsgraphics/another-graphic/promo.js' }), nativeMedia);
  assert.equal(graphicQuery(context, '(max-width: 600px)'), nativeMedia);
});

test('No autoplay preference is respected, including before prefs finish loading', () => {
  const { context, values } = setup('0');
  const media = graphicQuery(context);
  assert.equal(media.matches, false);
  values.set('nytCleanerAutoplayBlock', '1');
  assert.equal(media.matches, true);
  values.set('nytCleanerPrefsReady', '0');
  assert.equal(media.matches, true);
});

test('MediaQueryList native getters and listeners retain the correct receiver', () => {
  const { context } = setup();
  const media = graphicQuery(context);
  assert.equal(media.media, '(prefers-reduced-motion: reduce)');
  media.addEventListener('change', () => {});
  media.onchange = null;
  assert.equal(media.onchange, null);
});
