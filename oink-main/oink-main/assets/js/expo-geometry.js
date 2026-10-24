/* Shared geometry: source pixels are CSS pixels at 100%, independent of DPR. */
(function (root) {
  'use strict';
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const scale = (width, height, availableWidth, availableHeight, mode = 'fit') => {
    if (![width, height, availableWidth, availableHeight].every(n => Number.isFinite(n) && n > 0)) return 1;
    const x = availableWidth / width, y = availableHeight / height;
    // Expansion may enlarge small originals, but the stricter edge always wins.
    return mode === 'expand' ? Math.min(x, y) : Math.min(1, x, y);
  };
  // Bounded display ratios give panoramas and long scrolls usable entry tiles.
  const wall = (ratios, width, target, gap) => {
    if (!(width > 0)) return [];
    const boxes = []; let row = [], sum = 0, y = 0;
    const finish = last => {
      if (!row.length) return;
      const h = Math.min((width - gap * (row.length - 1)) / sum, last ? target : target * 1.6);
      let x = 0;
      row.forEach(ratio => { const w = ratio * h; boxes.push({ x, y, width: w, height: h }); x += w + gap; });
      y += h + gap; row = []; sum = 0;
    };
    ratios.forEach((value, index) => {
      const ratio = clamp(value || 1, .6, 2.8);
      row.push(ratio); sum += ratio;
      if (sum * target + gap * (row.length - 1) >= width) finish(false);
      else if (index === ratios.length - 1) finish(true);
    });
    return boxes;
  };
  const api = { clamp, scale, wall };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.OinkExpoGeometry = api;
})(globalThis);
