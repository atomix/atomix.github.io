---
layout: home
project: atomix
---

<div class="feature intro">
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>
Atomix is an event-driven framework for coordinating fault-tolerant distributed systems built on the Raft consensus algorithm. It provides the building blocks that solve many common distributed systems problems including cluster management, asynchronous messaging, group membership, leader election, distributed concurrency control, partitioning, and replication.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- Simple -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">

<div class="col-sm-7" markdown="1">
{% include sync-tabs-params.html active="#atomic-value:AtomicValue" inactive="#atomic-counter:AtomicCounter,#consistent-map:ConsistentMap,#consistent-multimap:ConsistentMultimap,#distributed-set:DistributedSet,#work-queue:WorkQueue,#document-tree:DocumentTree,#distributed-lock:DistributedLock,#leader-election:LeaderElection,#cluster-management:Cluster Management,#direct-messaging:Direct Messaging,#publish-subscribe:Publish-Subscribe" %}
<div class="tab-content" markdown="1">
<div class="tab-pane active" id="atomic-value" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();

// Get or create an AtomicValue
AtomicValue<String> value = atomix.getAtomicValue("value");

// Set the value
value.set("Hello world!");

// Print the current value
System.out.println(value.get());
```
</div>
<div class="tab-pane" id="atomic-counter" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="consistent-map" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="consistent-multimap" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="distributed-set" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="work-queue" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="document-tree" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="distributed-lock" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="leader-election" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="cluster-management" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="direct-messaging" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
<div class="tab-pane" id="publish-subscribe" markdown="1">
```java
// Create an Atomix instances from a YAML configuration file
Atomix atomix = new Atomix("atomix.yaml");

// Start the instance
atomix.start().join();
```
</div>
</div>
</div>
    <div class="col-sm-5 text-right">
      <h2>Simple</h2>
      <p>Atomix provides a collection of dead simple, asynchronous APIs for sharing mission critical state and solving a variety of common distributed systems problems.</p>
    </div>
    </div>
  </div>
</div>

<!-- Reliable -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Reliable</h2>
        <p>Atomix features reliable data consistency guarantees that are maintained even when machine or network failures occur.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/reliable.svg">
      </div>
    </div>
  </div>
</div>

<!--Resilient -->
<div class="feature gray-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-5 col-sm-offset-1">
        <img class="svg" src="/assets/img/icons/resilient.svg">
      </div>
      <div class="col-sm-6 text-right">
        <h2>Resilient</h2>
        <p>Atomix clusters are resilient to failure, automatically replacing failed replicas as needed without any data loss.</p>
      </div>
    </div>
  </div>
</div>

<!--Scalable -->
<div class="feature white-background">
  <div class="container">
    <div class="row">
      <div class="col-sm-6">
        <h2>Scalable</h2>
        <p>Atomix scales along with the rest of your system, providing high read throughput while maintaining strong write consistency.</p>
      </div>
      <div class="col-sm-5 text-right">
        <img class="svg" src="/assets/img/icons/scalable.svg">
      </div>
    </div>
  </div>
</div>

<!-- Embeddable -->
<!-- <div class="feature gray-background">
  <div class="container">
    <div class="row">
<div class="col-sm-6" markdown="1">
```java
AtomixReplica replica = AtomixReplica.builder(address, members)
  .withTransport(new NettyTransport())
  .withStorage(new Storage(StorageLevel.DISK))
  .build()
  .open()
  .join();
```
</div>
      <div class="col-sm-6 text-right">
        <h2>Embeddable</h2>
        <p>Atomix supports fully embeddable replicas that live in-process, eliminating the need to manage external coordination services.</p>
      </div>
    </div>
  </div>
</div> -->

<!--Learn more -->
<div class="feature get-started">
  <div class="container">
    <div class="row">
      <div class="col-sm-12 text-center">
        <h2>Ready to learn more?</h2>
        <p>
          <a href="/user-manual" class="btn btn-default btn-lg doc-btn">Explore the Docs</a>
        </p>
      </div>
    </div>
  </div>
</div>

<script type='text/javascript'>
// Format tabs
$(function(){
  var $container = $('#sync-tabs');

  updateTabs($container);
  $(window).resize(function(){
    updateTabs($container);
  })

  function updateTabs($tabsContainer){
      var $containerWidth = $tabsContainer.width();
      var tabWidths = [];
      var $tabs = $tabsContainer.find('li');
      $tabs.each(function(index, tab){
        tabWidths.push($(tab).width());
      });

      var formattedTabs = [];
      var maxWidth = $containerWidth;
      var maxWidthSet = false;
      var rowWidth = 0;
      for(var i = tabWidths.length - 1; i >= 0; i--){
          var tabWidth = tabWidths[i];
          if(rowWidth + tabWidth > maxWidth){
            if(!maxWidthSet){
              maxWidth = rowWidth;
              maxWidthSet = true;
            }
            rowWidth = tabWidth;
            formattedTabs.unshift($('<div class="spacer"></div>'));
          }else{
            rowWidth += tabWidth;
          }
          formattedTabs.unshift($tabs.get(i));
      }

      var $tempContainer = $('<div></div>');
      formattedTabs.forEach(function(tab, index){
        $tempContainer.append(tab);
      });
      $tabsContainer.html($tempContainer.html());
  }
});
</script>