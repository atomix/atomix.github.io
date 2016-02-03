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
    <div class="col-sm-9">
      <div class="row">
        <div class="col-sm-6">
          <h3>Gitter Chat</h3>
          <p><a href="https://gitter.im/atomix/atomix">Gitter Chat</a> is a way for users to ask questions and chat with the Atomix team. Feel free to leave a message even if we're not around, and we'll respond when available.</p>
        </div>
        <div class="col-sm-6">
          <h3>Google Group</h3>
          <p>The <a href="https://groups.google.com/forum/#!forum/atomixio">Google Group</a> is another way to ask questions and communicate with the Atomix team and other users.</p>
        </div>
      </div>
      <div class="row">
        <div class="col-sm-6">
          <h3>Github Issues</h3>
          <p>Bugs and feature requests can be filed as issues on Github. Issues are tracked separately for each project:</p>
          <ul>
            <li><a href="https://github.com/atomix/atomix/issues">Atomix</a></li>
            <li><a href="https://github.com/atomix/copycat/issues">Copycat</a></li>
            <li><a href="https://github.com/atomix/catalyst/issues">Catalyst</a></li>
          </ul>
        </div>
        <div class="col-sm-6">
          <h3>Pay It Forward</h3>
          <p>The Atomix stack is a volunteer effort. Help support the projects by answering questions and most importantly, by spreading the word. Your help makes a difference!</p>
        </div>
      </div>
    </div>
  </div>
  <div class="row row-tall">
    <div class="col-sm-3">
      <h2 id="#contributing">Contributing</h2>
    </div>
    <div class="col-sm-8">
      <p>Bug fixes and feature <a href="https://github.com/atomix">contributions</a> in the form of pull requests are welcome. If you have a non-trivial change in mind that you'd like to discuss, feel free to ping us on <a href="https://gitter.im/atomix/atomix">Gitter</a> or the <a href="https://groups.google.com/forum/#!forum/atomixio">user group</a>.</p>
    </div>
  </div>
  <div class="row row-tall">
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