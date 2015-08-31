---
layout: content
menu: none
title: User Manual
---

Documentation is still under active development. The following documentation is loosely modeled on the structure of modules as illustrated in the [Javadoc][Javadoc]. Docs will be updated frequently until a release, so check back for more! If you would like to request specific documentation, please [submit a request](http://github.com/kuujo/copycat/issues).

[Javadoc]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/

<div id="user-manual-index">
{% capture usermanual %}{% include user-manual-menu.md %}{% endcapture %}
{{ usermanual | markdownify }}
</div>