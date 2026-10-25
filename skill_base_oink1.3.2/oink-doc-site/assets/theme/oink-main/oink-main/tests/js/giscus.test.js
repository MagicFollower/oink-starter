'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// No network: an already mounted comment frame records the configuration
// messages it would receive when the reader changes style or mode.
test('Giscus follows preset and mode while explicit author themes remain authoritative', () => {
  const attributes = new Map([['data-td-preset', 'paper'], ['data-bs-theme', 'light']]);
  const root = { getAttribute: key => attributes.get(key) };
  const messages = [];
  const section = {
    dataset: {
      loaded: 'true', theme: 'auto',
      tdThemeLight: '/legacy-light.css', tdThemeDark: '/legacy-dark.css',
      tdPresetThemes: JSON.stringify({
        paper: { light: '/paper-light.css', dark: '/paper-dark.css' },
        slate: { light: '/slate-light.css', dark: '/slate-dark.css' },
      }),
    },
    querySelector: () => ({ contentWindow: { postMessage: (message, origin) => messages.push({ message, origin }) } }),
  };
  let notify;
  const MutationObserver = class {
    constructor(callback) { notify = callback; }
    observe(target, options) {
      assert.equal(target, root);
      assert.deepEqual(Array.from(options.attributeFilter), ['data-bs-theme', 'data-td-preset']);
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../../assets/js/giscus.js'), 'utf8'), {
    document: { documentElement: root, querySelectorAll: () => [section] },
    window: { location: { origin: 'https://example.org' }, matchMedia: () => ({ matches: true, addEventListener() {} }) },
    MutationObserver, URL,
  });
  function expectTheme(theme) {
    notify();
    const last = messages.at(-1);
    assert.equal(last.origin, 'https://giscus.app');
    assert.equal(last.message.giscus.setConfig.theme, theme);
  }
  expectTheme('https://example.org/paper-light.css');
  attributes.delete('data-bs-theme');
  expectTheme('https://example.org/paper-light.css');
  attributes.set('data-bs-theme', 'dark');
  expectTheme('https://example.org/paper-dark.css');
  attributes.set('data-td-preset', 'slate');
  expectTheme('https://example.org/slate-dark.css');
  section.dataset.theme = 'dark_high_contrast';
  attributes.set('data-td-preset', 'paper');
  expectTheme('dark_high_contrast');
  section.dataset.theme = '/custom.css';
  expectTheme('https://example.org/custom.css');
  section.dataset.theme = 'auto';
  section.dataset.tdPresetThemes = '{}';
  expectTheme('https://example.org/legacy-dark.css');
});
