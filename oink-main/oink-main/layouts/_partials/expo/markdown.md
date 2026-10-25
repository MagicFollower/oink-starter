{{- range partialCached "expo/items.html" . .RelPermalink }}

## {{ partial "content/markdown-escape.html" .title }}

![{{ partial "content/markdown-escape.html" .alt | replaceRE `[\r\n]` " " }}]({{ partial "content/markdown-url.html" .original }})
{{ with .caption }}
{{ partial "content/markdown-escape.html" . }}
{{ end }}{{ with .byline }}
{{ partial "content/markdown-escape.html" . }}
{{ end }}
{{ end -}}
