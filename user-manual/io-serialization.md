---
layout: content
menu: user-manual
title: I/O & Serialization
---


## I/O & Serialization

Copycat provides a custom I/O and serialization framework that it uses for all disk and network I/O. The I/O framework is designed to provide an abstract API for reading and writing bytes on disk, in memory, and over a network in a way that is easily interchangeable and reduces garbage collection and unnecessary memory copies.

The I/O subproject consists of several essential components:

* [Buffers](#buffers) - A low-level buffer abstraction for reading/writing bytes in memory or on disk
* [Serialization](#serialization) - A low-level serialization framework built on the `Buffer` API
* [Storage](#storage) - A low-level ordered and indexed, self-cleaning `Log` designed for use in the [Raft consensus algorithm][Raft]
* [Transport](#transports) - A low-level generalization of asynchronous client-server messaging

### Buffers

Copycat provides a [Buffer][Buffer] abstraction that provides a common interface to both memory and disk. Currently, four buffer types are provided:

* `HeapBuffer` - on-heap `byte[]` backed buffer
* `DirectBuffer` - off-heap `sun.misc.Unsafe` based buffer
* `MemoryMappedBuffer` - `MappedByteBuffer` backed buffer
* `FileBuffer` - `RandomAccessFile` backed buffer

The [Buffer][Buffer] interface implements `BufferInput` and `BufferOutput` which are functionally similar to Java's `DataInput` and `DataOutput` respectively. Additionally, features of how bytes are managed are intentionally similar to [ByteBuffer][ByteBuffer]. Copycat's buffers expose many of the same methods such as `position`, `limit`, `flip`, and others. Additionally, buffers are allocated via a static `allocate` method similar to `ByteBuffer`:

```java
Buffer buffer = DirectBuffer.allocate(1024);
```

Buffers are dynamically allocated and allowed to grow over time, so users don't need to know the number of bytes they're expecting to use when the buffer is created.

The `Buffer` API exposes a set of `read*` and `write*` methods for reading and writing bytes respectively:

```java
Buffer buffer = HeapBuffer.allocate(1024);
buffer.writeInt(1024)
  .writeUnsignedByte(255)
  .writeBoolean(true)
  .flip();

assert buffer.readInt() == 1024;
assert buffer.readUnsignedByte() == 255;
assert buffer.readBoolean();
```

See the [Buffer API documentation][Buffer] for more detailed usage information.

#### Bytes

All `Buffer` instances are backed by a `Bytes` instance which is a low-level API over a fixed number of bytes. In contrast to `Buffer`, `Bytes` do not maintain internal pointers and are not dynamically resizeable.

`Bytes` can be allocated in the same way as buffers, using the respective `allocate` method:

```java
FileBytes bytes = FileBytes.allocate(new File("path/to/file"), 1024);
```

Additionally, bytes can be resized via the `resize` method:

```java
bytes.resize(2048);
```

When in-memory bytes are resized, the memory will be copied to a larger memory space via `Unsafe.copyMemory`. When disk backed bytes are resized, disk space will be allocated by resizing the underlying file.

#### Buffer pools

All buffers can optionally be pooled and reference counted. Pooled buffers can be allocated via a `PooledAllocator`:

```java
BufferAllocator allocator = new PooledHeapAllocator();

Buffer buffer = allocator.allocate(1024);
```

Copycat tracks buffer references by implementing the `ReferenceCounted` interface. When pooled buffers are allocated, their `ReferenceCounted.references` count will be `1`. To release the buffer back to the pool, the reference count must be decremented back to `0`:

```java
// Release the reference to the buffer
buffer.release();
```

Alternatively, `Buffer` extends `AutoCloseable`, and buffers can be released back to the pool regardless of their reference count by calling `Buffer.close`:

```java
// Release the buffer back to the pool
buffer.close();
```

### Serialization

Copycat provides an efficient custom serialization framework that's designed to operate on both disk and memory via a common [Buffer](#buffers) abstraction.

#### Serializer

Copycat's serializer can be used by simply instantiating a [Serializer][Serializer] instance:

```java
// Create a new Serializer instance with an unpooled heap allocator
Serializer serializer = new Serializer(new UnpooledHeapAllocator());

// Register the Person class with a serialization ID of 1
serializer.register(Person.class, 1);
```

Objects are serialized and deserialized using the `writeObject` and `readObject` methods respectively:

```java
// Create a new Person object
Person person = new Person(1234, "Jordan", "Halterman");

// Write the Person object to a newly allocated buffer
Buffer buffer = serializer.writeObject(person);

// Flip the buffer for reading
buffer.flip();

// Read the Person object
Person result = serializer.readObject(buffer);
```

The `Serializer` class supports serialization and deserialization of `CopycatSerializable` types, types that have an associated `Serializer`, and native Java `Serializable` and `Externalizable` types, with `Serializable` being the most inefficient method of serialization.

Additionally, Copycat support copying objects by serializing and deserializing them. To copy an object, simply use the `Serializer.copy` method:

```java
Person copy = serializer.copy(person);
```

All `Serializer` instance constructed by Copycat use `ServiceLoaderTypeResolver`. Copycat registers internal `CopycatSerializable` types via `META-INF/services/net.kuujo.copycat.io.serializer.CopycatSerializable`. To register additional serializable types, create an additional `META-INF/services/net.kuujo.copycat.io.serializer.CopycatSerializable` file and list serializable types in that file.

`META-INF/services/net.kuujo.copycat.io.serializer.CopycatSerializable`

```
com.mycompany.SerializableType1
com.mycompany.SerializableType2
```

Users should annotate all `CopycatSerializable` types with the `@SerializeWith` annotation and provide a serialization ID for efficient serialization. Alley cat reserves serializable type IDs `128` through `255` and Copycat reserves `256` through `512`.

#### Pooled object deserialization

Copycat's serialization framework integrates with [object pools](#buffer-pools) to support allocating pooled objects during deserialization. When a `Serializer` instance is used to deserialize a type that implements `ReferenceCounted`, Copycat will automatically create new objects from a `ReferencePool`:

```java
Serializer serializer = new Serializer();

// Person implements ReferenceCounted<Person>
Person person = serializer.readObject(buffer);

// ...do some stuff with Person...

// Release the Person reference back to Copycat's internal Person pool
person.close();
```

#### Serializable type resolution

Serializable types are resolved by a user-provided [SerializableTypeResolver][SerializableTypeResolver]. By default, Copycat uses a combination of the 

Copycat always registers serializable types provided by [PrimitiveTypeResolver][PrimitiveTypeResolver] and [JdkTypeResolver][JdkTypeResolver], including the following types:

* Primitive types
* Primitive wrappers
* Primitive arrays
* Primitive wrapper arrays
* `String`
* `Class`
* `BigInteger`
* `BigDecimal`
* `Date`
* `Calendar`
* `TimeZone`
* `Map`
* `List`
* `Set`

Additionally, Copycat's Raft implementation uses [ServiceLoaderTypeResolver][ServiceLoaderTypeResolver] to register types registered via Java's `ServiceLoader`

Users can resolve custom serializers at runtime via `Serializer.resolve` methods or register specific types via `Serializer.register` methods.

To register a serializable type with an `Serializer` instance, the type must generally meet one of the following conditions:

* Implement `CopycatSerializable`
* Implement `Externalizable`
* Provide a `Serializer` class
* Provide a `SerializerFactory`

```java
Serializer serializer = new Serializer();
serializer.register(Foo.class, FooSerializer.class);
serializer.register(Bar.class);
```

Additionally, Copycat supports serialization of `Serializable` and `Externalizable` types without registration, but this mode of serialization is inefficient as it requires that Copycat serialize the full class name as well.

#### Registration identifiers

Types explicitly registered with a `Serializer` instance can provide a registration ID in lieu of serializing class names. If given a serialization ID, Copycat will write the serializable type ID to the serialized `Buffer` instance of the class name and use the ID to locate the serializable type upon deserializing the object. This means *it is critical that all processes that register a serializable type use consistent identifiers.*

To register a serializable type ID, pass the `id` to the `register` method:

```java
Serializer serializer = new Serializer();
serializer.register(Foo.class, FooSerializer.class, 1);
serializer.register(Bar.class, 2);
```

Valid serialization IDs are between `0` and `65535`. However, Copycat reserves IDs `128` through `255` for internal use. Attempts to register serializable types within the reserved range will result in an `IllegalArgumentException`.

#### CopycatSerializable

Instead of writing a custom `TypeSerializer`, serializable types can also implement the `CopycatSerializable` interface. The `CopycatSerializable` interface is synonymous with Java's native `Serializable` interface. As with the `Serializer` interface, `CopycatSerializable` exposes two methods which receive both a [Buffer](#buffers) and a `Serializer`:

```java
public class Foo implements CopycatSerializable {
  private int bar;
  private Baz baz;

  public Foo() {
  }

  public Foo(int bar, Baz baz) {
    this.bar = bar;
    this.baz = baz;
  }

  @Override
  public void writeObject(Buffer buffer, Serializer serializer) {
    buffer.writeInt(bar);
    serializer.writeObject(baz);
  }

  @Override
  public void readObject(Buffer buffer, Serializer serializer) {
    bar = buffer.readInt();
    baz = serializer.readObject(buffer);
  }
}
```

For the most efficient serialization, it is essential that you associate a serializable type `id` with all serializable types. Type IDs can be provided during type registration or by implementing the `@SerializeWith` annotation:

```java
@SerializeWith(id=1)
public class Foo implements CopycatSerializable {
  ...

  @Override
  public void writeObject(Buffer buffer, Serializer serializer) {
    buffer.writeInt(bar);
    serializer.writeObject(baz);
  }

  @Override
  public void readObject(Buffer buffer, Serializer serializer) {
    bar = buffer.readInt();
    baz = serializer.readObject(buffer);
  }
}
```

For classes annotated with `@SerializeWith`, the ID will automatically be retrieved during registration:

```java
Serializer serializer = new Serializer();
serializer.register(Foo.class);
```

#### TypeSerializer

At the core of the serialization framework is the [TypeSerializer][TypeSerializer]. The `TypeSerializer` is a simple interface that exposes two methods for serializing and deserializing objects of a specific type respectively. That is, serializers are responsible for serializing objects of other types, and not themselves. Copycat provides this separate serialization interface in order to allow users to create custom serializers for types that couldn't otherwise be serialized by Copycat.

The `TypeSerializer` interface consists of two methods:

```java
public class FooSerializer implements TypeSerializer<Foo> {
  @Override
  public void write(Foo foo, BufferWriter writer, Serializer serializer) {
    writer.writeInt(foo.getBar());
  }

  @Override
  @SuppressWarnings("unchecked")
  public Foo read(Class<Foo> type, BufferReader reader, Serializer serializer) {
    Foo foo = new Foo();
    foo.setBar(reader.readInt());
  }
}
```

To serialize and deserialize an object, simply write to and read from the passed in `BufferWriter` or `BufferReader` instance respectively. In addition to the reader/writer, the `Serializer` that is serializing or deserializing the instance is also passed in. This allows the serializer to serialize or deserialize subtypes as well:

```java
public class FooSerializer implements TypeSerializer<Foo> {
  @Override
  public void write(Foo foo, BufferWriter writer, Serializer serializer) {
    writer.writeInt(foo.getBar());
    Baz baz = foo.getBaz();
    serializer.writeObject(baz, writer);
  }

  @Override
  @SuppressWarnings("unchecked")
  public Foo read(Class<Foo> type, BufferReader reader, Serializer serializer) {
    Foo foo = new Foo();
    foo.setBar(reader.readInt());
    foo.setBaz(serializer.readObject(reader));
  }
}
```

Copycat comes with a number of native `TypeSerializer` implementations, for instance `ListSerializer`:

```java
public class ListSerializer implements TypeSerializer<List> {
  @Override
  public void write(List object, BufferWriter writer, Serializer serializer) {
    writer.writeUnsignedShort(object.size());
    for (Object value : object) {
      serializer.writeObject(value, writer);
    }
  }

  @Override
  @SuppressWarnings("unchecked")
  public List read(Class<List> type, BufferReader reader, Serializer serializer) {
    int size = reader.readUnsignedShort();
    List object = new ArrayList<>(size);
    for (int i = 0; i < size; i++) {
      object.add(serializer.readObject(reader));
    }
    return object;
  }

}
```

### Storage

The [Storage][Storage] API provides an interface to a low-level ordered and index self-cleaning log designed for use in the [Raft consensus algorithm](#raft-consensus-algorithm). Each server in a Copycat cluster writes state changes to disk via the [Log][Log]. Logs are built on top of Copycat's [Buffer](#buffers) abstraction, so the backing store can easily be switched between memory and disk.

When constructing a `RaftServer` or `CopycatReplica`, users must provide the server with a `Storage` instance which controls the underlying `Log`. `Storage` objects are built via the storage [Builder](#builders):

```java
Storage storage = Storage.builder()
  .withDirectory("logs")
  .withStorageLevel(StorageLevel.DISK)
  .build();
```

#### Log

*Note: Much of the following is relevant only to Copycat internals*

Underlying the [Storage][Storage] API is the [Log][Log].

```java
Log log = storage.open();
```

The `Log` is an ordered and indexed list of entries stored on disk in a series of files called *segments*. Each segment file represents range of entries in the overall log and is backed by a file-based [buffer](#buffers). Entries are serialized to disk using Copycat's [serialization framework](#serialization).

Entries can only be appended to the log:

```java
try (MyEntry entry = log.create(MyEntry.class)) {
  entry.setFoo("foo");
  entry.setBar(1);
  log.append(entry);
}
```

Segment buffers are backed by an *offset index*. The offset index is responsible for tracking the offsets and positions of entries in the segment. Indexes are built in memory from segment entries as they're written to disk. In order to preserve disk/memory space, the index stores entry indices as offsets relative to the beginning of each segment. When a segment is loaded from disk, the in-memory index is recreated from disk. Additionally, each segment is limited to a maximum size of `Integer.MAX_VALUE` so that the position of an entry cannot exceed 4 bytes. This means each entry in the index consumes only 8 bytes - 4 for the offset and 4 for the position.

When entries are read from a segment, the offset index is used to locate the starting position of the entry in the segment file. To locate an entry, the index uses a [binary search algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm) to locate the appropriate offset within the index buffer. Given the offset, the related *position* is used to seek to the appropriate position in the segment file where the entry is read and deserialized.

Offset indexes are also responsible for tracking entries that have been [cleaned from the segment](#log-cleaning). When entries are cleaned from the log, a flag is set in the owning segment's offset index to indicate that the entry is awaiting compaction. Clean flags are stored in a bit set in memory, so each segment consumes `[num entries] / 8` additional bytes of memory for delete bits.

Entries in the log are always keyed by an `index` - a monotonically increasing 64-bit number. But because of the nature of [log cleaning](#log-cleaning) - allowing entries to arbitrarily be removed from the log - the log and its segments are designed to allow entries to be missing *at any point in the log*. Over time, it is expected that entries will be cleaned and compacted out of the log. The log and segments always store entries in as compact a form as possible. Offset indexes contain only entries that have been physically written to the segment, and indexes are searched with a binary search algorithm during reads.

#### Log cleaning

The most critical component of Copycat's [Log][Log] design relates to log cleaning. Cleaning is the process of removing arbitrary entries from the log over time. Copycat's `Log` is designed to facilitate storing operations on a state machine. Over time, as state machine operations become irrelevant to a state machine's state, they can be marked for deletion from the log by the `clean(index)` method.

When an entry is `clean`ed from the log, the entry is internally marked for deletion from the log. Thereafter, the entry will no longer be accessible via the `Log` interface. Internally, the log sets an in-memory bit indicating that the entry at the given index is awaiting compaction.

Note, though, that calling `clean` does not mean that an entry will be removed from disk or memory. Entries are only removed once the log rolls over to a new `Segment` or the user explicitly `clean`s the log:

```java
log.cleaner().clean();
```

When the log is cleaned, a background thread will evaluate the log's segments to determine whether they need to be compacted. Currently, segments are compacted based on two factors:

* The number of entries that have been `clean`ed from the segment
* The number of times the segment has been previously cleaned

For a segment that has not yet been cleaned, cleaning will take place only once 50% of the entries in the segment have been `clean`ed. The second time the segment is cleaned, 25% of its entries must have been `clean`ed, and so forth.

Log cleaning works by simply creating a new segment at the start of the segment being cleaned and iterating over the entries in the segment, rewriting live entries from the old segment to the new segment, and discarding entries that have been `clean`ed:

![Combining segments](http://s12.postimg.org/jhdthtpct/Combined_Segment_Compaction_New_Page_1.png)

This graphic depicts the cleaning process. As entries are appended to the log, some older entries are marked for cleaning (the grey boxes). During the log cleaning process, a background thread iterates through the segment being cleaned (the bold boxes) and discards entries that have been `clean`ed (the bold white boxes). In the event that two neighboring segments have been compacted small enough to form a single segment, they will be combined into one segment (the last row). This ensures that the number of open files remains more or less constant as entries are cleaned from the log.

### Transports

The [Transport][Transport] API provides an interface that generalizes the concept of asynchronous client-server messaging. `Transport` objects control the communication between all clients and servers throughout a Copycat cluster. Therefore, it is essential that all nodes in a cluster use the same transport.

The [NettyTransport][NettyTransport] is a TCP-based transport built on [Netty](http://netty.io/) 4.

```java
Transport transport = new NettyTransport();
```

For test cases, Copycat provides the [LocalTransport][LocalTransport] which mimics the behavior of a network based transport via threads and executors.

[Javadoc]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/
[CAP]: https://en.wikipedia.org/wiki/CAP_theorem
[Raft]: https://raft.github.io/
[Executor]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/Executor.html
[CompletableFuture]: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html
[collections]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections.html
[atomic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic.html
[coordination]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination.html
[copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat.html
[protocol]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol.html
[io]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io.html
[serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer.html
[transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport.html
[storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage.html
[utilities]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util.html
[Copycat]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Copycat.html
[CopycatReplica]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatReplica.html
[CopycatClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/CopycatClient.html
[Resource]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/Resource.html
[Transport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/Transport.html
[LocalTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/LocalTransport.html
[NettyTransport]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/transport/NettyTransport.html
[Storage]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Storage.html
[Log]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/storage/Log.html
[Buffer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/Buffer.html
[BufferReader]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferReader.html
[BufferWriter]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/BufferWriter.html
[Serializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/Serializer.html
[CopycatSerializable]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/CopycatSerializable.html
[TypeSerializer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/TypeSerializer.html
[SerializableTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[PrimitiveTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[JdkTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/SerializableTypeResolver.html
[ServiceLoaderTypeResolver]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/io/serializer/ServiceLoaderTypeResolver.html
[RaftServer]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftServer.html
[RaftClient]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/RaftClient.html
[Session]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/session/Session.html
[Operation]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Operation.html
[Command]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Command.html
[Query]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Query.html
[Commit]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/Commit.html
[ConsistencyLevel]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/raft/protocol/ConsistencyLevel.html
[DistributedAtomicValue]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/atomic/DistributedAtomicValue.html
[DistributedSet]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedSet.html
[DistributedMap]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/collections/DistributedMap.html
[DistributedLock]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLock.html
[DistributedLeaderElection]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedLeaderElection.html
[DistributedTopic]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/coordination/DistributedTopic.html
[Builder]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Builder.html
[Listener]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/Listener.html
[Context]: http://kuujo.github.io/copycat/api/{{ site.javadoc-version }}/net/kuujo/copycat/util/concurrent/Context.html