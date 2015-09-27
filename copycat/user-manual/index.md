---
layout: content
project: copycat
title: User Manual
---

{:.no-margin-top}
Documentation is still under active development. The following documentation is loosely modeled on the structure of modules as illustrated in the [Javadoc][CopycatJavadoc]. Docs will be updated frequently until a release, so check back for more! If you would like to request specific documentation, please [submit a request](http://github.com/atomix/copycat/issues).

<div id="user-manual-index">
{% capture usermanual %}{% include copycat/user-manual-menu.md %}{% endcapture %}
{{ usermanual | markdownify }}
</div>

{% include common-links.html %}