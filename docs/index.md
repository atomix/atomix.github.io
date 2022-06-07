---
hide:
  - navigation
  - toc
---

# Atomix

Atomix Cloud

!!! Example

    === "Counter"

        === ":fontawesome-brands-golang:"
        
            ```go
            // Get a string:string map
            c, err := atomix.GetCounter(context.Background(), "my-counter")
            if err != nil {
                ...
            }
        
            // Increment the counter
            count, err = c.Increment(context.Background())
            if err != nil {
                ...
            }
        
            // Get the counter value
            value, err = c.Get(context.Background())
            if err != nil {
                ...
            }
            ```
        
        === ":fontawesome-brands-java:"
        
            ```java
            // Create an Atomix instance
            Atomix atomix = new Atomix();
    
            // Get the "foo" counter
            AtomicCounter counter = atomix.getCounter("foo");
    
            // Increment the counter
            int count = counter.incrementAndGet();
    
            // Get the counter value
            count = counter.get();
            ```

    === "Map"

        === ":fontawesome-brands-golang:"
        
            ```go
            // Get a string:string map
            m, err := atomix.GetMap[string, string](context.Background(), "my-map")
            if err != nil {
                ...
            }
        
            // Write to the map
            _, err = m.Put(context.Background(), "foo", "bar")
            if err != nil {
                ...
            }
        
            // Read from the map
            entry, err := m.Get(context.Background(), "foo")
            if err != nil {
                ...
            }
            ```
        
        === ":fontawesome-brands-java:"
        
            ```java
            // Create an Atomix instance
            Atomix atomix = new Atomix();
    
            // Get the "foo" map
            Map<String, String> map = atomix.getMap("foo");
    
            // Write to the map
            map.put("foo", "bar");
    
            // Read from the map
            Entry<string, string> entry = map.get("foo");
            ```
