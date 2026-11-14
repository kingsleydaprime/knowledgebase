# Networking: From the Wire to the Web

## What networking is

**Networking is how computers send information to each other.**

When you open a website, send a WhatsApp message or stream a video, your device breaks the information into small pieces called **packets** and sends them out. They hop from machine to machine, through your Wi-Fi router, your internet provider and many other computers around the world, until they reach the right place. There they're put back together in the right order, even if some got lost or arrived jumbled on the way.

It works a bit like the post. Every packet carries an address (an **IP address**), and machines along the way read the address and pass it on, one step closer each time. On top of that, there are agreed rules called **protocols** that make sure messages arrive complete, find the right app on the right computer, and stay private.

## What you'll be able to do

By the end you will be able to:
- explain step by step what happens when you type a web address and press Enter;
- read and work out IP addresses, and understand how your home network shares one public address;
- explain how packets find their way across the internet;
- explain how a connection makes sure nothing is lost, and why networks slow down when they're busy;
- understand how website names become addresses (DNS), and how HTTPS keeps traffic private;
- find out why a connection is slow or broken, using real command-line tools.

## Where to start

Read the parts in order. Part B is the heart of the course.

Two other courses cover networking from different angles. This one explains **why** things work the way they do. [[devops/08-networking-and-web/index|DevOps: Networking and Web]] covers **setting things up**, such as configuring a domain name or a web server. [[cybersecurity/03-network-security/index|Network Security]] covers **attacks and defences**. Reading this one first makes the other two much easier.

### Part A: How a message reaches the next machine

1. [[networking/01-what-a-network-is|What a Network Actually Is]]: packets, how networking is organised in layers, and what happens when you load a webpage.
2. [[networking/02-the-link-layer|The Link Layer]]: how devices on the same network (like your home Wi-Fi) talk to each other directly.
3. [[networking/03-ip-addressing-and-subnetting|IP Addressing & Subnetting]]: how addresses work, splitting a network into smaller ones, and how many devices share one public address.
4. [[networking/04-routing|Routing]]: how packets find their way across the internet, one hop at a time.

### Part B: Getting messages there reliably (the heart of the course)

5. [[networking/05-udp-and-ports|UDP & Ports]]: the simplest way to send data, with no guarantees, and how ports make sure data reaches the right app.
6. [[networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]]: how two computers open a reliable connection with a "handshake", and how they close it.
7. [[networking/07-tcp-reliability-and-flow-control|TCP Reliability & Flow Control]]: how TCP notices lost packets and resends them, and how it avoids sending faster than the other side can take.
8. [[networking/08-congestion-control|Congestion Control]]: how computers slow down when the network gets busy, so the whole internet doesn't jam.
9. [[networking/09-sockets-and-the-network-api|Sockets & the Network API]]: how a program actually opens a connection and sends data, and how servers handle thousands of connections at once.

### Part C: Names, security and the web

10. [[networking/10-dns-in-depth/index|DNS in Depth]]: how a name like `google.com` gets turned into an address, and why DNS problems cause so many outages.
11. [[networking/11-http-evolution/index|HTTP and Its Evolution]]: the language browsers and servers speak, and how it has changed to make websites faster.
12. [[networking/12-tls-and-transport-security/index|TLS & Transport Security]]: how HTTPS keeps your traffic private and proves you're talking to the real website, and what the padlock does and doesn't mean.
13. [[networking/13-quic-and-modern-transport|QUIC & Modern Transport]]: the newest way of sending web traffic, built to be faster, especially on phones that switch networks.

### Part D: Speed and fixing problems

14. [[networking/14-nat-firewalls-and-middleboxes|NAT, Firewalls & Middleboxes]]: the boxes that sit in the middle of connections, such as home routers, firewalls and proxies, and the problems they cause.
15. [[networking/15-network-performance|Network Performance]]: what makes a connection fast or slow, and why distance matters more than speed for many apps.
16. [[networking/16-debugging-networks|Debugging Networks]]: finding what's broken, layer by layer, with tools like `dig`, `curl` and `tcpdump`.

## Practice

Networking is invisible until you watch it happen, so do these alongside the reading:

1. **After Part A:** run `ip route`, `ip neigh` and `mtr` on your own machine and match the output to the notes.
2. **After Part B:** run `tcpdump` while fetching a page with `curl`, and find the TCP handshake in the output yourself. This is the most valuable exercise in the course.
3. **Build something:** a small server that echoes back what it receives, then your own simple web server. → [[build-your-own-shit/01-http-server|Build your own HTTP server]]
4. **Break things on purpose:** add delay and lost packets to your own machine and watch downloads slow down.

```sh
# add 100 ms delay and 1% packet loss to your machine's own loopback network, then measure
sudo tc qdisc add dev lo root netem delay 100ms loss 1%
sudo tc qdisc del dev lo root          # undo
```

For a big project: [[build-your-own-shit/19-your-own-tcp-ip-stack|Build your own TCP/IP stack]] turns Parts A and B into running code you wrote yourself.

## Key ideas to remember

1. **Data travels in small packets,** each finding its own way, and they're put back together at the end. → [[networking/01-what-a-network-is|01]]
2. **Networking is built in layers.** Each layer does one job and relies on the one below, like a letter inside an envelope inside a mail bag. → [[networking/01-what-a-network-is|01]]
3. **TCP gives you a stream of bytes, not separate messages.** If you send two messages, they can arrive glued together or split up, and your program has to handle that. → [[networking/07-tcp-reliability-and-flow-control|07]]
4. **Most slowness comes from round trips, not bandwidth.** Every back-and-forth costs time, however fast the connection. → [[networking/15-network-performance|15]]
5. **When the internet "is down", check DNS first.** It's behind a surprising number of outages. → [[networking/10-dns-in-depth/index|10]]
6. **The padlock means the connection is private, not that the website is honest.** → [[networking/12-tls-and-transport-security/index|12]]

## Related

- [[networking/interview/index|Networking interview prep]]: questions with model answers, drawn from these notes.
- [[os/index|Operating Systems]]: the layer directly underneath. A network connection is a file to the operating system.
- [[architecture/04-distributed-systems/index|Distributed Systems]]: what happens when many machines have to work together over unreliable networks.
- [[cybersecurity/03-network-security/index|Network Security]]: attacking and defending everything here.

---

## About this course

- **Size:** 16 notes. Each opens with a simple explanation before going into detail.
- **Sources:** the standard textbooks (Kurose and Ross, *Computer Networking: A Top-Down Approach*; Stevens, *TCP/IP Illustrated*; Grigorik, *High Performance Browser Networking*) and the official protocol documents (RFCs) where precision matters.
