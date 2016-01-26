---
layout: content
project: atomix
title: Documenation
---

{:.no-margin-top}
<div class="conatiner">
  <div class="row">
    <div class="col-md-4">
      <div class="docs-logo-heading"><img src="/assets/img/atomix.png" /><h2>Atomix</h2></div>
      <div id="docs-index">
{% capture usermanual %}{% include atomix/docs-menu.md %}{% endcapture %}
{{ usermanual | markdownify }}
      </div>
    </div>
    <div class="col-md-4">
      <div class="docs-logo-heading"><img src="/assets/img/copycat.png" /><h2>Copycat</h2></div>
      <div id="docs-index">
{% capture usermanual %}{% include copycat/docs-menu.md %}{% endcapture %}
{{ usermanual | markdownify }}
      </div>
    </div>
    <div class="col-md-4">
      <div class="docs-logo-heading"><img src="/assets/img/catalyst.png" /><h2>Catalyst</h2></div>
      <div id="docs-index">
{% capture usermanual %}{% include catalyst/docs-menu.md %}{% endcapture %}
{{ usermanual | markdownify }}
      </div>
    </div>
  </div>
</div>

{% include common-links.html %}