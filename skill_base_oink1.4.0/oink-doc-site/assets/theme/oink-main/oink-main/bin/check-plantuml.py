#!/usr/bin/env python3
"""Build fresh PlantUML fixtures: local assets, exact source, opt-in and outputs."""

import argparse
import html
import re
import tempfile
from pathlib import Path

from test_site import ROOT, run_hugo_process, theme_warnings


SOURCE = '@startuml\nAlice -> Bob: 中文 <tag> & "quotes"\n@enduml\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hugo', default='hugo')
    args = parser.parse_args()
    errors = []
    cases = {
        'default': '',
        'disabled': 'plantuml: false',
        'local': 'plantuml: true',
        'local-map': 'plantuml:\n    enable: true',
        'server': 'plantuml:\n    enable: true\n    svg_image_url: https://render.example/svg/',
        'invalid': 'plantuml:\n    enable: true\n    svg_image_url: javascript:alert(1)',
        'invalid-false': 'plantuml:\n    enable: true\n    svg_image_url: false',
        'invalid-empty-map': 'plantuml:\n    enable: true\n    svg_image_url: {}',
        'invalid-zero': 'plantuml:\n    enable: true\n    svg_image_url: 0',
    }
    with tempfile.TemporaryDirectory(prefix='oink-plantuml-') as tmp:
        site = Path(tmp)
        (site / 'content/docs').mkdir(parents=True)
        (site / 'content/docs/diagram.md').write_text(
            '---\ntitle: PlantUML\noutputs: [HTML, Print, Markdown]\n---\n\n```plantuml\n' + SOURCE + '```\n')
        (site / 'content/docs/plain.md').write_text('---\ntitle: Plain\n---\n\nNo diagrams.\n')
        for name, params in cases.items():
            (site / 'hugo.yaml').write_text(
                'baseURL: https://example.org/sub/\ntitle: PlantUML fixture\n'
                f'theme: {ROOT.name}\n' + (f'params:\n  {params}\n' if params else ''))
            result = run_hugo_process(
                [args.hugo, '--source', str(site), '--themesDir', str(ROOT.parent),
                 '--destination', str(site / 'public'), '--cleanDestinationDir', '--logLevel', 'warn'],
                capture_output=True, text=True, check=False)
            log = result.stdout + result.stderr
            print(log, end='')
            if result.returncode:
                errors.append(f'{name}: build failed')
                continue
            output = site / 'public'
            page = (output / 'docs/diagram/index.html').read_text()
            block = re.search(r'<code class="language-plantuml">(.*?)</code>', page, re.S)
            if not block or html.unescape(block[1]) != SOURCE.rstrip('\n'):
                errors.append(f'{name}: source text was changed or double escaped')
            local = name in ('local', 'local-map')
            if ('type="module" src="/sub/js/chunks/plantuml-browser-' in page) != local:
                errors.append(f'{name}: browser renderer selection is wrong')
            if ('/sub/js/chunks/plantuml-en.' in page) != (name == 'server'):
                errors.append(f'{name}: legacy server renderer selection is wrong')
            if ('pako' in page or 'viz-global' in page):
                errors.append(f'{name}: engine leaked into global scripts')
            assets = list((output / 'third_party/plantuml').glob('*.js'))
            if bool(assets) != local or (local and len(assets) != 2):
                errors.append(f'{name}: expected only the two used local engine assets')
            if local:
                runtime = next((output / 'js/chunks').glob('plantuml-browser-*.js')).read_text()
                for asset in assets:
                    if '/sub/third_party/plantuml/' + asset.name not in runtime:
                        errors.append(f'{name}: asset lost the deployment prefix: {asset.name}')
                    original = ROOT / 'assets/third_party/plantuml' / ('viz-global.js' if asset.name.startswith('viz-global.') else 'plantuml.js')
                    if asset.read_bytes() != original.read_bytes():
                        errors.append(f'{name}: precompiled engine was transformed')
            if ('data-td-diagram-zoom-dialog' in page) != local:
                errors.append(f'{name}: shared local viewer selection is wrong')
            if local and ('/sub/js/chunks/diagram.' not in page):
                errors.append(f'{name}: shared scheduler is missing')
            plain = (output / 'docs/plain/index.html').read_text()
            if 'js/chunks/diagram.' in plain:
                errors.append(f'{name}: plain page loads the diagram scheduler')
            if 'js/chunks/plantuml-' in plain:
                errors.append(f'{name}: plain page loads PlantUML')
            print_page = (output / '_print/docs/diagram/index.html').read_text()
            if 'js/chunks/plantuml-' in print_page or 'language-plantuml' not in print_page:
                errors.append(f'{name}: Print must retain source without a renderer')
            markdown = (output / 'docs/diagram/index.md').read_text()
            if SOURCE.strip() not in markdown:
                errors.append(f'{name}: Markdown lost original PlantUML source')
            warnings = theme_warnings(log)
            if name.startswith('invalid'):
                if not any('params.plantuml' in warning for warning in warnings):
                    errors.append('invalid endpoint did not warn')
            elif warnings:
                errors.append(f'{name}: unexpected warnings: {warnings}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PlantUML output check passed ({len(cases)} configurations, exact source, local assets and static outputs)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
