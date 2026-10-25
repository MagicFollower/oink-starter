'use strict';

// Source contract only; rendered contrast and interactions belong to the
// sibling documentation site's Markmap browser suite.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const source = fs.readFileSync(
  path.join(__dirname, '../../assets/scss/td/_content-components.scss'), 'utf8',
).replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g, '');

test('Markmap maps the article token on screen with wrapper/SVG specificity', () => {
  assert.match(source,
    /@media\s+screen\s*\{\s*\.td-content\s+\.markmap\s*\{\s*--markmap-text-color:\s*var\(--bs-body-color\);\s*\}\s*\}/,
    'keep the mapping screen-only and applicable to both wrapper and SVG');
});

test('Markmap has no competing text-token assignment or important override', () => {
  const declarations = source.match(/--markmap-text-color\s*:[^;]+;/g) || [];
  assert.deepEqual(declarations, ['--markmap-text-color: var(--bs-body-color);']);
});
