---
layout: content
project: catalyst
menu: user-manual
title: I/O & Serialization
pitch: Custom binary serialization, built for the JVM
first-section: serialization
---

Catalyst provides a custom I/O and serialization framework that it uses for all disk and network I/O. The I/O framework is designed to provide an abstract API for reading and writing bytes on disk, in memory, and over a network in a way that is easily interchangeable and reduces garbage collection and unnecessary memory copies.

## Serialization

Catalyst provides an efficient custom serialization framework that's designed to operate on both disk and memory via a common [Buffer](#buffers) abstraction.

### Serializer

Catalyst's serializer can be used by simply instantiating a [Serializer][Serializer] instance:

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

The `Serializer` class supports serialization and deserialization of `CatalystSerializable` types, types that have an associated `Serializer`, and native Java `Serializable` and `Externalizable` types, with `Serializable` being the most inefficient method of serialization.

Additionally, Catalyst support copying objects by serializing and deserializing them. To copy an object, simply use the `Serializer.copy` method:

```java
Person copy = serializer.copy(person);
```

All `Serializer` instance constructed by Catalyst use `ServiceLoaderTypeResolver`. Catalyst registers internal `CatalystSerializable` types via `META-INF/services/io.atomix.catalyst.serializer.CatalystSerializable`. To register additional serializable types, create an additional `META-INF/services/io.atomix.catalyst.serializer.CatalystSerializable` file and list serializable types in that file.

`META-INF/services/io.atomix.catalyst.serializer.CatalystSerializable`

```
com.mycompany.SerializableType1
com.mycompany.SerializableType2
```

Users should annotate all `CatalystSerializable` types with the `@SerializeWith` annotation and provide a serialization ID for efficient serialization. Alley cat reserves serializable type IDs `128` through `255` and Catalyst reserves `256` through `512`.

### Pooled object deserialization

Catalyst's serialization framework integrates with [object pools](#buffer-pools) to support allocating pooled objects during deserialization. When a `Serializer` instance is used to deserialize a type that implements `ReferenceCounted`, Catalyst will automatically create new objects from a `ReferencePool`:

```java
Serializer serializer = new Serializer();

// Person implements ReferenceCounted<Person>
Person person = serializer.readObject(buffer);

// ...do some stuff with Person...

// Release the Person reference back to Catalyst's internal Person pool
person.close();
```

### Serializable type resolution

Serializable types are resolved by a user-provided [SerializableTypeResolver][SerializableTypeResolver]. By default, Catalyst uses a combination of the 

Catalyst always registers serializable types provided by [PrimitiveTypeResolver][PrimitiveTypeResolver] and [JdkTypeResolver][JdkTypeResolver], including the following types:

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

Additionally, Catalyst's Raft implementation uses [ServiceLoaderTypeResolver][ServiceLoaderTypeResolver] to register types registered via Java's `ServiceLoader`

Users can resolve custom serializers at runtime via `Serializer.resolve` methods or register specific types via `Serializer.register` methods.

To register a serializable type with an `Serializer` instance, the type must generally meet one of the following conditions:

* Implement `CatalystSerializable`
* Implement `Externalizable`
* Provide a `Serializer` class
* Provide a `SerializerFactory`

```java
Serializer serializer = new Serializer();
serializer.register(Foo.class, FooSerializer.class);
serializer.register(Bar.class);
```

Additionally, Catalyst supports serialization of `Serializable` and `Externalizable` types without registration, but this mode of serialization is inefficient as it requires that Catalyst serialize the full class name as well.

### Registration identifiers

Types explicitly registered with a `Serializer` instance can provide a registration ID in lieu of serializing class names. If given a serialization ID, Catalyst will write the serializable type ID to the serialized `Buffer` instance of the class name and use the ID to locate the serializable type upon deserializing the object. This means *it is critical that all processes that register a serializable type use consistent identifiers.*

To register a serializable type ID, pass the `id` to the `register` method:

```java
Serializer serializer = new Serializer();
serializer.register(Foo.class, FooSerializer.class, 1);
serializer.register(Bar.class, 2);
```

Valid serialization IDs are between `0` and `65535`. However, Catalyst reserves IDs `128` through `255` for internal use. Attempts to register serializable types within the reserved range will result in an `IllegalArgumentException`.

### CatalystSerializable

Instead of writing a custom `TypeSerializer`, serializable types can also implement the `CatalystSerializable` interface. The `CatalystSerializable` interface is synonymous with Java's native `Serializable` interface. As with the `Serializer` interface, `CatalystSerializable` exposes two methods which receive both a [Buffer](#buffers) and a `Serializer`:

```java
public class Foo implements CatalystSerializable {
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
public class Foo implements CatalystSerializable {
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

### TypeSerializer

At the core of the serialization framework is the [TypeSerializer][TypeSerializer]. The `TypeSerializer` is a simple interface that exposes two methods for serializing and deserializing objects of a specific type respectively. That is, serializers are responsible for serializing objects of other types, and not themselves. Catalyst provides this separate serialization interface in order to allow users to create custom serializers for types that couldn't otherwise be serialized by Catalyst.

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

Catalyst comes with a number of native `TypeSerializer` implementations, for instance `ListSerializer`:

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

{% include common-links.html %}