---
layout: docs
project: catalyst
menu: docs
title: Buffers
first-section: buffers
---

{:.no-margin-top}
Catalyst provides a [`Buffer`][Buffer] abstraction that provides a common interface to both memory and disk. Currently, four buffer types are provided:

* `HeapBuffer` - on-heap `byte[]` backed buffer
* `DirectBuffer` - off-heap `sun.misc.Unsafe` based buffer
* `MemoryMappedBuffer` - `MappedByteBuffer` backed buffer
* `FileBuffer` - `RandomAccessFile` backed buffer

The [`Buffer`][Buffer] interface implements [`BufferInput`][BufferInput] and [`BufferOutput`][BufferOutput] which are functionally similar to Java's `DataInput` and `DataOutput` respectively. Additionally, features of how bytes are managed are intentionally similar to [`ByteBuffer`][ByteBuffer]. Catalyst's buffers expose many of the same methods such as `position`, `limit`, `flip`, and others. Additionally, buffers are allocated via a static `allocate` method similar to [`ByteBuffer`][ByteBuffer]:

```java
Buffer buffer = DirectBuffer.allocate(1024);
```

Buffers are dynamically allocated and allowed to grow over time, so users don't need to know the number of bytes they're expecting to use when the buffer is created.

The [`Buffer`][Buffer] API exposes a set of `read*` and `write*` methods for reading and writing bytes respectively:

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

## Bytes

All `Buffer` instances are backed by a [`Bytes`][Bytes] instance which is a low-level API over a fixed number of bytes. In contrast to [`Buffer`][Buffer], [`Bytes`][Bytes] do not maintain internal pointers and are not dynamically resizeable.

[`Bytes`][Bytes] can be allocated in the same way as buffers, using the respective `allocate` method:

```java
FileBytes bytes = FileBytes.allocate(new File("path/to/file"), 1024);
```

Additionally, bytes can be resized via the `resize` method:

```java
bytes.resize(2048);
```

When in-memory bytes are resized, the memory will be copied to a larger memory space via `Unsafe.copyMemory`. When disk backed bytes are resized, disk space will be allocated by resizing the underlying file.

## Buffer Pools

All buffers can optionally be pooled and reference counted. Pooled buffers can be allocated via a `PooledAllocator`:

```java
BufferAllocator allocator = new PooledHeapAllocator();

Buffer buffer = allocator.allocate(1024);
```

Catalyst tracks buffer references by implementing the `ReferenceCounted` interface. When pooled buffers are allocated, their `ReferenceCounted.references` count will be `1`. To release the buffer back to the pool, the reference count must be decremented back to `0`:

```java
// Release the reference to the buffer
buffer.release();
```

Alternatively, [`Buffer`][Buffer] extends `AutoCloseable`, and buffers can be released back to the pool regardless of their reference count by calling `Buffer.close`:

```java
// Release the buffer back to the pool
buffer.close();
```

{% include common-links.html %}