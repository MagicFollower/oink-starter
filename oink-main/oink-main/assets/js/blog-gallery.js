/* A blog gallery links to articles. Only geometry is shared with Expo. */
(() => {
  'use strict';
  const G = window.OinkExpoGeometry;
  if (!G) return;
  document.querySelectorAll('[data-td-blog-gallery]').forEach(gallery => {
    const grid = gallery.querySelector('[data-gallery-grid]');
    const items = [...grid.querySelectorAll('[data-gallery-item]')];
    const controls = gallery.querySelector('[data-gallery-controls]');
    const modes = [...controls.querySelectorAll('[data-gallery-mode]')];
    const slider = controls.querySelector('[data-gallery-size]');
    const hover = matchMedia('(hover: hover) and (pointer: fine)');
    let mode = gallery.dataset.tdMode;
    let size = Number(gallery.dataset.tdSize);
    try {
      const saved = localStorage.getItem('td-blog-gallery-mode');
      const savedSize = Number(localStorage.getItem('td-blog-gallery-size'));
      if (['wall', 'cards', 'seamless'].includes(saved)) mode = saved;
      if (Number.isInteger(savedSize) && savedSize >= 160 && savedSize <= 360) size = savedSize;
    } catch { /* Storage is optional. */ }
    const remember = (key, value) => {
      try { localStorage.setItem(`td-blog-gallery-${key}`, String(value)); } catch { /* Use this session. */ }
    };
    const ratio = item => {
      const img = item.querySelector('img');
      return (Number(item.dataset.tdWidth) || img?.naturalWidth || 4)
        / (Number(item.dataset.tdHeight) || img?.naturalHeight || 3);
    };
    const place = (item, x, y, width, height) => {
      Object.assign(item.style, { insetInlineStart: `${x}px`, top: `${y}px`, width: `${width}px` });
      item.querySelector('.td-blog-gallery__media').style.height = `${height}px`;
    };
    let frame;
    const layout = () => {
      gallery.dataset.tdMode = mode;
      modes.forEach(input => { input.checked = input.value === mode; });
      slider.value = String(size);
      const width = grid.clientWidth;
      // Hidden blog forms must not be measured as if they were zero-width walls.
      if (!width || !items.length) return;
      grid.classList.add('is-ready');
      if (mode === 'cards') {
        const gap = width < 500 ? 12 : 20;
        const columns = width < 500 ? (size >= 320 ? 1 : 2) : Math.max(2, Math.round((width + gap) / (size + gap)));
        const w = (width - gap * (columns - 1)) / columns;
        const bottoms = Array(columns).fill(0);
        items.forEach(item => { item.style.width = `${w}px`; });
        const captions = items.map(item => item.querySelector('.td-blog-gallery__caption').offsetHeight);
        const ratios = items.map(ratio);
        items.forEach((item, i) => {
          const column = bottoms.indexOf(Math.min(...bottoms));
          const h = w / G.clamp(ratios[i], .6, 2.8);
          place(item, column * (w + gap), bottoms[column], w, h);
          bottoms[column] += h + captions[i] + gap;
        });
        grid.style.height = `${Math.max(...bottoms) - gap}px`;
      } else {
        const gap = mode === 'seamless' ? 0 : 6;
        const compact = width < 500;
        // Narrow screens need readable caption columns even for long scrolls.
        // Images remain contained; only their entry tile proportions are bounded.
        const ratios = items.map(item => compact ? G.clamp(ratio(item), 1, 1.8) : ratio(item));
        const boxes = G.wall(ratios, width, compact ? Math.max(180, size * .65) : size, gap);
        items.forEach((item, i) => { item.style.width = `${boxes[i].width}px`; });
        const captions = items.map(item => hover.matches ? 0 : item.querySelector('.td-blog-gallery__caption').offsetHeight);
        // Touch captions sit below images. Reserve the tallest caption per row
        // so both text and the following row remain clickable and unobscured.
        const rows = new Map();
        boxes.forEach((box, i) => rows.set(box.y, Math.max(rows.get(box.y) || 0, captions[i])));
        let extra = 0;
        const offsets = new Map();
        rows.forEach((height, y) => { offsets.set(y, extra); extra += height; });
        boxes.forEach((box, i) => place(items[i], box.x, box.y + offsets.get(box.y), box.width, box.height));
        grid.style.height = `${Math.max(...boxes.map((box, i) => box.y + offsets.get(box.y) + box.height + captions[i]))}px`;
      }
    };
    const schedule = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(layout); };
    modes.forEach(input => input.addEventListener('change', () => { mode = input.value; remember('mode', mode); schedule(); }));
    slider.addEventListener('input', () => { size = Number(slider.value); remember('size', size); schedule(); });
    let previousWidth = 0;
    new ResizeObserver(entries => {
      const width = entries[0].contentRect.width;
      if (width !== previousWidth) { previousWidth = width; schedule(); }
    }).observe(grid);
    new MutationObserver(schedule).observe(document.documentElement, {
      attributes: true, attributeFilter: ['data-td-blog-index', 'data-td-preset'],
    });
    hover.addEventListener('change', schedule);
    document.fonts?.ready.then(schedule);
    document.fonts?.addEventListener('loadingdone', schedule);
    items.forEach(item => {
      const img = item.querySelector('img');
      if (!img) return;
      const settle = () => {
        item.classList.toggle('is-missing', !img.naturalWidth);
        schedule();
      };
      img.addEventListener('load', settle);
      img.addEventListener('error', settle);
      if (img.complete) settle();
    });
    controls.hidden = false;
    layout();
  });
})();
