const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../../docs/_static/js/home.js'), 'utf8');

function setup({ loaded = true, reduced = false } = {}) {
  function target() {
    const classes = new Set();
    return {
      events: {},
      classList: { add: k => classes.add(k), remove: k => classes.delete(k), contains: k => classes.has(k) },
      style: { setProperty() {}, removeProperty() {} },
      addEventListener(k, fn) { (this.events[k] ??= []).push(fn); },
      emit(k) { for (const fn of this.events[k] || []) fn(); },
    };
  }
  const eclipse = target(), logo = target(), ambient = target();
  Object.assign(logo, { complete: loaded, naturalWidth: loaded ? 1920 : 0, parentElement: eclipse });
  const motion = target(); motion.matches = reduced;
  const fine = target(); fine.matches = true;
  vm.runInNewContext(script, {
    document: { documentElement: target(), querySelector: s => ({
      '.first-run-logo': logo, '.ambient': ambient,
      '.ambient-network': { getContext: () => null },
    })[s], querySelectorAll: () => [] },
    window: target(),
    matchMedia: q => q.includes('reduce') ? motion : fine,
    requestAnimationFrame() {}, cancelAnimationFrame() {},
  });
  return { logo, eclipse };
}

test('cached logo animates on every page load without session storage', () => {
  for (let visit = 0; visit < 2; visit++) {
    assert.equal(setup().eclipse.classList.contains('is-ready'), true);
  }
});

test('animation waits for the image to load', () => {
  const s = setup({ loaded: false });
  assert.equal(s.eclipse.classList.contains('is-ready'), false);
  s.logo.emit('load');
  assert.equal(s.eclipse.classList.contains('is-ready'), true);
});

test('reduced motion bypasses the logo animation', () => {
  for (const loaded of [true, false]) {
    const s = setup({ loaded, reduced: true });
    s.logo.emit('load');
    assert.equal(s.eclipse.classList.contains('is-ready'), false);
  }
});
