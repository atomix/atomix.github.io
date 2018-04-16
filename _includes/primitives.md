{% for g in site.data.primitives %}
* {{ g.group }} - [{{ g.sections |  | join: '], [' }}]{% endfor %}