---
layout: content
project: atomix
title: Community
---

{:.no-margin-top}
<div class="container community">
  <div class="row">
    <div class="col-sm-3">
      <h2 id="support">Support</h2>
    </div>
    <div class="col-sm-3">
      <h3>Discussion</h3>
      <ul>
        <li><a href="https://gitter.im/atomix/atomix">Gitter Chat</a></li>
        <li><a href="https://groups.google.com/forum/#!forum/atomixio">User Group</a></li>
      </ul>
    </div>
    <div class="col-sm-3">
      <h3>Issue Tracking</h3>
      <ul>
        <li><a href="https://github.com/atomix/atomix/issues">Atomix</a></li>
        <li><a href="https://github.com/atomix/copycat/issues">Copycat</a></li>
        <li><a href="https://github.com/atomix/catalyst/issues">Catalyst</a></li>
      </ul>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3">
      <h2 id="#contributing">Contributing</h2>
    </div>
    <div class="col-sm-8">
      <h3>Source</h3>
      <ul>
        <li><a href="https://github.com/atomix/atomix">Atomix</a></li>
        <li><a href="https://github.com/atomix/copycat">Copycat</a></li>
        <li><a href="https://github.com/atomix/catalyst">Catalyst</a></li>
      </ul>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3">
      <h2 id="committers">Committers</h2>
    </div>
    <div class="col-sm-9">
      <div class="row">
  {% for contributor in site.data.committers %}
        <div class="col-sm-4">
  {% include contributor.html %}
        </div>
  {% endfor %}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3">
      <h2 id="contributors">Contributors</h2>
    </div>
    <div class="col-sm-9">
      <div class="row">
  {% for contributor in site.data.contributors %}
        <div class="col-sm-4">
  {% include contributor.html %}
        </div>
  {% endfor %}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-3">
      <h2 id="thanks">Thanks</h2>
    </div>
    <div class="col-sm-8">
      <p>
        YourKit is kindly supporting open source projects with its full-featured Java Profiler.
        YourKit, LLC is the creator of innovative and intelligent tools for profiling
        Java and .NET applications. Take a look at YourKit's leading software products:
        <a href="http://www.yourkit.com/java/profiler/index.jsp">YourKit Java Profiler</a> and
        <a href="http://www.yourkit.com/.net/profiler/index.jsp">YourKit .NET Profiler</a>.
      </p>
    </div>
  </div>
</div>

{% include common-links.html %}