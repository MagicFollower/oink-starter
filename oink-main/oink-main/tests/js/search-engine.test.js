'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

global.window = {};
const lunr = require(
  path.join(__dirname, '..', '..', 'assets/js/third_party/lunr.min.js'),
);
const engineModule = require(
  path.join(__dirname, '..', '..', 'assets/js/search-engine.js'),
);

const documents = [
  {
    ref: '/docs/tutorial/',
    title: 'Tutorial',
    body: 'ordinary page',
    keywords: ['pgboost'],
    boost: 1.5,
  },
  {
    ref: '/docs/advanced/',
    title: 'Advanced',
    body: 'ordinary page',
    keywords: ['pgboost'],
    boost: 3,
  },
  {
    ref: '/docs/reference/',
    title: 'Reference',
    body: 'postgres appears in body',
    keywords: ['postgres'],
    boost: 1,
  },
  {
    ref: '/zh/tutorial/',
    title: '教程',
    body: '普通页面',
    keywords: ['增强词'],
    boost: 1.5,
  },
  {
    ref: '/zh/advanced/',
    title: '高级',
    body: '普通页面',
    keywords: ['增强词'],
    boost: 3,
  },
  {
    ref: '/tie/b/',
    title: 'Same',
    body: 'tiequery',
    keywords: [],
    boost: 1,
  },
  {
    ref: '/tie/a/',
    title: 'Same',
    body: 'tiequery',
    keywords: [],
    boost: 1,
  },
];

const engine = engineModule.create(documents, lunr, 20);

const latin = engine.queryLatin('pgboost');
assert.deepEqual(
  latin.slice(0, 2).map((result) => result.doc.ref),
  ['/docs/advanced/', '/docs/tutorial/'],
);
assert.ok(latin[0].score > latin[1].score);

const latinKeyword = engine.queryLatin('postgres');
assert.equal(latinKeyword[0].doc.ref, '/docs/reference/');
assert.ok(latinKeyword[0].score > 0);

const cjk = engine.queryCjk('增强词');
assert.deepEqual(
  cjk.slice(0, 2).map((result) => result.doc.ref),
  ['/zh/advanced/', '/zh/tutorial/'],
);
assert.equal(cjk[0].textScore, cjk[1].textScore);
assert.ok(cjk[0].score > cjk[1].score);

// Synonyms help discovery; a keyword-only match still describes the page.
const keywordPages = [
  {
    ref: '/zh/config/',
    title: 'Configuration',
    keywords: ['配置', 'params', 'defaults'],
    description: '查找站点参数的类型、默认值与用法。',
    excerpt: 'A shorter fallback.',
  },
  {
    ref: '/zh/fallback/',
    title: 'Fallback',
    keywords: '配置 params defaults',
    excerpt: 'Site settings and examples.',
  },
  { ref: '/zh/no-summary/', title: 'No summary', keywords: ['配置'] },
  {
    ref: '/zh/body/',
    title: 'Body match',
    keywords: ['配置'],
    body: '这里介绍配置步骤。',
    description: 'Read the guide.',
  },
];
const keywordResults = engineModule.create(keywordPages, lunr, 20).query('配置');
const excerpts = new Map(keywordResults.map(({ doc, excerpt }) => [doc.ref, excerpt]));
assert.equal(excerpts.get('/zh/config/'), keywordPages[0].description);
assert.equal(excerpts.get('/zh/fallback/'), keywordPages[1].excerpt);
assert.equal(excerpts.get('/zh/no-summary/'), '');
assert.equal(excerpts.get('/zh/body/'), '这里介绍配置步骤。…');

const tie = engine.queryLatin('tiequery');
assert.deepEqual(
  tie.map((result) => result.doc.ref),
  ['/tie/a/', '/tie/b/'],
);

const grouped = engineModule.group([
  { doc: { ref: '/docs/a/', root: 'Docs', breadcrumb: ['Documentation'] } },
  { doc: { ref: '/blog/a/', type: 'BLOG', breadcrumb: ['Blog'] } },
  { doc: { ref: '/docs/b/', root: 'docs', breadcrumb: ['Docs'] } },
]);
assert.deepEqual(
  grouped.map((group) => ({
    key: group.key,
    label: group.label,
    refs: group.results.map((result) => result.doc.ref),
  })),
  [
    {
      key: 'docs',
      label: 'Documentation',
      refs: ['/docs/a/', '/docs/b/'],
    },
    { key: 'blog', label: 'Blog', refs: ['/blog/a/'] },
  ],
);

const legacy = documents.map(({ keywords, boost, ...document }) => document);
const defaults = legacy.map((document) => ({
  ...document,
  keywords: [],
  boost: 1,
}));
const legacyResults = engineModule
  .create(legacy, lunr, 20)
  .queryLatin('ordinary')
  .map((result) => [result.doc.ref, result.score]);
const defaultResults = engineModule
  .create(defaults, lunr, 20)
  .queryLatin('ordinary')
  .map((result) => [result.doc.ref, result.score]);
assert.deepEqual(legacyResults, defaultResults);

if (process.argv.length > 2) {
  assert.equal(process.argv.length, 4, 'expected EN and ZH built index paths');
  const en = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const zh = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
  const enResults = engineModule.create(en, lunr, 20).queryLatin('pgboost');
  const zhResults = engineModule.create(zh, lunr, 20).queryCjk('增强词');
  assert.deepEqual(
    enResults.slice(0, 2).map((result) => result.doc.ref.split('/').at(-2)),
    ['advanced', 'tutorial'],
  );
  assert.deepEqual(
    zhResults.slice(0, 2).map((result) => result.doc.ref.split('/').at(-2)),
    ['advanced', 'tutorial'],
  );
}

console.log('search engine ranking checks passed');
