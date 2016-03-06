{% for g in site.data.resources %}
* {{ g.group }} - [{{ g.resources |  | join: '], [' }}]{% endfor %}