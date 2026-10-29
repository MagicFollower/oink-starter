{{ if eq .Site.Params.markmap true }}
(function () {
  'use strict';

  var fitLabel = {{ i18n "ui_diagram_fit" | jsonify | safeJS }};

  function enhance(container, source) {
    var api = window.markmap;
    var transformer = new api.Transformer(api.autoLoader.transformPlugins);
    transformer.urlBuilder.setProvider('oink', api.autoLoader.provider);
    transformer.urlBuilder.provider = 'oink';
    // Preserve the autoloader's normalization for indented outlines and YAML.
    var lines = source.split('\n');
    var indent = lines.reduce(function (minimum, line) {
      return line.trim() ? Math.min(minimum, line.match(/^\s*/)[0].length) : minimum;
    }, Infinity);
    var content = lines.map(function (line) { return line.slice(indent); }).join('\n').trim();
    var map, svg, mounting, ready, frame;
    var manual = false;
    var size = '';
    var generation = 0;

    function fit() {
      if (!ready || !svg.getBoundingClientRect().width) return;
      // Layout changes should not animate or override a reader's gesture.
      var duration = map.options.duration;
      map.options.duration = 0;
      map.fit();
      map.options.duration = duration;
    }

    async function render() {
      var version = ++generation;
      var result = transformer.transform(content);
      var assets = transformer.getUsedAssets(result.features);
      await Promise.all([api.loadCSS(assets.styles || []), api.loadJS(assets.scripts || [])]);
      if (version !== generation) return;
      var options = api.deriveOptions(result.frontmatter && result.frontmatter.markmap);
      options.autoFit = false;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) options.duration = 0;
      await map.setData(result.root, options);
      await document.fonts.ready;
      ready = true;
      if (!manual) fit();
    }

    function resize() {
      frame = 0;
      if (!container.getBoundingClientRect().width || window.matchMedia('print').matches) return;
      if (!map) {
        if (mounting) return;
        mounting = true;
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        var reset = document.createElement('button');
        reset.type = 'button';
        reset.className = 'td-markmap__fit';
        reset.textContent = fitLabel;
        reset.addEventListener('click', function () { manual = false; fit(); });
        container.replaceChildren(svg, reset);
        map = api.Markmap.create(svg, { embedGlobalCSS: false });
        map.zoom.on('start.oink', function (event) {
          if (event.sourceEvent) manual = true;
        });
        // Markmap's scroll-for-pan mode applies its transform programmatically.
        svg.addEventListener('wheel', function () { manual = true; }, { passive: true });
        transformer.hooks.retransform.tap(function () { render().catch(failed); });
        render().catch(failed);
      }
      var rect = svg.getBoundingClientRect();
      var next = rect.width + ':' + rect.height;
      if (next === size) return;
      size = next;
      if (!manual) fit();
    }

    function schedule() {
      if (!frame) frame = requestAnimationFrame(resize);
    }

    function failed(error) {
      console.error('Markmap:', error);
      container.textContent = source;
    }

    if (window.ResizeObserver) new ResizeObserver(schedule).observe(container);
    else window.addEventListener('resize', schedule);
    document.addEventListener('td:tab-shown', schedule);
    document.addEventListener('toggle', schedule, true);
    window.addEventListener('afterprint', schedule);
    schedule();
  }

  Array.prototype.forEach.call(
    document.querySelectorAll('.language-markmap'),
    function (code) {
      var pre = code.parentNode;
      if (!pre || !pre.parentNode) return;
      var container = document.createElement('div');
      container.className = 'markmap';
      container.textContent = pre.textContent;
      pre.parentNode.replaceChild(container, pre);
      var source = container.textContent;
      window.markmap.autoLoader.ready.then(function () { enhance(container, source); });
    },
  );

})();
{{ end }}
