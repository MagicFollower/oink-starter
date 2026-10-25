'use strict';

const assert = require('node:assert/strict');
const clipboard = require('../../assets/js/clipboard.js');

function harness(command = () => true) {
  const ranges = [{ cloneRange() { return this; } }];
  const selection = {
    rangeCount: 1,
    getRangeAt(index) { return ranges[index]; },
    removeAllRanges() { ranges.length = 0; },
    addRange(range) { ranges.push(range); },
  };
  const doc = {
    body: { appendChild() {} },
    documentElement: {},
    getSelection() { return selection; },
    createElement() {
      return {
        style: {},
        value: '',
        setAttribute() {},
        select() { doc.activeElement = this; },
        setSelectionRange() {},
        remove() { this.removed = true; if (doc.activeElement === this) doc.activeElement = doc.body; },
      };
    },
    execCommand(name) { assert.equal(name, 'copy'); return command(doc); },
  };
  const previous = {
    isConnected: true,
    selectionStart: 2,
    selectionEnd: 5,
    selectionDirection: 'backward',
    focus(options) { assert.equal(options.preventScroll, true); doc.activeElement = this; },
    setSelectionRange(...args) { this.restoredSelection = args; },
  };
  doc.activeElement = previous;
  return { doc, previous, ranges };
}

(async () => {
  for (const navigator of [{}, { clipboard: { writeText() { return Promise.reject(new Error('denied')); } } }]) {
    const { doc, previous, ranges } = harness();
    await clipboard.writeText('Copy text', doc, navigator);
    assert.equal(doc.activeElement, previous);
    assert.deepEqual(previous.restoredSelection, [2, 5, 'backward']);
    assert.equal(ranges.length, 1);
  }
  for (const command of [() => false, () => { throw new Error('copy threw'); }]) {
    const { doc, previous } = harness(command);
    await assert.rejects(clipboard.writeText('Copy text', doc, {}));
    assert.equal(doc.activeElement, previous, 'failed copy did not restore focus');
  }
  const newerFocus = {};
  const changed = harness(doc => { doc.activeElement = newerFocus; return true; });
  await clipboard.writeText('Copy text', changed.doc, {});
  assert.equal(changed.doc.activeElement, newerFocus, 'copy stole focus from a copy-event handler');

  const detached = harness(() => { detached.previous.isConnected = false; return true; });
  await clipboard.writeText('Copy text', detached.doc, {});
  assert.equal(detached.doc.activeElement, detached.doc.body);

  for (const succeeds of [true, false]) {
    const dom = harness(() => succeeds);
    delete dom.previous.selectionStart;
    const node = {};
    Object.assign(dom.ranges[0], {
      collapsed: false, startContainer: node, startOffset: 2, endContainer: node, endOffset: 8,
    });
    const selection = dom.doc.getSelection();
    Object.assign(selection, {
      anchorNode: node, anchorOffset: 8, focusNode: node, focusOffset: 2,
      setBaseAndExtent(...args) { this.restoredDirection = args; },
    });
    const copy = clipboard.writeText('Copy text', dom.doc, {});
    if (succeeds) await copy;
    else await assert.rejects(copy);
    assert.equal(dom.doc.activeElement, dom.previous);
    assert.deepEqual(selection.restoredDirection, [node, 8, node, 2]);
  }
  console.log('clipboard fallback focus checks passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
