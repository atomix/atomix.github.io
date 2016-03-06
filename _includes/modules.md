{% for m in site.data.modules %}
* `{{ m.module }}` - [{{ m.resources |  | join: '], [' }}]{% endfor %}