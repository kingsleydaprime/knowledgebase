# OS — Interview Prep

From [[foundations/os/fundamentals|foundations/os]]. The layer directly beneath [[foundations/networking/README|networking]], [[languages/01-java/02-jvm-and-concurrency/README|the JVM]], and [[devops/01-linux/README|Linux]] — thin as a folder, but the questions here underpin all three.

## Files
1. [[foundations/os/interview/01-processes-memory-and-io|Processes, Memory & I/O]] — processes vs threads, context switching, virtual memory, page cache, syscalls, scheduling, deadlock

## Why this comes up

OS questions appear in systems, low-latency, and infrastructure interviews as a **depth probe**. Nobody asks you to implement a scheduler; they ask what a context switch costs, or what happens on a page fault, to find out whether your mental model bottoms out at the language runtime or goes below it.

**That's exactly the Rank II→III transition** in [[PRIMETECHIE|the Primetechie path]] — knowing the layer below the one you work at.

## Related
- [[foundations/os/fundamentals|OS fundamentals]]
- [[foundations/networking/09-sockets-and-the-network-api|Sockets]] — file descriptors, epoll, io_uring
- [[languages/01-java/interview/02-jvm-and-concurrency|Java: JVM & concurrency]] — the same concepts one layer up
- [[devops/interview/01-linux-containers-and-operations|DevOps: Linux & containers]] — namespaces and cgroups are OS features
