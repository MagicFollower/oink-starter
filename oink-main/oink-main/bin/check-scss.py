#!/usr/bin/env python3
"""Build real theme styles and consumer hooks without an external Sass tool."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import tempfile

from test_site import ROOT, run_hugo_process


LIBSASS_WARNING = (
    "WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 "
    "and will be removed in a future release. Use dartsass instead. "
    "See https://gohugo.io/functions/css/sass/#dart-sass"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hugo", default="hugo")
    parser.add_argument("--allow-libsass-warning", action="store_true",
                        help="accept only Hugo 0.168's known LibSass warning")
    args = parser.parse_args()
    hugo = shutil.which(args.hugo)
    if not hugo:
        raise SystemExit(f"Hugo executable not found: {args.hugo}")

    with tempfile.TemporaryDirectory(prefix="oink-scss-") as directory:
        site = Path(directory)
        tools = site / "tools"
        tools.mkdir()
        # A fresh PATH and fresh resources prevent an installed Sass compiler
        # or a previously compiled asset from making this regression pass.
        env = os.environ.copy()
        env.update(PATH=str(tools), GOWORK="off", HUGO_MODULE_WORKSPACE="off",
                   HUGO_RESOURCEDIR=str(site / "resources"))
        env.pop("HUGO_MODULE_REPLACEMENTS", None)
        assert shutil.which("sass", path=env["PATH"]) is None
        files = {
            "hugo.yaml": """baseURL: https://example.org/
title: Sass regression
theme: oink
disableKinds: [taxonomy, term, RSS, sitemap]
markup:
  highlight:
    noClasses: false
""",
            "content/_index.md": "---\ntitle: Sass regression\n---\n",
            "content/docs/_index.md": "---\ntitle: Docs\n---\n",
            "content/docs/api.md": (
                '---\ntitle: API\n---\n\n{{< redoc "/spec.yaml" >}}\n'
                '\n```go\nfunc main() {}\n```\n'
            ),
            "static/spec.yaml": "openapi: 3.0.0\ninfo: {title: Probe, version: '1'}\npaths: {}\n",
            "assets/scss/_variables_project.scss": "$primary: #13579b;\n",
            "assets/scss/_variables_project_after_bs.scss": "$oink_probe_width: 42px;\n",
            "assets/scss/_styles_project.scss": (
                ".oink-scss-hook-probe { width: $oink_probe_width; color: $primary; }\n"
            ),
        }
        for name, content in files.items():
            path = site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        command = [hugo, "--source", str(site), "--themesDir", str(ROOT.parent),
                   "--destination", str(site / "public"), "--cacheDir", str(site / "cache"),
                   "--ignoreCache", "--noBuildLock", "--logLevel", "warn",
                   "--environment", "development"]
        if not args.allow_libsass_warning:
            command.append("--panicOnWarning")
        result = run_hugo_process(command, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        if result.returncode:
            raise SystemExit(output)
        diagnostics = [line for line in output.splitlines() if re.match(r"^(WARN|ERROR)\b", line)]
        unexpected = [line for line in diagnostics
                      if not (args.allow_libsass_warning and line == LIBSASS_WARNING)]
        if unexpected:
            raise SystemExit("Unexpected build diagnostics:\n" + "\n".join(unexpected))
        if args.allow_libsass_warning and LIBSASS_WARNING not in diagnostics:
            raise SystemExit("Expected the Hugo 0.168 LibSass warning to remain visible")
        public = site / "public"
        page = (public / "docs/api/index.html").read_text()
        styles = {path.name: path.read_text() for path in (public / "scss").glob("*.css")}
        main_css = next((css for name, css in styles.items() if name.startswith("main.")), "")
        redoc_css = next((css for name, css in styles.items() if name.startswith("redoc.")), "")
        assert re.search(r"\.oink-scss-hook-probe\s*\{\s*width: 42px;\s*color: #13579b;", main_css), \
            "consumer variable/style hooks were not compiled"
        assert "--bs-primary: #13579b" in main_css, "Bootstrap ignored the consumer primary color"
        assert re.search(r"\[data-bs-theme=['\"]?dark['\"]?\] \.chroma", main_css), \
            "dark Chroma palette is missing"
        assert ".td-redoc" in redoc_css and re.search(r'href="[^"]*redoc[^\"]*\.css"', page), \
            "ReDoc stylesheet was not compiled and linked"
        for diagnostic in diagnostics:
            print(diagnostic)
        print("SCSS checks passed: built-in compiler, main/ReDoc CSS, dark Chroma, and consumer hooks; no Sass on PATH")


if __name__ == "__main__":
    main()
